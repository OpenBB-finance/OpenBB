"""Test the HubSession class."""

from openbb_core.app.model.hub.hub_session import HubSession
from pydantic import SecretStr

# ruff: noqa: S105 S106


def test_hub_session():
    """Test the HubSession class."""
    session = HubSession(
        access_token=SecretStr("mock_access_token"),
        token_type="mock_token_type",
        email="mock_email",
        user_uuid="mock_user_uuid",
        username="mock_username",
        primary_usage="mock_primary_usage",
    )
    assert session.access_token.get_secret_value() == "mock_access_token"
    assert session.token_type == "mock_token_type"
    assert session.email == "mock_email"
    assert session.user_uuid == "mock_user_uuid"
    assert session.username == "mock_username"
    assert session.primary_usage == "mock_primary_usage"


def test_fields():
    """Test the HubSession fields."""
    fields = HubSession.model_fields
    fields_keys = fields.keys()

    assert "access_token" in fields_keys
    assert "token_type" in fields_keys
    assert "email" in fields_keys
    assert "user_uuid" in fields_keys
    assert "username" in fields_keys
    assert "primary_usage" in fields_keys
