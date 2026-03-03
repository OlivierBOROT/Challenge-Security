FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Installation des dépendances via le lockfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copie du code source
COPY src ./src

# Port par défaut pour Streamlit
EXPOSE 7860

# Lancement de l'application
CMD ["uv", "run", "streamlit", "run", "src/app/Dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]