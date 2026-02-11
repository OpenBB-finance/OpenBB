"""Embedding generation for the RAG Financial Research Agent."""

from typing import List

import httpx
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from .config import settings


class OllamaEmbeddings(Embeddings):
    """Custom Ollama embeddings that work with the Ollama API."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = self._embed(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query."""
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        """Call Ollama embeddings API."""
        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["embedding"]


def get_embeddings() -> Embeddings:
    """Get configured embeddings instance (supports OpenAI or Ollama)."""
    # If using Ollama (base_url points to Ollama)
    if settings.openai_base_url and "11434" in settings.openai_base_url:
        # Extract base URL without /v1 suffix
        base_url = settings.openai_base_url.replace("/v1", "")
        return OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=base_url,
        )

    # Otherwise use OpenAI
    api_key = settings.openai_api_key if settings.openai_api_key else "ollama"
    kwargs: dict = {
        "model": settings.embedding_model,
        "api_key": SecretStr(api_key),
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAIEmbeddings(**kwargs)
