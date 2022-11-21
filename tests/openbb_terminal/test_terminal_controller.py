from contextlib import contextmanager
import pytest
from openbb_terminal import terminal_controller


@pytest.mark.skip
@pytest.mark.block_network
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quick_exit(mocker, monkeypatch):
    monkeypatch.setattr(terminal_controller.obbff, "ENABLE_QUICK_EXIT", True)
    monkeypatch.setattr(terminal_controller.obbff, "USE_ION", False)
    monkeypatch.setattr(terminal_controller.obbff, "USE_PROMPT_TOOLKIT", True)

    mocker.patch("sys.stdin")

    terminal_controller.terminal()


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quit(mocker, monkeypatch):
    monkeypatch.setattr(terminal_controller.obbff, "ENABLE_QUICK_EXIT", False)
    monkeypatch.setattr(terminal_controller.obbff, "USE_ION", False)
    monkeypatch.setattr(terminal_controller.obbff, "USE_PROMPT_TOOLKIT", True)

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
    "debug, test, verbose, filtert, path",
    [
        (True, False, False, None, None),
        (False, False, False, None, ["scripts/test_alt_covid.openbb"]),
        #       (False, True, False, "alt_covid", ["scripts/"]),
        #       (False, True, True, "alt_covid", ["scripts/"]),
    ],
)
def test_menu(mocker, debug, test, filtert, path, verbose):
    mocker.patch(target="terminal_controller.terminal")
    mocker.patch(target="terminal_controller.suppress_stdout", side_effect=no_suppress)
    terminal_controller.main(debug, test, filtert, path, verbose)
