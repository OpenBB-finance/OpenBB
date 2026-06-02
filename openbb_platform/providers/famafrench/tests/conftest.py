"""Shared fixtures for the openbb_famafrench test suite."""

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip the User-Agent header from recorded cassettes."""
    return {"filter_headers": [("User-Agent", None)]}


@pytest.fixture(autouse=True)
def _clear_helper_caches():
    """Clear helpers' lru_cache wrappers so cached downloads never leak between tests."""
    from openbb_famafrench.utils import helpers

    cached = (
        helpers.download_file,
        helpers.download_international_portfolios,
        helpers.get_international_portfolio,
        helpers.get_portfolio_data,
        helpers.get_breakpoint_data,
    )
    for fn in cached:
        fn.cache_clear()
    yield
    for fn in cached:
        fn.cache_clear()
