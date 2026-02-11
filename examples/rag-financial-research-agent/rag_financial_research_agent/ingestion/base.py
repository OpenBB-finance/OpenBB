"""Base ingestion interface."""

from abc import ABC, abstractmethod


class BaseIngestor(ABC):
    """Abstract base class for document ingestors."""

    @abstractmethod
    def ingest(self, *args, **kwargs) -> int:
        """Ingest documents and return the number of chunks ingested."""
