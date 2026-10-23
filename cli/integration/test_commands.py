"""Integration tests for CLI commands.

The default mode is non-TTY: ``main()`` parses argv, dispatches one command,
emits a JSON line, and exits. These tests cover that one-shot path against
real provider commands — they require API credentials and are gated by the
``integration`` marker so they don't run in default CI sweeps.
"""

import shlex

import pytest

from openbb_cli.cli import main


@pytest.mark.parametrize(
    "command",
    [
        "equity.price.historical --symbol aapl --provider fmp",
        "equity.price.historical --symbol msft --provider yfinance",
        "equity.price.historical --symbol goog --provider polygon",
        "crypto.price.historical --symbol btc --provider fmp",
        "currency.price.historical --symbol eur --provider fmp",
        "derivatives.futures.historical --symbol cl --provider fmp",
        "etf.price.historical --symbol spy --provider fmp",
    ],
)
@pytest.mark.integration
def test_launch_one_shot(capsys, command):
    """``main(argv)`` dispatches the command and exits without raising.

    The exit code may be non-zero (e.g. missing API key) — we only assert
    that the entry point returns cleanly and emits a JSON line on stdout.
    """
    rc = main(shlex.split(command))
    captured = capsys.readouterr()
    assert isinstance(rc, int)
    assert captured.out, "expected a JSON response line on stdout"
