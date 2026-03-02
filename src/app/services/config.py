# -*- coding: utf-8 -*-
"""Configuration du service LLM Mistral.

La clé API est lue (par ordre de priorité) depuis :
  1. Le fichier .env à la racine du dossier streamlit  (MISTRAL_API_KEY=sk-...)
  2. Les variables d'environnement du shell
"""

import os
from pathlib import Path

from dotenv import load_dotenv  # python-dotenv

_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# Nom du modèle Mistral à utiliser
DEFAULT_MODEL = "mistral-medium-latest"


def get_api_key() -> str:
    """Retourne la clé API Mistral (chargée depuis .env ou variable d'environnement)."""
    return os.environ.get("MISTRAL_API_KEY", "")
