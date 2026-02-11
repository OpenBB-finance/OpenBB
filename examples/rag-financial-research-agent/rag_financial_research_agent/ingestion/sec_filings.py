"""SEC EDGAR filings ingestion."""

import logging
from pathlib import Path

from sec_edgar_downloader import Downloader

from ..utils.text_splitter import split_document
from ..vector_store import VectorStore

logger = logging.getLogger(__name__)


class SECFilingsIngestor:
    """Ingest SEC filings into the vector store."""

    def __init__(
        self,
        vector_store: VectorStore,
        download_dir: str = "./sec_filings",
    ) -> None:
        self.vector_store = vector_store
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = Downloader(
            company_name="OpenBB Research Agent",
            email_address="research@example.com",
            download_folder=str(self.download_dir),
        )

    def download_filing(
        self,
        ticker: str,
        filing_type: str = "10-K",
        limit: int = 1,
    ) -> list[Path]:
        """Download SEC filings for a ticker."""
        self.downloader.get(filing_type, ticker, limit=limit)

        ticker_dir = (
            self.download_dir / "sec-edgar-filings" / ticker / filing_type
        )
        if not ticker_dir.exists():
            return []

        return list(ticker_dir.glob("**/full-submission.txt"))

    def ingest_filing(self, file_path: Path, ticker: str) -> int:
        """Ingest a single SEC filing into the vector store.

        Returns number of chunks ingested.
        """
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        filing_type = file_path.parent.parent.name

        metadata = {
            "source": f"{ticker}_{filing_type}_{file_path.parent.name}",
            "document_type": "sec_filing",
            "ticker": ticker.upper(),
            "filing_type": filing_type,
            "file_path": str(file_path),
        }

        chunks, metadatas = split_document(text, metadata)

        ids = [
            f"{metadata['source']}_chunk_{i}" for i in range(len(chunks))
        ]

        self.vector_store.add_documents(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("Ingested %d chunks from %s", len(chunks), file_path)
        return len(chunks)

    def ingest_ticker(
        self,
        ticker: str,
        filing_types: list[str] | None = None,
        limit_per_type: int = 1,
    ) -> int:
        """Ingest all specified filings for a ticker.

        Returns total number of chunks ingested.
        """
        filing_types = filing_types or ["10-K", "10-Q", "8-K"]
        total_chunks = 0

        for filing_type in filing_types:
            files = self.download_filing(ticker, filing_type, limit_per_type)
            for file_path in files:
                total_chunks += self.ingest_filing(file_path, ticker)

        return total_chunks
