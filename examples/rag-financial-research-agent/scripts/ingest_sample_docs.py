#!/usr/bin/env python3
"""Ingest sample documents for testing."""

import logging
from pathlib import Path

from rag_financial_research_agent.ingestion.earnings_transcripts import (
    EarningsTranscriptIngestor,
)
from rag_financial_research_agent.ingestion.sec_filings import SECFilingsIngestor
from rag_financial_research_agent.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Ingest sample documents."""
    vs = VectorStore()
    sec_ingestor = SECFilingsIngestor(vs)
    earnings_ingestor = EarningsTranscriptIngestor(vs)

    # Ingest SEC filings for sample tickers
    sample_tickers = ["AAPL", "MSFT", "GOOGL"]

    for ticker in sample_tickers:
        logger.info("Ingesting SEC filings for %s...", ticker)
        try:
            chunks = sec_ingestor.ingest_ticker(
                ticker=ticker,
                filing_types=["10-K"],
                limit_per_type=1,
            )
            logger.info("Ingested %d chunks for %s", chunks, ticker)
        except Exception:
            logger.exception("Failed to ingest %s", ticker)

    # Ingest any earnings transcripts in data directory
    data_dir = Path("./data")
    if data_dir.exists():
        for transcript_file in data_dir.glob("*_Q*_*.txt"):
            logger.info("Ingesting transcript: %s", transcript_file.name)
            try:
                chunks = earnings_ingestor.ingest_from_file(transcript_file)
                logger.info("Ingested %d chunks", chunks)
            except Exception:
                logger.exception("Failed to ingest %s", transcript_file)

    logger.info("Ingestion complete!")


if __name__ == "__main__":
    main()
