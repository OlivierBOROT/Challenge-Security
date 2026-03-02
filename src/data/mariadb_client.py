import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class MariaDBClient:
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT", 3306)
        self.database = os.getenv("DB_NAME")
        
        # Utilisation de pymysql pour la compatibilité MariaDB/MySQL [cite: 9]
        connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(connection_string, pool_pre_ping=True)

    def list_tables(self):
        """Utile pour débugger et voir quelles tables existent réellement."""
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def fetch_logs(self, table_name: str = "Logs_fw", limit: int = 5000) -> pd.DataFrame:
        """Récupère les logs en respectant les colonnes du projet[cite: 80, 87]."""
        # On vérifie d'abord si la table existe pour éviter l'erreur 1146
        existing_tables = self.list_tables()
        if table_name not in existing_tables:
            raise ValueError(f"La table '{table_name}' est introuvable dans '{self.database}'. Tables dispos : {existing_tables}")
            
        query = text(f"SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT :limit")
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": limit})