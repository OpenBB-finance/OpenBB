"""ChromaDB vector store operations."""

import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma

from .config import settings
from .embeddings import get_embeddings

logger = logging.getLogger(__name__)


class VectorStore:
    """Wrapper for ChromaDB vector store operations."""

    def __init__(self) -> None:
        self.embeddings = get_embeddings()

        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        self.vector_store = Chroma(
            client=self.client,
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings,
        )

    def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> None:
        """Add documents to the vector store."""
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info("Added %d documents to vector store", len(texts))

    def similarity_search(
        self,
        query: str,
        k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[str, dict[str, Any], float]]:
        """Search for similar documents.

        Returns list of (content, metadata, score) tuples.
        """
        k = k or settings.rag_top_k

        results = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            filter=filter,
        )

        # Note: With some embedding models (e.g., Ollama), scores may be raw distances
        # rather than 0-1 similarity scores. Skip threshold filtering in that case.
        return [
            (doc.page_content, doc.metadata, score)
            for doc, score in results
        ]

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(settings.chroma_collection_name)
        logger.info("Deleted collection: %s", settings.chroma_collection_name)

    def get_collection_stats(self) -> dict[str, Any]:
        """Get collection statistics."""
        collection = self.client.get_collection(settings.chroma_collection_name)
        return {
            "name": collection.name,
            "count": collection.count(),
        }
