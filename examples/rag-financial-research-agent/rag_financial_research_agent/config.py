"""Configuration settings for the RAG Financial Research Agent."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = ""
    openai_base_url: str | None = None  # For Ollama: http://localhost:11434/v1

    # Vector Store
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "financial_documents"

    # Retrieval
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.7

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Server
    host: str = "0.0.0.0"
    port: int = 7777

    # Model
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
