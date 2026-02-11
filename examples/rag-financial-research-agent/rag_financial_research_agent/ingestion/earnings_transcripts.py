"""Earnings call transcript ingestion."""

import logging
from pathlib import Path
from typing import Any

from ..utils.text_splitter import split_document
from ..vector_store import VectorStore

logger = logging.getLogger(__name__)


class EarningsTranscriptIngestor:
    """Ingest earnings call transcripts into the vector store."""

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def ingest_transcript(
        self,
        text: str,
        ticker: str,
        quarter: str,
        year: int,
        additional_metadata: dict[str, Any] | None = None,
    ) -> int:
        """Ingest an earnings transcript.

        Args:
            text: The transcript text
            ticker: Company ticker symbol
            quarter: Quarter (Q1, Q2, Q3, Q4)
            year: Fiscal year
            additional_metadata: Optional extra metadata

        Returns:
            Number of chunks ingested
        """
        source_name = f"{ticker}_{quarter}_{year}_earnings"

        metadata = {
            "source": source_name,
            "document_type": "earnings_transcript",
            "ticker": ticker.upper(),
            "quarter": quarter,
            "year": year,
            **(additional_metadata or {}),
        }

        chunks, metadatas = split_document(text, metadata)

        ids = [f"{source_name}_chunk_{i}" for i in range(len(chunks))]

        self.vector_store.add_documents(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("Ingested %d chunks from %s", len(chunks), source_name)
        return len(chunks)

    def ingest_from_file(self, file_path: Path) -> int:
        """Ingest transcript from a file.

        Expected filename format: TICKER_Q#_YYYY.txt
        Example: AAPL_Q4_2024.txt
        """
        stem = file_path.stem
        parts = stem.split("_")

        if len(parts) < 3:
            raise ValueError(
                f"Invalid filename format: {file_path.name}. "
                "Expected: TICKER_Q#_YYYY.txt"
            )

        ticker = parts[0]
        quarter = parts[1]
        year = int(parts[2])

        text = file_path.read_text(encoding="utf-8")

        return self.ingest_transcript(text, ticker, quarter, year)
