import streamlit as st
from src.data.mariadb_client import MariaDBClient

def main():
    st.set_page_config(page_title="Projet SISE-OPSIE 2026", layout="wide")
    
    st.title("🛡️ État Global du Système d'Information")
    st.info("Utilisez la barre latérale pour naviguer entre les modules d'analyse.")

    db = MariaDBClient()
    
    try:
        df = db.fetch_logs(table_name="FW", limit=1)
        if not df.empty:
            st.success("✅ Connexion à la base MariaDB Cloud opérationnelle.")
            
            # Affichage de métriques très haut niveau
            col1, col2 = st.columns(2)
            col1.metric("Statut Infrastructure", "Connecté")
            col2.metric("Dernière synchro logs", str(df['datetime'].iloc[0]))
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    main()