"""Tests for the vector store module."""

import os

import pytest

os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "./test_chroma_db_vs"
os.environ["CHROMA_COLLECTION_NAME"] = "test_vs_collection"


from rag_financial_research_agent.vector_store import VectorStore


@pytest.fixture
def clean_vector_store(tmp_path):
    """Create a clean vector store for testing."""
    os.environ["CHROMA_PERSIST_DIRECTORY"] = str(tmp_path / "chroma_test")
    os.environ["CHROMA_COLLECTION_NAME"] = "test_collection_vs"

    # Reload settings
    from rag_financial_research_agent.config import Settings

    test_settings = Settings()

    import rag_financial_research_agent.config as config_module

    original_settings = config_module.settings
    config_module.settings = test_settings

    vs = VectorStore()
    yield vs

    config_module.settings = original_settings


def test_get_collection_stats(clean_vector_store: VectorStore) -> None:
    """Test getting collection statistics."""
    stats = clean_vector_store.get_collection_stats()
    assert "name" in stats
    assert "count" in stats
    assert stats["count"] == 0
