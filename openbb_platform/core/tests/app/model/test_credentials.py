"""Test the Credentials model."""

import importlib
from unittest.mock import patch


# pylint: disable=import-outside-toplevel
def test_credentials():
    """Test the Credentials model."""
    with patch(
        "openbb_core.app.model.credentials.ProviderInterface"
    ) as mock_provider_interface, patch.dict(
        "os.environ", {"MOCK_ENV_API_KEY": "mock_env_key_value"}
    ):
        mock_provider_interface.return_value.credentials = {
            "benzinga": ["benzinga_api_key"],
            "polygon": ["polygon_api_key"],
        }

        # Reload the module so CredentialsLoader picks up the patched environment
        import openbb_core.app.model.credentials as credentials_module

        importlib.reload(credentials_module)
        Credentials = credentials_module.Credentials

        creds = Credentials(
            benzinga_api_key="mock_benzinga_api_key",
            polygon_api_key="mock_polygon_api_key",
        )

        assert isinstance(creds, Credentials)
        assert creds.benzinga_api_key.get_secret_value() == "mock_benzinga_api_key"
        assert creds.polygon_api_key.get_secret_value() == "mock_polygon_api_key"
        assert creds.mock_env_api_key.get_secret_value() == "mock_env_key_value"
