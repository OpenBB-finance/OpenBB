"""Wrapped native tables must remain structured in stdout JSON."""

import json

import pandas as pd
import pytest
from openbb_core.app.model.obbject import OBBject

from openbb_cli.outputs.json import JsonOutput


@pytest.mark.parametrize(
    "table,expected",
    [
        (
            pd.DataFrame({"symbol": ["AAPL"], "price": [42]}),
            [{"symbol": "AAPL", "price": 42}],
        ),
        (pd.Series({"AAPL": 42}), {"AAPL": 42}),
    ],
)
def test_wrapped_table_serializes_like_direct_table(table, expected, capsys):
    JsonOutput().display(OBBject(results=table))
    assert json.loads(capsys.readouterr().out) == expected


def test_wrapped_records_control(capsys):
    JsonOutput().display(OBBject(results=[{"value": 1}]))
    assert json.loads(capsys.readouterr().out) == [{"value": 1}]
