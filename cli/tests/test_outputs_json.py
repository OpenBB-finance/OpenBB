"""Tests for JsonOutput adapter."""

import json
from unittest.mock import Mock

import pandas as pd
import pytest

from openbb_cli.outputs.json import JsonOutput, _to_serializable


@pytest.fixture()
def json_output():
    return JsonOutput()


def _captured_json(capsys):
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


def test_export_true_produces_no_output(json_output, capsys):
    json_output.display(data={"key": "val"}, export=True)
    assert capsys.readouterr().out == ""


def test_obbject_with_list_results(json_output, capsys):
    mock_obj = Mock()
    mock_obj.model_dump.return_value = {"results": [{"a": 1}, {"b": 2}]}
    json_output.display(data=mock_obj)
    assert _captured_json(capsys) == [{"a": 1}, {"b": 2}]


def test_obbject_with_dict_results(json_output, capsys):
    mock_obj = Mock()
    mock_obj.model_dump.return_value = {"results": {"x": 10}}
    json_output.display(data=mock_obj)
    assert _captured_json(capsys) == {"x": 10}


def test_dataframe(json_output, capsys):
    df = pd.DataFrame({"col": [1, 2]})
    json_output.display(data=df)
    assert _captured_json(capsys) == [{"col": 1}, {"col": 2}]


def test_series(json_output, capsys):
    s = pd.Series({"a": 1, "b": 2})
    json_output.display(data=s)
    assert _captured_json(capsys) == {"a": 1, "b": 2}


def test_scalar(json_output, capsys):
    json_output.display(data=42)
    assert _captured_json(capsys) == 42


def test_none_data(json_output, capsys):
    json_output.display(data=None)
    assert capsys.readouterr().out.strip() == "null"


def test_serialization_failure_emits_error_envelope(json_output, capsys):
    """First dumps() raises → error envelope is dumped via the original."""
    bad = {"k": object()}

    import openbb_cli.outputs.json as mod

    original = mod.json.dumps
    calls = {"n": 0}

    def maybe_failing(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TypeError("not serializable")
        return original(*args, **kwargs)

    mod.json.dumps = maybe_failing
    try:
        json_output.display(data=bad)
    finally:
        mod.json.dumps = original

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["error"]["type"] == "TypeError"
    assert "not serializable" in payload["error"]["message"]


def test_no_ansi_in_output(json_output, capsys):
    json_output.display(data={"a": 1})
    assert "\x1b[" not in capsys.readouterr().out


def test_to_serializable_passthrough_primitives():
    assert _to_serializable(42) == 42
    assert _to_serializable(None) is None
    assert _to_serializable("x") == "x"


def test_to_serializable_obbject_extracts_results():
    mock_obj = Mock()
    mock_obj.model_dump.return_value = {"results": [1, 2, 3]}
    assert _to_serializable(mock_obj) == [1, 2, 3]
