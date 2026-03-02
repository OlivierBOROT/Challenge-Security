import os
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Machine Learning & Stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import pdist
from scipy.stats import kurtosis, entropy

# Database Access
from sqlalchemy import create_engine, text, inspect

# LLM Client
try:
    from mistralai import Mistral # Nouvelle syntaxe
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

load_dotenv()

# --- 1. Accès Données (Ton Script MariaDB) ---

class MariaDBClient:
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT", 3306)
        self.database = os.getenv("DB_NAME")
        # Utilisation de pymysql pour la compatibilité MariaDB/MySQL
        connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(connection_string, pool_pre_ping=True)

    def fetch_logs(self, table_name: str = "FW", limit: int = 5000) -> pd.DataFrame:
        """Récupère les logs pour l'analyse cyber."""
        query = text(f"SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT :limit")
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": limit})

# --- 2. Analyseur Topologique (CAH) ---

@dataclass
class TopologyMetrics:
    n_samples: int
    singleton_count: int
    max_fusion_dist: float
    cophenetic_corr: float
    density_heterogeneity: float
    global_kurtosis: float
    feature_entropy: Dict[str, float]

class CAHAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df_raw = df.copy()
        self.df_numeric = df.copy()
        self._prepare()

    def _prepare(self):
        # Suppression des colonnes temporelles pour le calcul mathématique
        if 'datetime' in self.df_numeric.columns:
            self.df_numeric = self.df_numeric.drop(columns=['datetime'])
        
        le = LabelEncoder()
        for col in self.df_numeric.select_dtypes(include=['object']).columns:
            self.df_numeric[col] = le.fit_transform(self.df_numeric[col].astype(str))
        
        self.X_scaled = StandardScaler().fit_transform(self.df_numeric)

    def get_metrics(self) -> TopologyMetrics:
        Z = linkage(self.X_scaled, method='ward')
        c, _ = cophenet(Z, pdist(self.X_scaled))
        max_d = Z[-1, 2]
        # Singletons : branches isolées à plus de 70% de la distance max
        clusters = fcluster(Z, t=0.7 * max_d, criterion='distance')
        singletons = (pd.Series(clusters).value_counts() == 1).sum()

        return TopologyMetrics(
            n_samples=len(self.df_numeric),
            singleton_count=int(singletons),
            max_fusion_dist=float(max_d),
            cophenetic_corr=float(c),
            density_heterogeneity=float(np.var(pdist(self.X_scaled))),
            global_kurtosis=float(kurtosis(self.X_scaled, axis=None)),
            feature_entropy={col: float(entropy(self.df_numeric[col].value_counts())) 
                             for col in self.df_numeric.columns}
        )

# --- 3. Orchestrateur LLM (Mistral Medium) ---

class SecurityOrchestrator:
    def __init__(self, model_name: str = "mistral-medium-latest"):
        self.model = model_name
        # Nouveau client simplifié
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    def run_analysis(self, analyzer: CAHAnalyzer):
        metrics = analyzer.get_metrics()
        
        prompt = f"Analyse ces métriques cyber : {asdict(metrics)}. Réponds uniquement 'IF' ou 'LOF'."
        
        # Changement ici : .chat.complete au lieu de .chat
        res = self.client.chat.complete(
            model=self.model, 
            messages=[{"role": "user", "content": prompt}]
        )
        decision = res.choices[0].message.content.strip()

        if "IF" in decision:
            algo = IsolationForest(contamination='auto').fit_predict(analyzer.X_scaled)
            label = "Isolation Forest"
        else:
            algo = LocalOutlierFactor(n_neighbors=20).fit_predict(analyzer.X_scaled)
            label = "Local Outlier Factor"

        self._report(analyzer.df_raw, algo, label)

    def _report(self, df, scores, label):
        plt.style.use('dark_background')
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))
        sns.scatterplot(x=df.index, y=df.iloc[:, 1], hue=scores, palette={1: '#3fb950', -1: '#f85149'}, ax=ax[0])
        ax[1].pie([sum(scores==1), sum(scores==-1)], labels=['Legit', 'Fraud'], autopct='%1.1f%%', colors=['#3fb950', '#f85149'])
        plt.show()
        
        # Final Expert Briefing
        fraud_sample = df[scores == -1].head(3).to_string()
        brief_prompt = f"Analyse ces fraudes détectées par {label} :\n{fraud_sample}"
        brief = self.client.chat.complete(
            model=self.model, 
            messages=[{"role": "user", "content": brief_prompt}]
        )
        print(f"\n📢 RAPPORT EXPERT ({self.model}) :\n{brief.choices[0].message.content}")
# --- 4. Main ---

if __name__ == "__main__":
    # Pipeline Complet
    db = MariaDBClient()
    logs = db.fetch_logs(limit=1000) # Récupération réelle
    
    if not logs.empty:
        cah = CAHAnalyzer(logs)
        orchestrator = SecurityOrchestrator(model_name="mistral-medium-latest")
        orchestrator.run_analysis(cah)