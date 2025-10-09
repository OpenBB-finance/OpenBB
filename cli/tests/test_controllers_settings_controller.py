"""Test the SettingsController class."""

from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.controllers.settings_controller import SettingsController

# pylint: disable=redefined-outer-name, unused-argument, no-member


@pytest.fixture
def mock_session():
    with patch("openbb_cli.controllers.settings_controller.session") as mock:
        mock.settings.USE_INTERACTIVE_DF = False
        mock.settings.ALLOWED_NUMBER_OF_ROWS = 20
        mock.settings.TIMEZONE = "UTC"
        mock.style.available_styles = ["dark"]
        mock.settings.set_item = MagicMock()

        yield mock


def test_call_interactive(mock_session):
    controller = SettingsController()
    controller.call_interactive(None)
    mock_session.settings.set_item.assert_called_once_with("USE_INTERACTIVE_DF", True)


@pytest.mark.parametrize(
    "input_rows, expected",
    [
        (10, 10),
        (15, 15),
    ],
)
def test_call_n_rows(input_rows, expected, mock_session):
    controller = SettingsController()
    args = ["--value", str(input_rows)]
    controller.call_n_rows(args)
    mock_session.settings.set_item.assert_called_with(
        "ALLOWED_NUMBER_OF_ROWS", expected
    )


def test_call_n_rows_no_args_provided(mock_session):
    controller = SettingsController()
    controller.call_n_rows([])
    mock_session.console.print.assert_called_with("[info]Current value:[/info] 20")


@pytest.mark.parametrize(
    "timezone, valid",
    [
        ("UTC", True),
        ("Mars/Phobos", False),
    ],
)
def test_call_timezone(timezone, valid, mock_session):
    controller = SettingsController()
    args = ["--value", timezone]
    controller.call_timezone(args)
    if valid:
        mock_session.settings.set_item.assert_called_with("TIMEZONE", timezone)
    else:
        mock_session.settings.set_item.assert_not_called()


def test_call_console_style(mock_session):
    controller = SettingsController()
    args = ["--value", "dark"]
    controller.call_console_style(args)
    mock_session.console.print.assert_called()


def test_call_console_style_no_args(mock_session):
    mock_session.settings.RICH_STYLE = "default"
    controller = SettingsController()
    controller.call_console_style([])
    mock_session.console.print.assert_called_with("[info]Current value:[/info] default")


def test_call_flair(mock_session):
    controller = SettingsController()
    args = ["--value", "rocket"]
    controller.call_flair(args)


def test_call_flair_no_args(mock_session):
    mock_session.settings.FLAIR = "bug"
    controller = SettingsController()
    controller.call_flair([])
    mock_session.console.print.assert_called_with("[info]Current value:[/info] bug")


def test_call_obbject_display(mock_session):
    controller = SettingsController()
    args = ["--value", "5"]
    controller.call_obbject_display(args)
    mock_session.settings.set_item.assert_called_once_with(
        "N_TO_DISPLAY_OBBJECT_REGISTRY", 5
    )


def test_call_obbject_display_no_args(mock_session):
    mock_session.settings.N_TO_DISPLAY_OBBJECT_REGISTRY = 10
    controller = SettingsController()
    controller.call_obbject_display([])
    mock_session.console.print.assert_called_with("[info]Current value:[/info] 10")


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--value", "50"], 50),
        (["--value", "100"], 100),
        ([], 20),
    ],
)
def test_call_n_rows_v2(args, expected, mock_session):
    mock_session.settings.ALLOWED_NUMBER_OF_ROWS = 20
    controller = SettingsController()
    controller.call_n_rows(args)
    if args:
        mock_session.settings.set_item.assert_called_with(
            "ALLOWED_NUMBER_OF_ROWS", expected
        )
    else:
        mock_session.console.print.assert_called_with("[info]Current value:[/info] 20")
