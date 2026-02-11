"""Generic PDF document ingestion."""

import logging
from pathlib import Path
from typing import Any

from ..utils.text_splitter import split_document
from ..vector_store import VectorStore

logger = logging.getLogger(__name__)


class PDFDocumentIngestor:
    """Ingest PDF documents into the vector store."""

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def ingest_pdf(
        self,
        file_path: Path,
        document_type: str = "research_report",
        ticker: str | None = None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> int:
        """Ingest a PDF document into the vector store.

        Requires the `pdfplumber` package for PDF text extraction.

        Args:
            file_path: Path to the PDF file
            document_type: Type classification for the document
            ticker: Optional ticker symbol associated with the document
            additional_metadata: Optional extra metadata

        Returns:
            Number of chunks ingested
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required for PDF ingestion. "
                "Install it with: pip install pdfplumber"
            )

        text_parts: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        text = "\n\n".join(text_parts)

        if not text.strip():
            logger.warning("No text extracted from %s", file_path)
            return 0

        source_name = file_path.stem

        metadata: dict[str, Any] = {
            "source": source_name,
            "document_type": document_type,
            "file_path": str(file_path),
            **(additional_metadata or {}),
        }
        if ticker:
            metadata["ticker"] = ticker.upper()

        chunks, metadatas = split_document(text, metadata)

        ids = [f"{source_name}_chunk_{i}" for i in range(len(chunks))]

        self.vector_store.add_documents(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("Ingested %d chunks from %s", len(chunks), file_path)
        return len(chunks)
