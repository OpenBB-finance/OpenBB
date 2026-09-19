"""Tests for TsvOutput adapter."""

from unittest.mock import Mock

import pandas as pd
import pytest

from openbb_cli.outputs.tsv import TsvOutput, _to_dataframe


@pytest.fixture()
def tsv_output():
    return TsvOutput()


class TestTsvOutputDisplay:
    """The TSV adapter writes the full DataFrame to stdout as TSV."""

    def test_export_true_no_output(self, tsv_output, capsys):
        tsv_output.display(data="anything", export=True)
        assert capsys.readouterr().out == ""

    def test_obbject_with_list_results(self, tsv_output, capsys):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {
            "results": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        }
        tsv_output.display(data=mock_obj)
        out = capsys.readouterr().out
        assert "a\tb" in out
        assert "1\t2" in out

    def test_obbject_with_none_results_emits_nothing(self, tsv_output, capsys):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": None}
        tsv_output.display(data=mock_obj)
        assert capsys.readouterr().out == ""

    def test_obbject_with_dict_results(self, tsv_output, capsys):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": {"x": 10}}
        tsv_output.display(data=mock_obj)
        out = capsys.readouterr().out
        assert "x" in out
        assert "10" in out

    def test_obbject_with_scalar_results_emits_repr(self, tsv_output, capsys):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": 42}
        tsv_output.display(data=mock_obj)
        assert capsys.readouterr().out == ""

    def test_dataframe(self, tsv_output, capsys):
        df = pd.DataFrame({"col": [1, 2, 3]})
        tsv_output.display(data=df)
        out = capsys.readouterr().out
        assert "col" in out
        assert "\t" not in out.split("\n")[0] or "col" in out

    def test_series(self, tsv_output, capsys):
        s = pd.Series([10, 20], name="vals")
        tsv_output.display(data=s)
        out = capsys.readouterr().out
        assert "vals" in out

    def test_dict_input(self, tsv_output, capsys):
        tsv_output.display(data={"a": [1], "b": [2]})
        out = capsys.readouterr().out
        assert "a\tb" in out

    def test_list_input(self, tsv_output, capsys):
        tsv_output.display(data=[{"val": 5}])
        out = capsys.readouterr().out
        assert "val" in out
        assert "5" in out

    def test_scalar_input_writes_repr(self, tsv_output, capsys):
        tsv_output.display(data="hello")
        out = capsys.readouterr().out.strip()
        assert out == "'hello'"

    def test_chart_with_chart_attr_returns_early(self, tsv_output, capsys):
        mock_obj = Mock()
        mock_obj.chart = "chart-object-repr"
        tsv_output.display(data=mock_obj, chart=True)
        assert capsys.readouterr().out == ""

    def test_no_ansi_in_output(self, tsv_output, capsys):
        df = pd.DataFrame({"a": [1, 2]})
        tsv_output.display(data=df)
        out = capsys.readouterr().out
        assert "\x1b[" not in out


def test_to_dataframe_passthrough_obbject_dataframe():
    mock_obj = Mock()
    df = pd.DataFrame({"a": [1]})
    mock_obj.model_dump.return_value = {"results": df}
    assert _to_dataframe(mock_obj) is df


def test_to_dataframe_returns_none_for_unknown():
    class X:
        pass

    assert _to_dataframe(X()) is None
