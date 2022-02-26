from contextlib import contextmanager
import pytest
import terminal


@pytest.mark.skip
@pytest.mark.block_network
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quick_exit(mocker, monkeypatch):
    monkeypatch.setattr(terminal.gtff, "ENABLE_QUICK_EXIT", True)
    monkeypatch.setattr(terminal.gtff, "USE_ION", False)
    monkeypatch.setattr(terminal.gtff, "USE_PROMPT_TOOLKIT", True)

    mocker.patch("sys.stdin")

    terminal.terminal()


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_terminal_quit(mocker, monkeypatch):
    monkeypatch.setattr(terminal.gtff, "ENABLE_QUICK_EXIT", False)
    monkeypatch.setattr(terminal.gtff, "USE_ION", False)
    monkeypatch.setattr(terminal.gtff, "USE_PROMPT_TOOLKIT", True)

    mocker.patch("sys.stdin")
    mocker.patch("builtins.input", return_value="e")
    mocker.patch("terminal.session")
    mocker.patch("terminal.session.prompt", return_value="e")
    mocker.patch("terminal.print_goodbye")
    spy_print_goodbye = mocker.spy(terminal, "print_goodbye")

    terminal.terminal()

    spy_print_goodbye.assert_called_once()


@contextmanager
def no_suppress():
    yield


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "debug, test, verbose, filtert, path",
    [
        (True, False, False, None, None),
        (False, False, False, None, ["scripts/test_alt_covid.gst"]),
        (False, True, False, "alt_covid", ["scripts/"]),
        (False, True, True, "alt_covid", ["scripts/"]),
    ],
)
def test_menu(mocker, debug, test, filtert, path, verbose):
    mocker.patch(target="terminal.terminal")
    mocker.patch(target="terminal.suppress_stdout", side_effect=no_suppress)
    terminal.main(debug, test, filtert, path, verbose)
