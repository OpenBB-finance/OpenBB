# IMPORTATION STANDARD

from contextlib import contextmanager

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal import terminal_controller
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)


@pytest.mark.skip
@pytest.mark.block_network
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quick_exit(mocker):
    preferences = PreferencesModel(
        ENABLE_QUICK_EXIT=True,
        USE_PROMPT_TOOLKIT=True,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    mocker.patch("sys.stdin")

    terminal_controller.terminal()


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quit(mocker):
    preferences = PreferencesModel(
        ENABLE_QUICK_EXIT=True,
        USE_PROMPT_TOOLKIT=True,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    mocker.patch("sys.stdin")
    mocker.patch("builtins.input", return_value="e")
    mocker.patch("terminal_controller.session")
    mocker.patch("terminal_controller.session.prompt", return_value="e")
    mocker.patch("terminal_controller.print_goodbye")
    spy_print_goodbye = mocker.spy(terminal_controller, "print_goodbye")

    terminal_controller.terminal()

    spy_print_goodbye.assert_called_once()


@contextmanager
def no_suppress():
    yield


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "debug, dev, path",
    [(True, False, None), (False, False, ["scripts/test_alt_covid.openbb"])],
)
def test_menu(mocker, debug, dev, path):
    mocker.patch(target="terminal_controller.terminal")
    mocker.patch(target="terminal_controller.suppress_stdout", side_effect=no_suppress)
    terminal_controller.main(debug, dev, path)
