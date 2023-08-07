from openbb_core.app.model.hub.hub_session import HubSession


def test_hub_session():
    session = HubSession(
        access_token="mock_access_token",
        token_type="mock_token_type",
        email="mock_email",
        user_uuid="mock_user_uuid",
        username="mock_username",
        primary_usage="mock_primary_usage",
    )
    assert session.access_token == "mock_access_token"
    assert session.token_type == "mock_token_type"
    assert session.email == "mock_email"
    assert session.user_uuid == "mock_user_uuid"
    assert session.username == "mock_username"
    assert session.primary_usage == "mock_primary_usage"


def test_fields():
    fields = HubSession.__fields__
    fields_keys = fields.keys()

    assert "access_token" in fields_keys
    assert "token_type" in fields_keys
    assert "email" in fields_keys
    assert "user_uuid" in fields_keys
    assert "username" in fields_keys
    assert "primary_usage" in fields_keys
