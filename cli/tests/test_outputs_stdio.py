"""Tests for StdioOutput — alias for TsvOutput."""

import pandas as pd
import pytest

from openbb_cli.outputs.stdio import StdioOutput
from openbb_cli.outputs.tsv import TsvOutput


@pytest.fixture()
def stdio_output():
    return StdioOutput()


def test_stdio_is_tsv_subclass():
    assert issubclass(StdioOutput, TsvOutput)


def test_stdio_export_no_output(stdio_output, capsys):
    stdio_output.display(data="x", export=True)
    assert capsys.readouterr().out == ""


def test_stdio_dataframe(stdio_output, capsys):
    df = pd.DataFrame({"x": [10, 20], "y": [30, 40]})
    stdio_output.display(data=df)
    out = capsys.readouterr().out
    assert "x\ty" in out
    assert "10\t30" in out


def test_stdio_no_ansi_in_output(stdio_output, capsys):
    df = pd.DataFrame({"a": [1]})
    stdio_output.display(data=df)
    assert "\x1b[" not in capsys.readouterr().out
