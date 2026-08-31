"""Tests for EIA provider helpers."""

import asyncio

import pytest
from openbb_core.provider.utils.errors import MissingCredentialError
from openbb_us_eia.utils.helpers import response_callback


class MockResponse:
    """Mock aiohttp response."""

    def __init__(self, status, payload):
        """Initialize the mock response."""
        self.status = status
        self._payload = payload

    async def json(self):
        """Return the JSON payload."""
        return self._payload


def test_response_callback_missing_api_key_raises_missing_credential():
    """Raise MissingCredentialError when the EIA API reports API_KEY_MISSING."""
    response = MockResponse(
        status=403,
        payload={
            "error": {
                "code": "API_KEY_MISSING",
                "message": "No api_key was supplied.",
            }
        },
    )

    with pytest.raises(MissingCredentialError) as exc_info:
        asyncio.run(response_callback(response, None))

    assert exc_info.value.provider == "eia"
    assert exc_info.value.credential == "eia_api_key"


def test_response_callback_other_403_raises_generic_error():
    """Keep generic OpenBBError for non-missing-key 403 responses."""
    response = MockResponse(
        status=403,
        payload={
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid key.",
            }
        },
    )

    with pytest.raises(Exception) as exc_info:
        asyncio.run(response_callback(response, None))

    assert not isinstance(exc_info.value, MissingCredentialError)
    assert "UNAUTHORIZED" in str(exc_info.value)
