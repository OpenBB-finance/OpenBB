"""Tests for the retriever module."""

from rag_financial_research_agent.retriever import (
    FinancialRetriever,
    RetrievedDocument,
)


def test_retrieved_document_properties() -> None:
    """Test RetrievedDocument dataclass properties."""
    doc = RetrievedDocument(
        content="Test content",
        metadata={
            "source": "AAPL_10-K_2024",
            "document_type": "sec_filing",
            "ticker": "AAPL",
        },
        score=0.95,
    )

    assert doc.source == "AAPL_10-K_2024"
    assert doc.document_type == "sec_filing"
    assert doc.ticker == "AAPL"


def test_retrieved_document_defaults() -> None:
    """Test RetrievedDocument with missing metadata fields."""
    doc = RetrievedDocument(
        content="Test content",
        metadata={},
        score=0.5,
    )

    assert doc.source == "unknown"
    assert doc.document_type == "unknown"
    assert doc.ticker is None


def test_format_context_empty() -> None:
    """Test formatting empty context returns empty string."""
    retriever = FinancialRetriever.__new__(FinancialRetriever)
    result = retriever.format_context([])
    assert result == ""


def test_format_context_with_documents() -> None:
    """Test formatting context with documents."""
    retriever = FinancialRetriever.__new__(FinancialRetriever)

    docs = [
        RetrievedDocument(
            content="Risk factor 1: supply chain disruption",
            metadata={
                "source": "AAPL_10-K",
                "document_type": "sec_filing",
                "ticker": "AAPL",
            },
            score=0.9,
        ),
        RetrievedDocument(
            content="Revenue grew 15% year over year",
            metadata={
                "source": "MSFT_Q4_2024_earnings",
                "document_type": "earnings_transcript",
                "ticker": "MSFT",
            },
            score=0.85,
        ),
    ]

    result = retriever.format_context(docs)

    assert "AAPL" in result
    assert "MSFT" in result
    assert "Risk factor 1" in result
    assert "Revenue grew" in result
    assert "0.90" in result
    assert "0.85" in result
    assert "Retrieved Financial Documents" in result


def test_format_context_without_ticker() -> None:
    """Test formatting context for documents without a ticker."""
    retriever = FinancialRetriever.__new__(FinancialRetriever)

    docs = [
        RetrievedDocument(
            content="General market analysis",
            metadata={
                "source": "market_report_2024",
                "document_type": "research_report",
            },
            score=0.8,
        ),
    ]

    result = retriever.format_context(docs)

    assert "market_report_2024" in result
    assert "General market analysis" in result
