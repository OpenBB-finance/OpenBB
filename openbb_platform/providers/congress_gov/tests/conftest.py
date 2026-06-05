"""Shared fixtures for the openbb_congress_gov test suite."""

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
    from openbb_congress_gov.utils import bulk, committees
    from openbb_congress_gov.utils.helpers import BillsState

    def _reset():
        BillsState().bulk.clear()
        committees._GOVTRACK_DATA_CACHE.clear()
        bulk._LOAD_LOCKS.clear()

    _reset()
    yield
    _reset()
