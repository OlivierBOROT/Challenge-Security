import streamlit as st

from src.data.mariadb_client import MariaDBClient

st.set_page_config(page_title="Exploration DB", layout="wide")
st.header("🗄️ Parcours des données via renderDataTable")

db = MariaDBClient()

# Récupération et affichage simple
try:
    df = db.fetch_logs(table_name="FW", limit=5000)
    st.dataframe(df, width="stretch")  # Équivalent renderDataTable
except Exception as e:
    st.error(f"Erreur : {e}")
