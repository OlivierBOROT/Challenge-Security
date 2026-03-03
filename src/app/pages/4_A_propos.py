import streamlit as st
from src.app.theme import inject_theme                          

st.set_page_config(page_title="A propos", layout="wide")
inject_theme()

st.markdown(
    '<meta http-equiv="refresh" content="0; url=https://github.com/OlivierBOROT/Challenge-Security">',
    unsafe_allow_html=True,
)
st.markdown(
    "Redirection vers [GitHub](https://github.com/OlivierBOROT/Challenge-Security)…"
)
