"""Test the container.py file."""

from re import escape
from unittest.mock import patch

import pytest
from pydantic import BaseModel, SecretStr

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.defaults import Defaults
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.static.container import Container


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


"""Extended Container tests targeting uncovered branches."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from openbb_core.app.model.obbject import OBBject


@pytest.fixture
def container_with_defaults():
    class MockCredentials(BaseModel):
        provider_1_api_key: SecretStr | None = None

    MockCredentials.origins = {"provider_1": ["provider_1_api_key"]}

    settings = UserSettings()
    settings.credentials = MockCredentials()
    settings.defaults = Defaults(
        commands={
            "test.cmd": {
                "provider": "provider_1",
                "chart": True,
                "limit": 50,
                "extra_only": "x",
            }
        }
    )
    return Container(CommandRunner(user_settings=settings))


@patch("openbb_core.app.command_runner.CommandRunner.sync_run")
def test_run_applies_defaults_to_standard_and_extra_params(
    mock_sync_run, container_with_defaults
):
    container_with_defaults._run(
        "/test/cmd",
        standard_params={"limit": None},
        extra_params={"extra_only": None},
    )
    args, kwargs = mock_sync_run.call_args
    assert kwargs["standard_params"]["limit"] == 50
    assert kwargs["extra_params"]["extra_only"] == "x"
    assert kwargs.get("chart") is True


@patch("openbb_core.app.command_runner.CommandRunner.sync_run")
def test_run_results_only_returns_results_list(mock_sync_run):
    settings = UserSettings()
    c = Container(CommandRunner(user_settings=settings))

    obb = OBBject(results=[{"a": 1}])
    object.__setattr__(obb, "_results_only", True)
    mock_sync_run.return_value = obb

    out = c._run(
        "/foo",
        standard_params={},
        extra_params={},
    )
    assert out == [{"a": 1}]


@patch("openbb_core.app.command_runner.CommandRunner.sync_run")
def test_run_with_dataframe_output_type(mock_sync_run):
    settings = UserSettings()
    settings.preferences.output_type = "dataframe"
    c = Container(CommandRunner(user_settings=settings))

    fake = SimpleNamespace(to_dataframe=lambda: "DF", _results_only=False)
    mock_sync_run.return_value = fake

    out = c._run("/foo", standard_params={}, extra_params={})
    assert out == "DF"


def test_get_provider_single_provider_in_config_short_circuits():
    class MockCredentials(BaseModel):
        provider_1_api_key: SecretStr | None = None

    MockCredentials.origins = {"provider_1": ["provider_1_api_key"]}

    settings = UserSettings()
    settings.credentials = MockCredentials()
    settings.defaults = Defaults(commands={"only.one": {"provider": ["solo"]}})
    c = Container(CommandRunner(user_settings=settings))
    # Single provider in config list -> returned without credential check (line 101).
    assert c._get_provider(None, "only.one", ("a", "b")) == "solo"
