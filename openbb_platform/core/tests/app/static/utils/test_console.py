"""Tests for openbb_core.app.static.utils.console.Console."""

from openbb_core.app.static.utils.console import Console


def test_console_log_verbose(capsys):
    Console(verbose=True).log("hello")
    out = capsys.readouterr().out
    assert "hello" in out


def test_console_log_quiet_when_not_verbose_and_not_debug(capsys, monkeypatch):
    monkeypatch.setattr(
        "openbb_core.app.static.utils.console.Env",
        type("E", (), {"DEBUG_MODE": False}),
    )
    Console(verbose=False).log("quiet")
    assert capsys.readouterr().out == ""


def test_console_log_in_debug_mode(capsys, monkeypatch):
    monkeypatch.setattr(
        "openbb_core.app.static.utils.console.Env",
        type("E", (), {"DEBUG_MODE": True}),
    )
    Console(verbose=False).log("debug-only")
    assert "debug-only" in capsys.readouterr().out


def test_console_error_always_prints(capsys):
    Console(verbose=False).error("oops")
    assert "oops" in capsys.readouterr().out
