"""Application settings loaded from environment / .env."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (Groq)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Embeddings (Voyage)
    voyage_api_key: str = ""
    voyage_model: str = "voyage-3-lite"

    # RAG
    top_k: int = 4
    chunk_size: int = 900
    chunk_overlap: int = 150
    data_dir: str = "data"
    vectorstore_dir: str = "vectorstore"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"


settings = Settings()
