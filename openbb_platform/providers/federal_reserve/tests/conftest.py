"""Shared pytest fixtures for the openbb-federal-reserve test suite."""

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip the User-Agent header from recorded cassettes."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [],
    }


@pytest.fixture(autouse=True)
def _isolate_disk_cache(tmp_path, monkeypatch):
    """Point the unified disk cache at a per-test temp directory."""
    from openbb_federal_reserve.utils import cache

    monkeypatch.setenv(cache.CACHE_DIR_ENV_VAR, str(tmp_path / "cache"))
    cache.reset_cache()
    yield
    cache.reset_cache()


@pytest.fixture(autouse=True)
def _clear_fomc_document_cache():
    """Reset the file-backed FOMC document loader cache between tests."""
    from openbb_federal_reserve.utils.fomc_documents import (
        load_historical_fomc_documents,
    )

    load_historical_fomc_documents.cache_clear()
    yield
    load_historical_fomc_documents.cache_clear()
