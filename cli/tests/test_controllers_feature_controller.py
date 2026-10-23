"""Test the FeatureController class."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

MODULE = "openbb_cli.controllers.feature_controller"


@pytest.fixture
def sample_df():
    """Return a small sample DataFrame."""
    return pd.DataFrame({"A": [1, 2, 3], "B": [4.0, 5.0, 6.0], "C": ["x", "y", "z"]})


@pytest.fixture
def mock_result(sample_df):
    """Return a mock OBBject with a DataFrame."""
    result = MagicMock()
    result.results = sample_df
    result.extra = {}
    result.id = "test-id"
    result.to_dataframe.return_value = sample_df
    return result


@pytest.fixture
def mock_session(mock_result):
    """Create a mock session with registry containing one table."""
    with patch(f"{MODULE}.session") as sess:
        sess.console = MagicMock()
        sess.output_adapter = MagicMock()
        sess.settings = MagicMock()
        sess.obbject_registry = MagicMock()
        sess.obbject_registry.all = {0: {"key": "prices"}}
        sess.obbject_registry.get.return_value = mock_result
        sess.obbject_registry.obbjects = [mock_result]
        yield sess


@pytest.fixture
def controller(mock_session, sample_df):
    """Create a FeatureController with mocks."""
    with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
        from openbb_cli.controllers.feature_controller import FeatureController

        ctrl = FeatureController.__new__(FeatureController)
        ctrl.current_table = None
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl.parse_known_args_and_warn = MagicMock()
        yield ctrl


def test_feature_controller_init_runs_super_and_initializes_state(mock_session):
    """``__init__`` chains super, sets ``current_table = None``, updates completer."""
    from openbb_cli.controllers.feature_controller import FeatureController

    with (
        patch(
            "openbb_cli.controllers.base_controller.BaseController.__init__",
            return_value=None,
        ) as super_init,
        patch.object(FeatureController, "update_completer") as update_completer,
    ):
        ctrl = FeatureController(queue=["q"])
    super_init.assert_called_once_with(queue=["q"])
    assert ctrl.current_table is None
    update_completer.assert_called_once()


class TestGetTableIndices:
    def test_returns_register_keys(self, controller, mock_session):
        mock_session.obbject_registry.all = {0: {"key": "prices"}, 1: {"key": "vol"}}
        assert controller._get_table_indices() == ["prices", "vol"]

    def test_returns_numeric_index_when_no_key(self, controller, mock_session):
        mock_session.obbject_registry.all = {0: {"key": ""}, 1: {"key": ""}}
        assert controller._get_table_indices() == ["0", "1"]

    def test_empty_registry(self, controller, mock_session):
        mock_session.obbject_registry.all = {}
        assert controller._get_table_indices() == []


class TestResolveTableIdentifier:
    def test_numeric_index(self, controller, mock_session):
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        assert controller._resolve_table_identifier("0") == 0

    def test_register_key(self, controller, mock_session):
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        assert controller._resolve_table_identifier("prices") == 0

    def test_unknown_returns_none(self, controller, mock_session):
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        assert controller._resolve_table_identifier("unknown") is None


class TestGetColumnNames:
    def test_returns_columns_when_selected(self, controller, mock_session, sample_df):
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            assert controller._get_column_names() == ["A", "B", "C"]

    def test_empty_when_no_table(self, controller):
        controller.current_table = None
        assert controller._get_column_names() == []

    def test_empty_when_result_is_none(self, controller, mock_session):
        controller.current_table = 0
        mock_session.obbject_registry.get.return_value = None
        assert controller._get_column_names() == []


class TestCallList:
    def test_empty_registry(self, controller, mock_session):
        mock_session.obbject_registry.all = {}
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.call_list([])
        mock_session.console.print.assert_called()
        args = mock_session.console.print.call_args[0][0]
        assert "No tables" in args

    def test_populated_registry(self, controller, mock_session, sample_df):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_list([])
        mock_session.output_adapter.display.assert_called_once()

    def test_no_parser(self, controller):
        controller.parse_known_args_and_warn.return_value = None
        controller.call_list([])


class TestCallSelect:
    def test_valid_select(self, controller, mock_session, mock_result, sample_df):
        ns = MagicMock()
        ns.index = "prices"
        controller.parse_known_args_and_warn.return_value = ns
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_select([])
        assert controller.current_table is not None
        mock_session.console.print.assert_called()

    def test_invalid_select(self, controller, mock_session):
        ns = MagicMock()
        ns.index = "nonexistent"
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.get.return_value = None
        controller.call_select([])
        args = mock_session.console.print.call_args[0][0]
        assert "not found" in args


class TestCallInfo:
    def test_no_table_selected(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_info([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_with_table(self, controller, mock_session, sample_df):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_info([])
        mock_session.output_adapter.display.assert_called_once()
        call_kwargs = mock_session.output_adapter.display.call_args[1]
        assert isinstance(call_kwargs["data"], pd.DataFrame)


class TestCallView:
    def test_no_table_selected(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_view([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_full_view(self, controller, mock_session, sample_df):
        ns = MagicMock()
        ns.head = None
        ns.tail = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_view([])
        mock_session.output_adapter.display.assert_called_once()

    def test_head(self, controller, mock_session, sample_df):
        ns = MagicMock()
        ns.head = 1
        ns.tail = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_view([])
        displayed = mock_session.output_adapter.display.call_args[1]["data"]
        assert len(displayed) == 1

    def test_tail(self, controller, mock_session, sample_df):
        ns = MagicMock()
        ns.head = None
        ns.tail = 2
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_view([])
        displayed = mock_session.output_adapter.display.call_args[1]["data"]
        assert len(displayed) == 2


class TestCallQuery:
    def test_no_table_selected(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_query([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_dataframe_result(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.expression = ["df[df['A']", ">", "1]"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])
        mock_session.output_adapter.display.assert_called()

    def test_save_flag(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.expression = ["df.head(1)"]
        ns.save = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])
        assert mock_result.results is not None

    def test_invalid_expression(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.expression = ["invalid_var_xyz"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])
        assert any(
            "error" in str(c).lower() for c in mock_session.console.print.call_args_list
        )


class TestCallColname:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_colname([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_lists_columns(self, controller, mock_session, sample_df):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_colname([])
        mock_session.output_adapter.display.assert_called_once()
        data = mock_session.output_adapter.display.call_args[1]["data"]
        assert list(data["Column"]) == ["A", "B", "C"]


class TestCallColtype:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_coltype([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_change_to_float(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.column = "A"
        ns.dtype = "float64"
        ns.categories = None
        ns.ordered = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_coltype([])
        mock_session.console.print.assert_called()
        args = mock_session.console.print.call_args[0][0]
        assert "Changed column" in args

    def test_datetime_conversion(self, controller, mock_session, mock_result):
        df = pd.DataFrame({"date": ["2024-01-01", "2024-02-01"]})
        ns = MagicMock()
        ns.column = "date"
        ns.dtype = "datetime64[ns]"
        ns.categories = None
        ns.ordered = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=df):
            controller.call_coltype([])
        args = mock_session.console.print.call_args[0][0]
        assert "Changed column" in args

    def test_category_with_categories(self, controller, mock_session, mock_result):
        df = pd.DataFrame({"C": ["x", "y", "z"]})
        ns = MagicMock()
        ns.column = "C"
        ns.dtype = "category"
        ns.categories = ["x", "y", "z"]
        ns.ordered = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=df):
            controller.call_coltype([])
        args = mock_session.console.print.call_args[0][0]
        assert "Changed column" in args

    def test_invalid_dtype(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.column = "A"
        ns.dtype = "not_a_real_type"
        ns.categories = None
        ns.ordered = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_coltype([])
        args = mock_session.console.print.call_args[0][0]
        assert "Error" in args


class TestCallAddcol:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_addcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_add_column(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.name = "D"
        ns.expression = ["A", "+", "B"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.to_dataframe.return_value = sample_df.copy()
        controller.call_addcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Added column" in args

    def test_invalid_expression(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.name = "D"
        ns.expression = ["nonexistent_col", "*", "2"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.to_dataframe.return_value = sample_df.copy()
        controller.call_addcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Error" in args


class TestCallDropcol:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_dropcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_drop_single_column(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.columns = ["C"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_dropcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Dropped" in args

    def test_drop_nonexistent(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.columns = ["ZZZ"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_dropcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Error" in args


class TestCallRenamecol:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_renamecol([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_rename_column(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.old_name = "A"
        ns.new_name = "Alpha"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_renamecol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Renamed" in args


class TestCallModifycol:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_modifycol([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_arithmetic_expression(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.name = "A"
        ns.expression = ["A", "*", "2"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_modifycol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Modified" in args

    def test_pandas_method(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.name = "C"
        ns.expression = ["str.upper()"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_modifycol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Modified" in args


class TestCallJoin:
    def test_no_table_selected(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_join([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_join_on_column(self, controller, mock_session, sample_df, mock_result):
        pd.DataFrame({"A": [1, 2], "D": [10, 20]})
        ns = MagicMock()
        ns.table = "0"
        ns.on = "A"
        ns.left_on = None
        ns.right_on = None
        ns.how = "inner"
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0

        mock_session.obbject_registry.all = {0: {"key": "prices"}}

        def get_side_effect(idx):
            return mock_result

        mock_session.obbject_registry.get.side_effect = get_side_effect

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_join([])
        mock_session.output_adapter.display.assert_called()

    def test_join_unknown_table(self, controller, mock_session):
        ns = MagicMock()
        ns.table = "unknown"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        controller.call_join([])
        args = mock_session.console.print.call_args[0][0]
        assert "not found" in args

    def test_join_with_save(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.table = "0"
        ns.on = None
        ns.left_on = None
        ns.right_on = None
        ns.how = "inner"
        ns.save = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        mock_session.obbject_registry.get.side_effect = None
        mock_session.obbject_registry.get.return_value = mock_result

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_join([])
        assert mock_result.results is not None


class TestCallCopy:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_copy([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_copy_success(self, controller, mock_session, sample_df, mock_result):
        ns = MagicMock()
        ns.name = "my_copy"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.register.return_value = True

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_copy([])
        mock_session.obbject_registry.register.assert_called_once()
        args = mock_session.console.print.call_args[0][0]
        assert "Copied" in args

    def test_copy_register_fails(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.name = "fail_copy"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.register.return_value = False

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_copy([])
        args = mock_session.console.print.call_args[0][0]
        assert "Failed" in args


class TestCallSave:
    def test_no_table(self, controller, mock_session):
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = None
        controller.call_save([])
        args = mock_session.console.print.call_args[0][0]
        assert "No table selected" in args

    def test_save_csv(self, controller, mock_session, sample_df, mock_result, tmp_path):
        ns = MagicMock()
        ns.filename = "test.csv"
        ns.index = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])
        assert (tmp_path / "test.csv").exists()
        args = mock_session.console.print.call_args[0][0]
        assert "Saved" in args

    def test_save_json(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "test.json"
        ns.index = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])
        assert (tmp_path / "test.json").exists()
        args = mock_session.console.print.call_args[0][0]
        assert "Saved" in args

    def test_save_unsupported_format(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "test.txt"
        ns.index = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])
        args = mock_session.console.print.call_args[0][0]
        assert "Unsupported" in args


class TestCallDelete:
    def test_unknown_table(self, controller, mock_session):
        ns = MagicMock()
        ns.index = "unknown"
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        controller.call_delete([])
        args = mock_session.console.print.call_args[0][0]
        assert "not found" in args

    def test_delete_current_table(self, controller, mock_session):
        ns = MagicMock()
        ns.index = "0"
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        controller.current_table = 0
        controller.call_delete([])
        assert controller.current_table is None
        mock_session.obbject_registry.remove.assert_called_once_with(0)

    def test_delete_other_table(self, controller, mock_session):
        ns = MagicMock()
        ns.index = "0"
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        controller.current_table = 1
        controller.call_delete([])
        assert controller.current_table == 1
        mock_session.obbject_registry.remove.assert_called_once_with(0)

    def test_delete_no_parser(self, controller, mock_session):
        """parse_known_args_and_warn returns None → no-op."""
        controller.parse_known_args_and_warn.return_value = None
        controller.call_delete([])
        mock_session.console.print.assert_not_called()


class TestCallQueryAdvanced:
    """Advanced call_query tests: SQLite push-down, result types, error hints."""

    def test_sqlite_optimization_simple_filter(
        self, controller, mock_session, sample_df, tmp_path
    ):
        """SQLite table with regex-matchable expression triggers SQL push-down."""
        import sqlite3

        from openbb_cli.controllers.utils import SQLiteTable

        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        sqlite_table = SQLiteTable(db_path=str(db_path), table_name="data", row_count=3)

        ns = MagicMock()
        ns.expression = ["df[df['A']", ">", "1]"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"results": sqlite_table}
        mock_session.obbject_registry.get.return_value = mock_result

        controller.call_query([])

        mock_session.output_adapter.display.assert_called()

    def test_sqlite_optimization_with_save(
        self, controller, mock_session, sample_df, tmp_path
    ):
        """SQLite push-down with --save stores result back."""
        import sqlite3

        from openbb_cli.controllers.utils import SQLiteTable

        db_path = tmp_path / "save.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        sqlite_table = SQLiteTable(db_path=str(db_path), table_name="data", row_count=3)

        ns = MagicMock()
        ns.expression = ["df[df['A']", "==", "1]"]
        ns.save = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"results": sqlite_table}
        mock_session.obbject_registry.get.return_value = mock_result

        controller.call_query([])

        assert mock_result.results is not None

    def test_sqlite_fallback_on_query_error(
        self, controller, mock_session, sample_df, tmp_path
    ):
        """When SQLite query() raises, falls back to pandas eval."""
        import sqlite3

        from openbb_cli.controllers.utils import SQLiteTable

        db_path = tmp_path / "fallback.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        sqlite_table = SQLiteTable(db_path=str(db_path), table_name="data", row_count=3)
        sqlite_table.query = MagicMock(side_effect=Exception("SQL error"))

        ns = MagicMock()
        ns.expression = ["df[df['A']", ">", "1]"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"results": sqlite_table}
        mock_session.obbject_registry.get.return_value = mock_result

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("SQL optimization failed" in c for c in console_calls)

    def test_series_result(self, controller, mock_session, sample_df, mock_result):
        """Expression returning a Series is displayed via to_frame()."""
        ns = MagicMock()
        ns.expression = ["df['A']"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        mock_session.output_adapter.display.assert_called()
        data = mock_session.output_adapter.display.call_args[1]["data"]
        assert isinstance(data, pd.DataFrame)

    def test_list_result(self, controller, mock_session, sample_df, mock_result):
        """Expression returning a list is wrapped in a DataFrame."""
        ns = MagicMock()
        ns.expression = ["df['A'].tolist()"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        mock_session.output_adapter.display.assert_called()

    def test_scalar_result(self, controller, mock_session, sample_df, mock_result):
        """Expression returning a scalar is printed directly."""
        ns = MagicMock()
        ns.expression = ["df['A'].sum()"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Result" in c for c in console_calls)

    def test_name_error_hint(self, controller, mock_session, sample_df, mock_result):
        """NameError triggers 'is not defined' hint message."""
        ns = MagicMock()
        ns.expression = ["some_undefined_var"]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("is not defined" in c or "Hint" in c for c in console_calls)

    def test_syntax_error_hint(self, controller, mock_session, sample_df, mock_result):
        """SyntaxError triggers 'invalid syntax' hint message."""
        ns = MagicMock()
        ns.expression = ["df["]
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("error" in c.lower() for c in console_calls)

    def test_dataframe_save_with_row_count_message(
        self, controller, mock_session, sample_df, mock_result
    ):
        """Saving a filtered DataFrame prints the row count message."""
        ns = MagicMock()
        ns.expression = ["df[df['A']", ">", "1]"]
        ns.save = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.model_dump.return_value = {"results": sample_df}

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("rows" in c.lower() or "updated" in c.lower() for c in console_calls)


class TestCallSaveAdvanced:
    """Advanced call_save tests: Excel, SQLite modes."""

    def test_save_excel(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "test.xlsx"
        ns.index = False
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with (
            patch(f"{MODULE}.extract_dataframe", return_value=sample_df),
            patch("openbb_cli.controllers.utils.save_to_excel") as mock_save,
        ):
            controller.call_save([])
            mock_save.assert_called_once()
        args = mock_session.console.print.call_args[0][0]
        assert "Saved" in args

    def test_save_excel_with_sheet_name(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "test.xlsx"
        ns.index = False
        ns.sheet_name = "MySheet"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with (
            patch(f"{MODULE}.extract_dataframe", return_value=sample_df),
            patch("openbb_cli.controllers.utils.save_to_excel") as mock_save,
        ):
            controller.call_save([])
            call_kwargs = mock_save.call_args[1]
            assert call_kwargs["sheet_name"] == "MySheet"

    def test_save_sqlite_new_db(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "test.db"
        ns.index = False
        ns.table = None
        ns.mode = "replace"
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])

        assert (tmp_path / "test.db").exists()
        args = mock_session.console.print.call_args[0][0]
        assert "Created new database" in args

    def test_save_sqlite_replace(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        import sqlite3

        db_path = tmp_path / "existing.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        ns = MagicMock()
        ns.filename = "existing.db"
        ns.index = False
        ns.table = None
        ns.mode = "replace"
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Replacing" in c for c in console_calls)

    def test_save_sqlite_append(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        import sqlite3

        db_path = tmp_path / "append.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        ns = MagicMock()
        ns.filename = "append.db"
        ns.index = False
        ns.table = None
        ns.mode = "append"
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Appending" in c or "Appended" in c for c in console_calls)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM data")
        assert cursor.fetchone()[0] == 6
        conn.close()

    def test_save_sqlite_fail_mode(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        import sqlite3

        db_path = tmp_path / "fail.db"
        conn = sqlite3.connect(db_path)
        sample_df.to_sql("data", conn, index=False)
        conn.close()

        ns = MagicMock()
        ns.filename = "fail.db"
        ns.index = False
        ns.table = None
        ns.mode = "fail"
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])

        args = mock_session.console.print.call_args[0][0]
        assert "already exists" in args

    def test_save_sqlite_custom_table_name(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "custom.db"
        ns.index = False
        ns.table = "my_table"
        ns.mode = "replace"
        ns.sheet_name = None
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_save([])

        import sqlite3

        conn = sqlite3.connect(tmp_path / "custom.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='my_table'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_save_exception(
        self, controller, mock_session, sample_df, mock_result, tmp_path
    ):
        ns = MagicMock()
        ns.filename = "fail.csv"
        ns.index = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.user.preferences.data_directory = str(tmp_path)

        with (
            patch(f"{MODULE}.extract_dataframe", return_value=sample_df),
            patch.object(sample_df, "to_csv", side_effect=OSError("disk full")),
        ):
            controller.call_save([])

        args = mock_session.console.print.call_args[0][0]
        assert "Error" in args


class TestCallJoinAdvanced:
    def test_join_left_on_right_on(
        self, controller, mock_session, sample_df, mock_result
    ):
        df_right = pd.DataFrame({"X": [1, 2], "D": [10, 20]})
        ns = MagicMock()
        ns.table = "0"
        ns.on = None
        ns.left_on = "A"
        ns.right_on = "X"
        ns.how = "inner"
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        mock_session.obbject_registry.get.return_value = mock_result

        with patch(f"{MODULE}.extract_dataframe", side_effect=[sample_df, df_right]):
            controller.call_join([])

        mock_session.output_adapter.display.assert_called()

    def test_join_merge_exception(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.table = "0"
        ns.on = "NONEXISTENT_COL"
        ns.left_on = None
        ns.right_on = None
        ns.how = "inner"
        ns.save = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        mock_session.obbject_registry.get.return_value = mock_result

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_join([])

        args = mock_session.console.print.call_args[0][0]
        assert "error" in args.lower() or "Join error" in args

    def test_join_no_parser(self, controller, mock_session):
        """parse_known_args_and_warn returns None → no-op."""
        controller.parse_known_args_and_warn.return_value = None
        controller.call_join([])
        mock_session.console.print.assert_not_called()

    def test_join_default_index_join(
        self, controller, mock_session, sample_df, mock_result
    ):
        """No --on, --left-on, --right-on → default index-based join."""
        ns = MagicMock()
        ns.table = "0"
        ns.on = None
        ns.left_on = None
        ns.right_on = None
        ns.how = "inner"
        ns.save = True
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        mock_session.obbject_registry.get.return_value = mock_result

        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_join([])

        console_calls = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Join result" in c for c in console_calls)
        assert any("updated" in c.lower() for c in console_calls)


class TestPrintHelp:
    def test_print_help_no_table_selected(self, controller, mock_session):
        controller.current_table = None
        controller.print_help()
        mock_session.console.print.assert_called_once()

    def test_print_help_with_table_selected(
        self, controller, mock_session, sample_df, mock_result
    ):
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "my_data"}}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.print_help()
        call_kwargs = mock_session.console.print.call_args[1]
        text = call_kwargs.get("text", "")
        assert "my_data" in text
        assert "A, B, C" in text

    def test_print_help_table_info_exception(self, controller, mock_session):
        controller.current_table = 0
        mock_session.obbject_registry.get.side_effect = Exception("bad")
        controller.print_help()
        mock_session.console.print.assert_called_once()
        call_kwargs = mock_session.console.print.call_args[1]
        text = call_kwargs.get("text", "")
        assert "Selected table" in text

    def test_print_help_table_no_key(
        self, controller, mock_session, sample_df, mock_result
    ):
        """Table with no register_key uses 'Table N' as name."""
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": ""}}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.print_help()
        call_kwargs = mock_session.console.print.call_args[1]
        text = call_kwargs.get("text", "")
        assert "Table 0" in text


class TestChoicesDefault:
    def test_all_commands_present(self, controller, mock_session, sample_df):
        """choices_default contains all CHOICES_COMMANDS keys."""
        controller.current_table = None
        mock_session.obbject_registry.all = {}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            choices = controller.choices_default
        for cmd in [
            "list",
            "select",
            "info",
            "view",
            "query",
            "colname",
            "coltype",
            "addcol",
            "dropcol",
            "renamecol",
            "modifycol",
            "join",
            "copy",
            "save",
            "delete",
            "results",
            "load",
        ]:
            assert cmd in choices

    def test_dynamic_column_completions(self, controller, mock_session, sample_df):
        """When a table is selected, column names populate completions."""
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "prices"}}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            choices = controller.choices_default
        assert "A" in choices["query"]
        assert "B" in choices["query"]

    def test_dynamic_table_completions(self, controller, mock_session, sample_df):
        """Table indices populate select/delete/join/results completions."""
        controller.current_table = None
        mock_session.obbject_registry.all = {0: {"key": "prices"}, 1: {"key": "vol"}}
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            choices = controller.choices_default
        assert "prices" in choices["select"]
        assert "vol" in choices["select"]
        assert "prices" in choices["delete"]


class TestMiscEdgeCases:
    def test_modifycol_error_path(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.name = "A"
        ns.expression = ["invalid_method_xyz()"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_modifycol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Error" in args

    def test_select_numeric_int_index(
        self, controller, mock_session, sample_df, mock_result
    ):
        """Select by numeric string (e.g. '0') tries int lookup."""
        ns = MagicMock()
        ns.index = "0"
        mock_result.extra = {"register_key": ""}
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.get.return_value = mock_result
        mock_session.obbject_registry.obbjects = [mock_result]
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_select([])
        mock_session.console.print.assert_called()
        args = mock_session.console.print.call_args[0][0]
        assert "Selected" in args

    def test_dropcol_multiple_columns(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.columns = ["A", "B"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_dropcol([])
        args = mock_session.console.print.call_args[0][0]
        assert "Dropped" in args
        assert "A" in args and "B" in args

    def test_coltype_simple_category(self, controller, mock_session, mock_result):
        """Category conversion without explicit --categories."""
        df = pd.DataFrame({"C": ["x", "y", "z"]})
        ns = MagicMock()
        ns.column = "C"
        ns.dtype = "category"
        ns.categories = None
        ns.ordered = False
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=df):
            controller.call_coltype([])
        args = mock_session.console.print.call_args[0][0]
        assert "Changed column" in args

    def test_addcol_calls_update_completer(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.name = "D"
        ns.expression = ["A", "+", "B"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_result.to_dataframe.return_value = sample_df.copy()
        controller.call_addcol([])
        controller.update_completer.assert_called()

    def test_list_with_result_returning_none(self, controller, mock_session, sample_df):
        """Registry has entries but get() returns None for all."""
        ns = MagicMock()
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.all = {0: {"key": "a"}, 1: {"key": "b"}}
        mock_session.obbject_registry.get.return_value = None
        controller.call_list([])
        args = mock_session.console.print.call_args[0][0]
        assert "No dataframes" in args

    def test_renamecol_calls_update_completer(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.old_name = "A"
        ns.new_name = "Alpha"
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_renamecol([])
        controller.update_completer.assert_called()

    def test_dropcol_calls_update_completer(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock()
        ns.columns = ["C"]
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_dropcol([])
        controller.update_completer.assert_called()

    def test_query_no_parser(self, controller, mock_session):
        """parse_known_args_and_warn returns None → early return."""
        controller.parse_known_args_and_warn.return_value = None
        controller.call_query([])
        mock_session.console.print.assert_not_called()

    def test_select_no_parser(self, controller, mock_session):
        controller.parse_known_args_and_warn.return_value = None
        controller.call_select([])
        mock_session.console.print.assert_not_called()

    def test_info_no_parser(self, controller, mock_session):
        controller.parse_known_args_and_warn.return_value = None
        controller.call_info([])
        mock_session.console.print.assert_not_called()


class TestResultIsNoneEarlyReturns:
    """Each ``call_*`` method has a ``result is None: return`` guard after
    ``session.obbject_registry.get(self.current_table)``. Trigger it by
    setting ``current_table`` to a non-None value AND making the registry
    return ``None`` from ``.get``.
    """

    def _setup(self, controller, mock_session, ns):
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.get.return_value = None
        mock_session.output_adapter.display.reset_mock()

    def test_info_result_none(self, controller, mock_session):
        self._setup(controller, mock_session, MagicMock())
        controller.call_info([])
        mock_session.output_adapter.display.assert_not_called()

    def test_view_result_none(self, controller, mock_session):
        self._setup(controller, mock_session, MagicMock(head=None, tail=None))
        controller.call_view([])
        mock_session.output_adapter.display.assert_not_called()

    def test_query_result_none(self, controller, mock_session):
        ns = MagicMock(expression=["df.shape"], save=False)
        self._setup(controller, mock_session, ns)
        controller.call_query([])
        mock_session.output_adapter.display.assert_not_called()

    def test_colname_result_none(self, controller, mock_session):
        self._setup(controller, mock_session, MagicMock())
        controller.call_colname([])
        mock_session.output_adapter.display.assert_not_called()

    def test_coltype_result_none(self, controller, mock_session):
        ns = MagicMock(column="A", dtype="int", categories=None, ordered=False)
        self._setup(controller, mock_session, ns)
        controller.call_coltype([])
        mock_session.output_adapter.display.assert_not_called()

    def test_addcol_result_none(self, controller, mock_session):
        ns = MagicMock(name="X", expression=["1"])
        self._setup(controller, mock_session, ns)
        controller.call_addcol([])
        mock_session.output_adapter.display.assert_not_called()

    def test_dropcol_result_none(self, controller, mock_session):
        ns = MagicMock(columns=["A"])
        self._setup(controller, mock_session, ns)
        controller.call_dropcol([])
        mock_session.output_adapter.display.assert_not_called()

    def test_renamecol_result_none(self, controller, mock_session):
        ns = MagicMock(old_name="A", new_name="X")
        self._setup(controller, mock_session, ns)
        controller.call_renamecol([])
        mock_session.output_adapter.display.assert_not_called()

    def test_modifycol_result_none(self, controller, mock_session):
        ns = MagicMock(name="A", expression=["1"])
        self._setup(controller, mock_session, ns)
        controller.call_modifycol([])
        mock_session.output_adapter.display.assert_not_called()

    def test_copy_result_none(self, controller, mock_session):
        ns = MagicMock(name="copy_target")
        self._setup(controller, mock_session, ns)
        controller.call_copy([])
        mock_session.obbject_registry.register.assert_not_called()

    def test_save_result_none(self, controller, mock_session, tmp_path):
        ns = MagicMock(
            filename="x.csv", index=False, table=None, mode="replace", sheet_name=None
        )
        self._setup(controller, mock_session, ns)
        mock_session.user.preferences.data_directory = str(tmp_path)
        controller.call_save([])
        assert not (tmp_path / "x.csv").exists()


class TestQueryRareBranches:
    """Branches in ``call_query`` we couldn't otherwise hit: SQL value handling,
    iterable result types, and the ``invalid syntax`` hint.
    """

    def test_sql_value_quoted_string_passes_through(
        self, controller, mock_session, sample_df, mock_result
    ):
        """Filter expression like ``col == 'x'`` keeps the literal quoted."""
        from openbb_cli.controllers.utils import SQLiteTable

        sqlite_tbl = MagicMock(spec=SQLiteTable)
        sqlite_tbl.query.return_value = pd.DataFrame({"a": [1]})
        mock_result.model_dump.return_value = {"results": sqlite_tbl}
        ns = MagicMock(expression=["df[df['REF_AREA'] == 'CHE']"], save=False)
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.get.return_value = mock_result
        controller.call_query([])
        sqlite_tbl.query.assert_called_once()
        where = sqlite_tbl.query.call_args[1]["where"]
        assert "'CHE'" in where

    def test_sql_value_literal_eval_returns_string(
        self, controller, mock_session, sample_df, mock_result
    ):
        """``ast.literal_eval`` returns a non-numeric string → wrap in quotes."""
        from openbb_cli.controllers.utils import SQLiteTable

        sqlite_tbl = MagicMock(spec=SQLiteTable)
        sqlite_tbl.query.return_value = pd.DataFrame({"a": [1]})
        mock_result.model_dump.return_value = {"results": sqlite_tbl}
        ns = MagicMock(expression=["df[df['flag'] == True]"], save=False)
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.get.return_value = mock_result
        controller.call_query([])
        where = sqlite_tbl.query.call_args[1]["where"]
        assert "'True'" in where

    def test_sql_value_literal_eval_raises_falls_back_to_string(
        self, controller, mock_session, sample_df, mock_result
    ):
        """``ast.literal_eval`` raising → wrap raw value in quotes."""
        from openbb_cli.controllers.utils import SQLiteTable

        sqlite_tbl = MagicMock(spec=SQLiteTable)
        sqlite_tbl.query.return_value = pd.DataFrame({"a": [1]})
        mock_result.model_dump.return_value = {"results": sqlite_tbl}
        ns = MagicMock(expression=["df[df['REF_AREA'] == CHE]"], save=False)
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.get.return_value = mock_result
        controller.call_query([])
        where = sqlite_tbl.query.call_args[1]["where"]
        assert "'CHE'" in where

    def test_query_returns_iterable_array(
        self, controller, mock_session, sample_df, mock_result
    ):
        """``df.values`` returns numpy array → iterable branch."""
        ns = MagicMock(expression=["df.values.flatten()"], save=False)
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])
        mock_session.output_adapter.display.assert_called()

    def test_query_invalid_syntax_emits_hint(
        self, controller, mock_session, sample_df, mock_result
    ):
        """A syntactically invalid expression triggers the ``invalid syntax`` hint."""
        ns = MagicMock(expression=["1", "+"], save=False)
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_query([])
        msgs = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Valid query examples" in m for m in msgs)


class TestSelectIntFallback:
    """``call_select`` falls back to int(index) lookup when the string lookup
    misses."""

    def test_select_string_miss_int_hit(
        self, controller, mock_session, mock_result, sample_df
    ):
        ns = MagicMock(index="0")
        controller.parse_known_args_and_warn.return_value = ns

        def get(arg):
            return mock_result if isinstance(arg, int) else None

        mock_session.obbject_registry.get.side_effect = get
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df):
            controller.call_select([])
        assert mock_session.obbject_registry.get.call_count >= 2


class TestDeleteUnknownIndex:
    """``call_delete`` warns when the resolved index isn't actually present
    in ``obbject_registry.all``."""

    def test_delete_resolved_but_not_in_registry(self, controller, mock_session):
        ns = MagicMock(index="0")
        controller.parse_known_args_and_warn.return_value = ns
        mock_session.obbject_registry.all = {}
        with patch.object(controller, "_resolve_table_identifier", return_value=0):
            controller.call_delete([])
        msgs = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("not found" in m for m in msgs)


class TestJoinResultMissing:
    """When the resolved-but-evicted right-side result is None, ``call_join``
    short-circuits silently."""

    def test_join_with_missing_right(self, controller, mock_session, mock_result):
        ns = MagicMock(
            table="0", on=None, left_on=None, right_on=None, how="inner", save=False
        )
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {0: {"key": "x"}}

        mock_session.obbject_registry.get.side_effect = [mock_result, None]
        controller.call_join([])
        mock_session.output_adapter.display.assert_not_called()

    def test_join_resolved_idx_not_in_registry_all(self, controller, mock_session):
        """``_resolve_table_identifier`` returns an index, but ``registry.all`` is
        missing it → red 'not found' warning."""
        ns = MagicMock(
            table="0", on=None, left_on=None, right_on=None, how="inner", save=False
        )
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        mock_session.obbject_registry.all = {}
        with patch.object(controller, "_resolve_table_identifier", return_value=0):
            controller.call_join([])
        msgs = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("not found" in m for m in msgs)


class TestRenameColumnError:
    """Exception inside the rename ``try`` is caught and reported."""

    def test_rename_failure_emits_error_message(
        self, controller, mock_session, sample_df, mock_result
    ):
        ns = MagicMock(old_name="A", new_name="X")
        controller.parse_known_args_and_warn.return_value = ns
        controller.current_table = 0
        controller.update_completer.side_effect = RuntimeError("synthetic")
        with patch(f"{MODULE}.extract_dataframe", return_value=sample_df.copy()):
            controller.call_renamecol([])
        msgs = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("Error renaming column" in m for m in msgs)
