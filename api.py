from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import json

class LyricsInput(BaseModel):
    text: str

app = FastAPI()

MODEL_NAME_OR_PATH = "missantroop/BlackMetal"  
MODEL_BASENAME = "unsloth.Q8_0.gguf"         

try:
    MODEL_PATH = hf_hub_download(repo_id=MODEL_NAME_OR_PATH, filename=MODEL_BASENAME)
    print(f"Modelo baixado e localizado em: {MODEL_PATH}")
except Exception as e:
    print(f"Erro ao baixar o modelo: {e}")
    raise

try:
    llama_model = Llama(
        model_path=MODEL_PATH,
        n_threads=4,         
        n_batch=512,         
        n_gpu_layers=20,      
        n_ctx=2048,           
    )
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    raise

ALPACA_PROMPT = """Você é um assistente que fornece detalhes sobre as músicas de black metal com base na letra.
### Input:
{}
### Response:
"""

def get_song_details(lyrics: str) -> dict:
    """
    Gera detalhes sobre a música com base nas letras fornecidas.
    """

    formatted_prompt = ALPACA_PROMPT.format(lyrics)

    try:

        response = llama_model(
            prompt=formatted_prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stop=["### Response:"], 
            echo=False
        )

        response_text = response['choices'][0]['text'].strip()

        response_text = response_text.replace("<|begin_of_text|>", "").replace("<|end_of_text|>", "").strip()


        if "### Response:" in response_text:
            response_text = response_text.split("### Response:")[1].strip()

        formatted_response = response_text.replace("'", '"')

        output_data = json.loads(formatted_response)
        return output_data

    except json.JSONDecodeError as e:
        return {"error": f"A resposta do modelo não é um JSON válido: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro durante a inferência do modelo: {str(e)}"}

@app.post("/get_details")
def get_details(lyrics_input: LyricsInput):
    """
    Recebe uma letra de música e retorna os detalhes da música.
    """
    try:
        song_details = get_song_details(lyrics_input.text)
        return JSONResponse(song_details)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
