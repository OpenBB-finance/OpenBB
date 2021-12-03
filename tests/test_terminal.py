import pytest
import terminal


@pytest.mark.block_network
@pytest.mark.record_stdout
def test_terminal_quick_exit(mocker, monkeypatch):
    monkeypatch.setattr(terminal.gtff, "ENABLE_QUICK_EXIT", True)
    monkeypatch.setattr(terminal.gtff, "USE_ION", True)
    monkeypatch.setattr(terminal.gtff, "USE_PROMPT_TOOLKIT", True)

    mocker.patch("sys.stdin")

    terminal.terminal()


@pytest.mark.block_network
@pytest.mark.record_stdout
def test_terminal_quit(mocker, monkeypatch):
    monkeypatch.setattr(terminal.gtff, "ENABLE_QUICK_EXIT", False)
    monkeypatch.setattr(terminal.gtff, "USE_ION", True)
    monkeypatch.setattr(terminal.gtff, "USE_PROMPT_TOOLKIT", True)

    mocker.patch("sys.stdin")
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("terminal.session")
    mocker.patch("terminal.session.prompt", return_value="quit")
    mocker.patch("terminal.print_goodbye")
    spy_print_goodbye = mocker.spy(terminal, "print_goodbye")

    terminal.terminal()

    spy_print_goodbye.assert_called_once()
