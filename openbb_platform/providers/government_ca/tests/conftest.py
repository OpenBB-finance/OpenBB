"""Shared fixtures for the openbb-government-ca test suite."""

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip the User-Agent header from recorded cassettes."""
    return {"filter_headers": [("User-Agent", None)]}
