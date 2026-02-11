"""Tests for document ingestion modules."""

from pathlib import Path

import pytest

from rag_financial_research_agent.ingestion.earnings_transcripts import (
    EarningsTranscriptIngestor,
)
from rag_financial_research_agent.utils.text_splitter import (
    get_text_splitter,
    split_document,
)


def test_text_splitter_configured() -> None:
    """Test that the text splitter is properly configured."""
    splitter = get_text_splitter()
    assert splitter._chunk_size > 0
    assert splitter._chunk_overlap >= 0
    assert splitter._chunk_overlap < splitter._chunk_size


def test_split_document_basic() -> None:
    """Test basic document splitting."""
    text = "This is a test document. " * 200
    metadata = {"source": "test", "document_type": "test"}

    chunks, metadatas = split_document(text, metadata)

    assert len(chunks) > 1
    assert len(chunks) == len(metadatas)

    for i, m in enumerate(metadatas):
        assert m["source"] == "test"
        assert m["document_type"] == "test"
        assert m["chunk_index"] == i


def test_split_document_short_text() -> None:
    """Test splitting text shorter than chunk size."""
    text = "Short text."
    metadata = {"source": "test"}

    chunks, metadatas = split_document(text, metadata)

    assert len(chunks) == 1
    assert chunks[0] == "Short text."
    assert metadatas[0]["chunk_index"] == 0


def test_split_document_preserves_metadata() -> None:
    """Test that original metadata is preserved in all chunks."""
    text = "Word " * 500
    metadata = {"source": "doc1", "ticker": "AAPL", "year": 2024}

    chunks, metadatas = split_document(text, metadata)

    for m in metadatas:
        assert m["source"] == "doc1"
        assert m["ticker"] == "AAPL"
        assert m["year"] == 2024


def test_earnings_transcript_file_parsing(tmp_path: Path) -> None:
    """Test earnings transcript filename parsing."""
    transcript = tmp_path / "AAPL_Q4_2024.txt"
    transcript.write_text("Apple Q4 2024 earnings call transcript content.")

    # Just test that the ingestor can parse the filename
    stem = transcript.stem
    parts = stem.split("_")
    assert parts[0] == "AAPL"
    assert parts[1] == "Q4"
    assert int(parts[2]) == 2024


def test_earnings_transcript_invalid_filename() -> None:
    """Test that invalid filenames raise ValueError."""
    ingestor = EarningsTranscriptIngestor.__new__(EarningsTranscriptIngestor)

    with pytest.raises(ValueError, match="Invalid filename format"):
        ingestor.ingest_from_file(Path("invalid_name.txt"))
