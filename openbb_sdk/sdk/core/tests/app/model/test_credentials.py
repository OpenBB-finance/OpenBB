import typing
from unittest.mock import patch


def test_credentials():
    with patch(
        target="openbb_core.app.model.credentials.get_provider_interface"
    ) as mock_provider_interface:
        mock_provider_interface.required_credentials = {
            "benzinga_api_key": (typing.Optional[str], None),
            "polygon_api_key": (typing.Optional[str], None),
        }
        from openbb_core.app.model.credentials import Credentials

        creds = Credentials(
            benzinga_api_key="mock_benzinga_api_key",
            polygon_api_key="mock_polygon_api_key",
        )

        assert isinstance(creds, Credentials)
        assert creds.benzinga_api_key == "mock_benzinga_api_key"
        assert creds.polygon_api_key == "mock_polygon_api_key"
