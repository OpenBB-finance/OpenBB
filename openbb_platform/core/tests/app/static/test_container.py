"""Test the container.py file."""

from re import escape
from unittest.mock import patch

import pytest
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.defaults import Defaults
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.static.container import Container
from pydantic import BaseModel, SecretStr

# pylint: disable=redefined-outer-name,protected-access


@pytest.fixture(scope="module")
def container():
    """Set up test container class."""

    class MockCredentials(BaseModel):
        provider_1_api_key: SecretStr | None = None
        provider_2_api_key: SecretStr | None = "test_key"

    MockCredentials.origins = {
        "provider_1": ["provider_1_api_key"],
        "provider_2": ["provider_2_api_key"],
        "provider_3": [],
    }

    mock_user_settings = UserSettings()
    mock_user_settings.credentials = MockCredentials()
    mock_user_settings.defaults = Defaults(
        commands={
            "/test/command": {"provider": "provider_1"},
            "test.first_wins.command": {"provider": ["provider_1", "provider_2"]},
            "test.not_available.command": {"provider": ["x", "y", "z"]},
        }
    )
    return Container(CommandRunner(user_settings=mock_user_settings))


def test_container_init(container):
    """Test container init."""
    assert container


@patch("openbb_core.app.command_runner.CommandRunner.sync_run")
def test_container__run(mock_sync_run, container):
    """Test container _run method."""
    container._run()
    mock_sync_run.assert_called_once()


def test_container__check_credentials(container):
    """Test container _check_credentials method."""
    assert container._check_credentials("provider_1") is False
    assert container._check_credentials("provider_2") is True
    assert container._check_credentials("provider_3") is True


@pytest.mark.parametrize(
    "choice, command, default_priority, expected, error_msg",
    [
        # Provider set in args
        ("fmp", ..., ..., "fmp", None),
        # Provider not set in args or config, fallback to provider without keys
        (
            None,
            "test.no_config.command",
            ("provider_1", "provider_3"),
            "provider_3",
            None,
        ),
        # Provider priority set in config, first with key wins
        (
            None,
            "test.first_wins.command",
            ("provider_1", "provider_2", "provider_3"),
            "provider_2",
            None,
        ),
        # Provider priority set in config, with providers not available for the command
        (
            None,
            "test.not_available.command",
            ("provider_1", "provider_2"),
            OpenBBError,
            escape(
                "Provider fallback failed."
                "\n[Providers]\n  * 'x' -> not installed, please install openbb-x\n  * 'y' -> not installed,"
                " please install openbb-y\n  * 'z' -> not installed, please install openbb-z"
            ),
        ),
    ],
)
def test_container__get_provider(
    choice, command, default_priority, expected, error_msg, container
):
    """Test container _get_provider method."""
    if expected is OpenBBError:
        with pytest.raises(expected, match=error_msg):
            container._get_provider(choice, command, default_priority)
    else:
        result = container._get_provider(choice, command, default_priority)
        assert result == expected
