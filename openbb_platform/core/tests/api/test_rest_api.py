"""Test rest_api.py."""

import pytest
from openbb_core.api.rest_api import app


@pytest.mark.skip(
    "This test forces a side effect that makes test_integration_tests_ to fail in the GitHub actions.",
)
def test_openapi():
    """Test openapi schema generation."""
    assert app.openapi()
