import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/get_details"  

st.title("Corebot Classifier (Black Metal Version)")
st.write("Descubra detalhes sobre músicas de black metal com base nas letras!")

lyrics_input = st.text_area(
    "Insira a letra da música aqui:",
    placeholder="Digite ou cole a letra da música...",
    height=300
)

if st.button("Obter Detalhes"):
    if lyrics_input.strip():
        with st.spinner("Consultando o modelo..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"text": lyrics_input},
                    timeout=30 
                )
                if response.status_code == 200:
                    details = response.json()
                    st.subheader("Detalhes da Música:")
                    st.write(f"**Nome da Música:** {details.get('song_name', 'Desconhecido')}")
                    st.write(f"**Álbum:** {details.get('album', 'Desconhecido')}")
                    st.write(f"**Ano de Lançamento:** {details.get('release_year', 'Desconhecido')}")
                    st.write(f"**Artista:** {details.get('artist', 'Desconhecido')}")
                    st.write(f"**Gravadora:** {details.get('label', 'Desconhecida')}")
                else:
                    st.error(f"Erro: {response.status_code} - {response.json().get('error', 'Erro desconhecido.')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao conectar-se à API: {str(e)}")
    else:
        st.warning("Por favor, insira a letra da música antes de enviar.")
