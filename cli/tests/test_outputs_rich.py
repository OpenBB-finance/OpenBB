"""Tests for RichTableOutput adapter."""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from openbb_cli.outputs.rich import RichTableOutput


@pytest.fixture()
def rich_output():
    return RichTableOutput()


@pytest.fixture()
def mock_session():
    with patch("openbb_cli.outputs.rich.session") as ms:
        ms.console.print = MagicMock()
        ms.settings.USE_INTERACTIVE_DF = False
        ms.backend = None
        yield ms


class TestRichOutputDisplay:
    """Tests for RichTableOutput.display()."""

    def test_export_true_no_output(self, rich_output, mock_session):
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=pd.DataFrame({"a": [1]}), export=True)
            mock_prt.assert_not_called()

    def test_obbject_with_list_results(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}, {"a": 2}]}
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=mock_obj)
            mock_prt.assert_called_once()
            df_arg = mock_prt.call_args[1]["df"]
            assert len(df_arg) == 2

    def test_obbject_with_none_results(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": None}
        rich_output.display(data=mock_obj)
        mock_session.console.print.assert_called()
        msg = mock_session.console.print.call_args[0][0]
        assert "No results" in msg

    def test_obbject_with_empty_list(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": []}
        rich_output.display(data=mock_obj)
        mock_session.console.print.assert_called()

    def test_obbject_with_dict_results(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": {"x": 10}}
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=mock_obj)
            mock_prt.assert_called_once()

    def test_obbject_with_scalar_results(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": 42}
        rich_output.display(data=mock_obj)
        mock_session.console.print.assert_called()

    def test_dataframe(self, rich_output, mock_session):
        df = pd.DataFrame({"col": [1, 2, 3]})
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=df)
            mock_prt.assert_called_once()

    def test_empty_dataframe(self, rich_output, mock_session):
        df = pd.DataFrame()
        rich_output.display(data=df)
        mock_session.console.print.assert_called()

    def test_series(self, rich_output, mock_session):
        s = pd.Series([1, 2, 3], name="vals")
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=s)
            mock_prt.assert_called_once()

    def test_dict_input(self, rich_output, mock_session):
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data={"a": [1, 2], "b": [3, 4]})
            mock_prt.assert_called_once()

    def test_list_input(self, rich_output, mock_session):
        with patch("openbb_cli.outputs.rich.print_rich_table") as mock_prt:
            rich_output.display(data=[{"a": 1}, {"a": 2}])
            mock_prt.assert_called_once()

    def test_scalar_input(self, rich_output, mock_session):
        rich_output.display(data=42)
        mock_session.console.print.assert_called_with(42)

    def test_chart_true_calls_show(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}]}
        mock_obj.show.return_value = None
        rich_output.display(data=mock_obj, chart=True)
        mock_obj.show.assert_called_once()

    def test_chart_true_fallback_on_error(self, rich_output, mock_session):
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}]}
        mock_obj.show.side_effect = Exception("no chart")
        with patch("openbb_cli.outputs.rich.print_rich_table"):
            rich_output.display(data=mock_obj, chart=True)
            mock_session.console.print.assert_called()

    def test_empty_list_input(self, rich_output, mock_session):
        rich_output.display(data=[])
        mock_session.console.print.assert_called()

    def test_interactive_mode_obbject(self, mock_session):
        """When USE_INTERACTIVE_DF is True and backend exists, try charting.table()."""
        mock_session.settings.USE_INTERACTIVE_DF = True
        mock_session.backend = MagicMock()

        rich_output = RichTableOutput()
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}]}
        mock_obj.charting.table.return_value = None

        rich_output.display(data=mock_obj)
        mock_obj.charting.table.assert_called_once()

    def test_interactive_mode_obbject_falls_back_on_error(self, mock_session):
        """charting.table() failure falls through to rich-table display."""
        mock_session.settings.USE_INTERACTIVE_DF = True
        mock_session.backend = MagicMock()

        rich_output = RichTableOutput()
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}]}
        mock_obj.charting.table.side_effect = Exception("no interactive")

        with patch("openbb_cli.outputs.rich.print_rich_table") as prt:
            rich_output.display(data=mock_obj)
        assert any(
            "Interactive table not available" in str(c)
            for c in mock_session.console.print.call_args_list
        )
        prt.assert_called_once()

    def test_obbject_with_dataframe_result_passes_through(
        self, rich_output, mock_session
    ):
        """When OBBject.results is already a DataFrame, it's used directly."""
        df_in = pd.DataFrame({"col": [1, 2]})
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": df_in}
        with patch("openbb_cli.outputs.rich.print_rich_table") as prt:
            rich_output.display(data=mock_obj)
        prt.assert_called_once()

    def test_dataframe_interactive_send_table(self, mock_session):
        """USE_INTERACTIVE_DF + backend → ``send_table`` for DataFrames."""
        mock_session.settings.USE_INTERACTIVE_DF = True
        mock_session.backend = MagicMock()
        mock_session.user.preferences.table_style = "dark"

        rich_output = RichTableOutput()
        df = pd.DataFrame({"a": [1, 2]})
        rich_output.display(data=df, title="t")
        mock_session.backend.send_table.assert_called_once()

    def test_dataframe_interactive_send_table_failure_falls_through(self, mock_session):
        """``send_table`` failure swallowed; rich-table follows."""
        mock_session.settings.USE_INTERACTIVE_DF = True
        mock_session.backend = MagicMock()
        mock_session.backend.send_table.side_effect = Exception("backend down")
        mock_session.user.preferences.table_style = "dark"

        rich_output = RichTableOutput()
        df = pd.DataFrame({"a": [1, 2]})
        with patch("openbb_cli.outputs.rich.print_rich_table") as prt:
            rich_output.display(data=df)
        prt.assert_called_once()

    def test_obbject_dataframe_conversion_failure(self, rich_output, mock_session):
        """OBBject.results that pandas can't coerce falls through to console.print.

        Patch ``pd.DataFrame`` inside ``openbb_cli.outputs.rich`` so the list
        branch raises during construction; this exercises the except handler.
        """
        mock_obj = Mock()
        mock_obj.model_dump.return_value = {"results": [{"a": 1}]}

        with patch(
            "openbb_cli.outputs.rich.pd.DataFrame",
            side_effect=ValueError("cannot construct"),
        ):
            rich_output.display(data=mock_obj)

        assert any(
            "Cannot display as table" in str(c)
            for c in mock_session.console.print.call_args_list
        )

    def test_dict_input_conversion_failure(self, rich_output, mock_session):
        """Dict that ``pd.DataFrame.from_dict`` rejects falls through to console.print."""
        with patch(
            "openbb_cli.outputs.rich.pd.DataFrame.from_dict",
            side_effect=Exception("bad dict"),
        ):
            rich_output.display(data={"a": "scalar"})
        mock_session.console.print.assert_called()

    def test_list_input_conversion_failure(self, rich_output, mock_session):
        """List that ``pd.DataFrame()`` rejects falls through to console.print.

        Wraps ``pd.DataFrame.__call__`` via a sentinel that fails ONLY when
        called from the list-input branch (so the upstream isinstance check
        keeps using the real class).
        """

        class Boom:
            def __iter__(self):
                raise ValueError("synthetic")

        rich_output.display(data=[Boom()])
        mock_session.console.print.assert_called()

    def test_range_index_columns_stringified(self, rich_output, mock_session):
        """RangeIndex columns get stringified before ``print_rich_table``."""
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
        captured = {}

        def capture_prt(**kwargs):
            captured["df"] = kwargs.get("df")

        with patch("openbb_cli.outputs.rich.print_rich_table", side_effect=capture_prt):
            rich_output.display(data=df)
        assert captured.get("df") is not None
        assert list(captured["df"].columns) == ["0", "1", "2"]
