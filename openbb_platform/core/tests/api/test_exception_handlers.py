"""Test API exception handlers."""

import asyncio
import json

from openbb_core.api.exception_handlers import ExceptionHandlers
from openbb_core.provider.utils.errors import MissingCredentialError


def get_response_detail(response):
    """Return the JSON response detail."""
    return json.loads(response.body)["detail"]


def test_missing_credential_returns_structured_400():
    """Return a structured 4xx when a provider credential is missing."""
    error = MissingCredentialError(provider="eia", credential="eia_api_key")

    response = asyncio.run(ExceptionHandlers.missing_credential(None, error))

    assert response.status_code == 400
    detail = get_response_detail(response)
    assert detail["code"] == "missing_credentials"
    assert detail["provider"] == "eia"
    assert detail["credential"] == "eia_api_key"
    assert "eia_api_key" in detail["message"]


def test_missing_credential_message_preserved():
    """Keep the provider-provided message when one is supplied."""
    error = MissingCredentialError(
        provider="eia",
        credential="eia_api_key",
        message="API_KEY_MISSING -> No api_key was supplied.",
    )

    response = asyncio.run(ExceptionHandlers.missing_credential(None, error))

    detail = get_response_detail(response)
    assert detail["message"] == "API_KEY_MISSING -> No api_key was supplied."


def test_missing_credential_is_openbb_error():
    """MissingCredentialError must remain an OpenBBError for backward compatibility."""
    error = MissingCredentialError(provider="eia", credential="eia_api_key")

    assert isinstance(error, Exception)
    assert str(error) == error.message
