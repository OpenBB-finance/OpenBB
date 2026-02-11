"""RAG retrieval logic."""

import logging
from dataclasses import dataclass
from typing import Any

from .vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """A retrieved document with metadata."""

    content: str
    metadata: dict[str, Any]
    score: float

    @property
    def source(self) -> str:
        """Get the document source."""
        return self.metadata.get("source", "unknown")

    @property
    def document_type(self) -> str:
        """Get the document type (sec_filing, earnings_transcript, etc.)."""
        return self.metadata.get("document_type", "unknown")

    @property
    def ticker(self) -> str | None:
        """Get the ticker symbol if available."""
        return self.metadata.get("ticker")


class FinancialRetriever:
    """Retriever for financial documents."""

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        ticker: str | None = None,
        document_type: str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedDocument]:
        """Retrieve relevant documents for a query.

        Args:
            query: The search query
            ticker: Optional ticker to filter by
            document_type: Optional document type filter
                          (sec_filing, earnings_transcript, research_report)
            top_k: Number of documents to retrieve

        Returns:
            List of RetrievedDocument objects sorted by relevance
        """
        filter_dict: dict[str, Any] | None = None
        if ticker or document_type:
            filter_dict = {}
            if ticker:
                filter_dict["ticker"] = ticker.upper()
            if document_type:
                filter_dict["document_type"] = document_type

        results = self.vector_store.similarity_search(
            query=query,
            k=top_k,
            filter=filter_dict,
        )

        documents = [
            RetrievedDocument(content=content, metadata=metadata, score=score)
            for content, metadata, score in results
        ]

        logger.info(
            "Retrieved %d documents for query: %s...",
            len(documents),
            query[:50],
        )

        return documents

    def format_context(self, documents: list[RetrievedDocument]) -> str:
        """Format retrieved documents as context for the LLM."""
        if not documents:
            return ""

        context_parts = ["--- Retrieved Financial Documents ---\n"]

        for i, doc in enumerate(documents, 1):
            source_info = f"[{doc.source}]"
            if doc.ticker:
                source_info = f"[{doc.ticker} - {doc.source}]"

            context_parts.append(
                f"Document {i} {source_info} (relevance: {doc.score:.2f}):\n"
                f"{doc.content}\n"
                f"---\n"
            )

        return "\n".join(context_parts)
