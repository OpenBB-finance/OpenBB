"""Shared fixtures for the openbb_government_us test suite."""

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip auth headers and api_key from recorded cassettes."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.fixture(autouse=True)
def _clear_state_caches():
    """Reset module-level caches so state never leaks between tests."""
    from openbb_government_us.congress.utils import bulk, committees
    from openbb_government_us.congress.utils.helpers import BillsState

    def _reset():
        BillsState().bulk.clear()
        committees._GOVTRACK_DATA_CACHE.clear()
        bulk._LOAD_LOCKS.clear()

    _reset()
    yield
    _reset()


@pytest.fixture(autouse=True)
def _isolate_ers_cache(tmp_path, monkeypatch):
    """Point the ERS disk cache at a per-test directory so HTTP always fires."""
    monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path / "ers_cache"))
