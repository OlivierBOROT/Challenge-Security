import streamlit as st
import pandas as pd
from src.data.mariadb_client import MariaDBClient

def main():
    st.title("🛡️ Test de Connexion : Table FW")
    db = MariaDBClient()

    try:
        # Récupération brute des données de la table FW
        df = db.fetch_logs(table_name="FW", limit=50)
        
        if df.empty:
            st.warning("⚠️ Connexion réussie, mais la table 'FW' est vide.")
            return

        st.success(f"✅ Connexion établie ! {len(df)} lignes récupérées.")

        # --- APERÇU DES DONNÉES ---
        st.subheader("Aperçu des 50 dernières lignes")
        # Utilisation de st.dataframe pour le parcours des données (Partie 1.5.2) [cite: 169]
        st.dataframe(df, use_container_width=True)

        # --- DIAGNOSTIC DES DATES ---
        df['datetime'] = pd.to_datetime(df['datetime'])
        min_date = df['datetime'].min()
        max_date = df['datetime'].max()
        
        st.info(f"Plage temporelle des données actuelles : du {min_date} au {max_date}")
        
        # Vérification de la période projet (Nov 2025 - Fév 2026) 
        if min_date < pd.Timestamp('2025-11-01') or max_date > pd.Timestamp('2026-02-28'):
            st.warning("Note : Ces données sont hors de la période d'analyse du projet.")

    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture : {e}")

if __name__ == "__main__":
    main()