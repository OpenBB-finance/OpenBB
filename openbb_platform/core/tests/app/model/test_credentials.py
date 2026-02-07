"""Test the Credentials model."""

import importlib
import json
import sys
from unittest.mock import mock_open, patch


# pylint: disable=import-outside-toplevel
def test_credentials():
    """Test the Credentials model."""
    # Remove credentials module to ensure fresh import with mocks
    for mod_name in list(sys.modules.keys()):
        if "openbb_core.app.model.credentials" in mod_name:
            del sys.modules[mod_name]

    with (
        patch(
            "openbb_core.app.provider_interface.ProviderInterface"
        ) as mock_provider_interface,
        patch("openbb_core.app.extension_loader.ExtensionLoader") as mock_loader,
        patch("openbb_core.app.model.credentials.Path.exists", return_value=False),
        patch.dict(
            "os.environ", {"MOCK_ENV_API_KEY": "mock_env_key_value"}, clear=True
        ),
    ):
        # Ensure the mock instance returns the credentials dict
        mock_instance = mock_provider_interface.return_value
        mock_instance.credentials = {
            "benzinga": ["benzinga_api_key"],
            "mock_provider": ["mock_provider_api_key"],
        }
        mock_loader.return_value.obbject_objects = {}

        # Import the module fresh (within the patch context)
        import openbb_core.app.model.credentials as credentials_module

        importlib.reload(credentials_module)
        Credentials = credentials_module.Credentials

        creds = Credentials(
            benzinga_api_key="mock_benzinga_api_key",
            mock_provider_api_key="mock_provider_api_key",
        )

        assert isinstance(creds, Credentials)
        assert creds.benzinga_api_key.get_secret_value() == "mock_benzinga_api_key"
        assert creds.mock_provider_api_key.get_secret_value() == "mock_provider_api_key"
        assert creds.mock_env_api_key.get_secret_value() == "mock_env_key_value"


def test_credentials_env_overrides_null():
    """Environment variables replace stored null credentials."""
    # Remove credentials module to ensure fresh import with mocks
    for mod_name in list(sys.modules.keys()):
        if "openbb_core.app.model.credentials" in mod_name:
            del sys.modules[mod_name]

    fake_user_settings = json.dumps({"credentials": {"econdb_api_key": None}})
    with (
        patch(
            "openbb_core.app.provider_interface.ProviderInterface"
        ) as mock_provider_interface,
        patch("openbb_core.app.extension_loader.ExtensionLoader") as mock_loader,
        patch("openbb_core.app.model.credentials.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=fake_user_settings)),
        patch.dict("os.environ", {"ECONDB_API_KEY": "env_econdb_key"}),
    ):
        mock_provider_interface.return_value.credentials = {
            "econdb": ["econdb_api_key"]
        }
        mock_loader.return_value.obbject_objects = {}

        import openbb_core.app.model.credentials as credentials_module

        importlib.reload(credentials_module)
        Credentials = credentials_module.Credentials

        creds = Credentials()

        assert creds.econdb_api_key.get_secret_value() == "env_econdb_key"
