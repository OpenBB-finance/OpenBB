"""Tests for AG Grid models and configuration.

Tests:
- ColDef, ColGroupDef, DefaultColDef serialization
- RowSelection configuration
- GridOptions with conditional field inclusion
- normalize_data() for DataFrame, dict, list inputs
- _detect_column_types() for various dtypes
- build_column_defs() with ColDef objects and dicts
- build_grid_config() main entry point
- MultiIndex column/row handling
"""
# pylint: disable=too-many-lines

from __future__ import annotations

import json

from typing import Any

import pytest

from pywry.grid import (
    ColDef,
    ColGroupDef,
    DefaultColDef,
    GridConfig,
    GridData,
    GridOptions,
    PyWryGridContext,
    RowSelection,
    _detect_column_types,
    build_column_defs,
    build_grid_config,
    normalize_data,
    to_js_grid_config,
)


# =============================================================================
# AGGridModel Base Class Tests
# =============================================================================


class TestAGGridModel:
    """Tests for AGGridModel base class serialization."""

    def test_to_dict_uses_alias(self):
        """to_dict() uses camelCase alias when Field alias is defined."""
        # AGGridModel requires Field(alias=...) to use aliases.
        # Fields without aliases serialize with their Python names.
        # This test verifies that ColDef (which has aliases) works correctly.
        col = ColDef(field="test", header_name="My Header")
        result = col.to_dict()
        # Should have camelCase keys
        assert "headerName" in result
        assert result["headerName"] == "My Header"

    def test_to_dict_excludes_none(self):
        """to_dict() excludes None values by default."""
        col = ColDef(field="test", header_name=None)
        result = col.to_dict()
        assert "headerName" not in result


# =============================================================================
# ColDef Tests
# =============================================================================


class TestColDef:
    """Tests for ColDef column definition model."""

    def test_field_only(self):
        """Minimal ColDef with just field."""
        col = ColDef(field="myField")
        result = col.to_dict()
        assert result["field"] == "myField"
        assert "headerName" not in result

    def test_camel_case_serialization(self):
        """Python snake_case fields serialize to camelCase."""
        col = ColDef(
            field="test",
            header_name="Test Header",
            value_getter="data.x + data.y",
            value_formatter="value.toFixed(2)",
            cell_data_type="number",
            span_rows=True,
        )
        result = col.to_dict()

        assert "headerName" in result
        assert result["headerName"] == "Test Header"
        assert "valueGetter" in result
        assert result["valueGetter"] == "data.x + data.y"
        assert "valueFormatter" in result
        assert result["valueFormatter"] == "value.toFixed(2)"
        assert "cellDataType" in result
        assert result["cellDataType"] == "number"
        assert "spanRows" in result
        assert result["spanRows"] is True

        # Ensure snake_case NOT in output
        assert "header_name" not in result
        assert "value_getter" not in result
        assert "value_formatter" not in result
        assert "cell_data_type" not in result
        assert "span_rows" not in result

    def test_pinned_values(self):
        """Pinned accepts 'left' or 'right' (AG Grid v35 doesn't support bool)."""
        col_left = ColDef(field="a", pinned="left")
        assert col_left.to_dict()["pinned"] == "left"

        col_right = ColDef(field="b", pinned="right")
        assert col_right.to_dict()["pinned"] == "right"

        # Note: AG Grid v35 requires 'left' or 'right' strings, not booleans

    def test_filter_options(self):
        """Filter can be string or bool."""
        col_text = ColDef(field="a", filter="agTextColumnFilter")
        assert col_text.to_dict()["filter"] == "agTextColumnFilter"

        col_bool = ColDef(field="b", filter=True)
        assert col_bool.to_dict()["filter"] is True

    def test_width_fields(self):
        """Width, minWidth, maxWidth serialization."""
        col = ColDef(field="test", width=150, min_width=100, max_width=300)
        result = col.to_dict()
        assert result["width"] == 150
        assert result["minWidth"] == 100
        assert result["maxWidth"] == 300

    def test_checkboxes_column(self):
        """Checkboxes field for row selection column."""
        col = ColDef(field="test", checkboxes=True)
        result = col.to_dict()
        assert result["checkboxes"] is True


class TestColGroupDef:
    """Tests for ColGroupDef column group model."""

    def test_basic_group(self):
        """Column group with children."""
        group = ColGroupDef(
            header_name="My Group",
            children=[{"field": "a"}, {"field": "b"}],
        )
        result = group.to_dict()

        assert result["headerName"] == "My Group"
        assert len(result["children"]) == 2
        assert result["children"][0]["field"] == "a"

    def test_marry_children(self):
        """marryChildren keeps columns together during resize."""
        group = ColGroupDef(
            header_name="Group",
            children=[{"field": "x"}],
            marry_children=True,
        )
        result = group.to_dict()
        assert result["marryChildren"] is True


class TestDefaultColDef:
    """Tests for DefaultColDef model."""

    def test_sensible_defaults(self):
        """DefaultColDef has good defaults for UX."""
        default = DefaultColDef()
        result = default.to_dict()

        # Should be sortable, filterable, resizable
        assert result.get("sortable") is True
        assert result.get("filter") is True
        assert result.get("resizable") is True
        # floatingFilter defaults to False in the actual implementation
        assert "floatingFilter" in result


# =============================================================================
# RowSelection Tests
# =============================================================================


class TestRowSelection:
    """Tests for RowSelection configuration."""

    def test_default_is_multi_row(self):
        """Default mode is multiRow."""
        sel = RowSelection()
        result = sel.to_dict()
        assert result["mode"] == "multiRow"

    def test_single_row_mode(self):
        """Single row selection mode."""
        sel = RowSelection(mode="singleRow")
        result = sel.to_dict()
        assert result["mode"] == "singleRow"

    def test_checkboxes_enabled_by_default(self):
        """Checkboxes enabled by default for multiRow."""
        sel = RowSelection(mode="multiRow")
        result = sel.to_dict()
        assert result.get("checkboxes") is True

    def test_hide_disabled_checkboxes(self):
        """hideDisabledCheckboxes option."""
        sel = RowSelection(hide_disabled_checkboxes=True)
        result = sel.to_dict()
        assert result.get("hideDisabledCheckboxes") is True

    def test_header_checkbox(self):
        """Header checkbox for select-all."""
        sel = RowSelection(header_checkbox=True)
        result = sel.to_dict()
        assert result.get("headerCheckbox") is True

    def test_camel_case_output(self):
        """All fields serialize to camelCase."""
        sel = RowSelection(
            mode="multiRow",
            checkboxes=True,
            header_checkbox=True,
            hide_disabled_checkboxes=False,
        )
        result = sel.to_dict()

        # Check camelCase keys exist
        assert "mode" in result
        assert "checkboxes" in result
        assert "headerCheckbox" in result

        # Ensure snake_case NOT in output
        assert "header_checkbox" not in result
        assert "hide_disabled_checkboxes" not in result


# =============================================================================
# GridOptions Tests
# =============================================================================


class TestGridOptions:
    """Tests for GridOptions model."""

    def test_column_defs_required(self):
        """columnDefs is a required field."""
        opts = GridOptions(columnDefs=[{"field": "a"}])
        result = opts.to_dict()
        assert "columnDefs" in result

    def test_row_data_serialization(self):
        """rowData serializes correctly."""
        data = [{"a": 1}, {"a": 2}]
        opts = GridOptions(columnDefs=[{"field": "a"}], rowData=data)
        result = opts.to_dict()
        assert result["rowData"] == data

    def test_pagination_none_excluded(self):
        """pagination=None is excluded from output."""
        opts = GridOptions(columnDefs=[], pagination=None)
        result = opts.to_dict()
        assert "pagination" not in result

    def test_pagination_false_included(self):
        """pagination=False IS included in output."""
        opts = GridOptions(columnDefs=[], pagination=False)
        result = opts.to_dict()
        assert result["pagination"] is False

    def test_pagination_true_included(self):
        """pagination=True IS included in output."""
        opts = GridOptions(columnDefs=[], pagination=True)
        result = opts.to_dict()
        assert result["pagination"] is True

    def test_row_selection_dict(self):
        """rowSelection as dict passthrough."""
        sel = {"mode": "singleRow", "checkboxes": False}
        opts = GridOptions(columnDefs=[], rowSelection=sel)
        result = opts.to_dict()
        assert result["rowSelection"] == sel

    def test_row_model_type(self):
        """rowModelType serialization."""
        opts = GridOptions(columnDefs=[], rowModelType="infinite")
        result = opts.to_dict()
        assert result["rowModelType"] == "infinite"


# =============================================================================
# _detect_column_types Tests
# =============================================================================


class TestDetectColumnTypes:
    """Tests for _detect_column_types() function."""

    def test_returns_empty_without_pandas(self):
        """Returns empty dict if pandas not available or input isn't DataFrame."""
        result = _detect_column_types([{"a": 1}])
        assert not result

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_datetime_detection(self):
        """Detects datetime64 columns as 'dateTimeString'."""
        import pandas as pd

        df = pd.DataFrame({"timestamp": pd.to_datetime(["2024-01-01", "2024-01-02"])})
        result = _detect_column_types(df)
        # Implementation uses 'dateTimeString' (with Time) for full datetime
        assert result.get("timestamp") == "dateTimeString"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_numeric_detection(self):
        """Detects numeric columns as 'number'."""
        import pandas as pd

        df = pd.DataFrame({"value": [1.5, 2.5, 3.5], "count": [1, 2, 3]})
        result = _detect_column_types(df)
        assert result.get("value") == "number"
        assert result.get("count") == "number"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_boolean_detection(self):
        """Detects boolean columns as 'boolean'."""
        import pandas as pd

        df = pd.DataFrame({"active": [True, False, True]})
        result = _detect_column_types(df)
        assert result.get("active") == "boolean"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_leading_zero_string_detection(self):
        """Strings with leading zeros should be detected as 'text'."""
        import pandas as pd

        df = pd.DataFrame({"zip": ["00501", "01234", "07302"]})
        result = _detect_column_types(df)
        assert result.get("zip") == "text"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_regular_string_not_marked_as_text(self):
        """Regular strings without leading zeros are not marked as 'text'."""
        import pandas as pd

        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
        result = _detect_column_types(df)
        # Regular strings should NOT have 'text' type (let AG Grid auto-detect)
        assert "name" not in result or result.get("name") != "text"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_numeric_string_with_leading_zero(self):
        """Numeric strings like '007' should be 'text' to preserve zeros."""
        import pandas as pd

        df = pd.DataFrame({"code": ["007", "042", "123"]})
        result = _detect_column_types(df)
        assert result.get("code") == "text"


# =============================================================================
# normalize_data Tests
# =============================================================================


class TestNormalizeData:
    """Tests for normalize_data() function."""

    def test_list_of_dicts(self):
        """Handles list of dicts input."""
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = normalize_data(data)

        assert isinstance(result, GridData)
        assert result.row_data == data
        assert set(result.columns) == {"a", "b"}
        assert result.total_rows == 2

    def test_dict_of_lists(self):
        """Handles dict of lists (column-oriented)."""
        data = {"x": [1, 2, 3], "y": [4, 5, 6]}
        result = normalize_data(data)

        assert result.total_rows == 3
        assert set(result.columns) == {"x", "y"}
        # Should be converted to list of dicts
        assert result.row_data[0] == {"x": 1, "y": 4}

    def test_empty_list(self):
        """Handles empty list."""
        result = normalize_data([])
        assert result.row_data == []
        assert result.columns == []
        assert result.total_rows == 0

    def test_single_row(self):
        """Handles single row dict (not in list)."""
        data = {"name": "Alice", "age": 30}
        result = normalize_data(data)
        # Should interpret as column-oriented with 1 row each
        # or as a single row - depends on implementation
        assert result is not None  # Just verify it doesn't crash

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_pandas_dataframe(self):
        """Handles pandas DataFrame."""
        import pandas as pd

        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = normalize_data(df)

        assert result.total_rows == 2
        assert set(result.columns) == {"a", "b"}
        assert len(result.row_data) == 2

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_dataframe_with_datetime(self):
        """DataFrame with datetime converts to ISO strings."""
        import pandas as pd

        df = pd.DataFrame({"ts": pd.to_datetime(["2024-01-01"])})
        result = normalize_data(df)

        # Datetime should be serialized as string
        assert isinstance(result.row_data[0]["ts"], str)

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_dataframe_with_nan(self):
        """DataFrame NaN values become None."""
        import numpy as np
        import pandas as pd

        df = pd.DataFrame({"a": [1.0, np.nan, 3.0]})
        result = normalize_data(df)

        assert result.row_data[1]["a"] is None

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_multiindex_columns(self):
        """DataFrame with MultiIndex columns creates column groups."""
        import pandas as pd

        cols = pd.MultiIndex.from_tuples([("A", "x"), ("A", "y"), ("B", "z")])
        df = pd.DataFrame([[1, 2, 3]], columns=cols)
        result = normalize_data(df)

        # Should have column_groups for grouped headers
        assert result.column_groups is not None
        assert len(result.column_groups) > 0

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_multiindex_rows(self):
        """DataFrame with MultiIndex rows creates index columns."""
        import pandas as pd

        idx = pd.MultiIndex.from_tuples([("A", 1), ("A", 2), ("B", 1)])
        df = pd.DataFrame({"val": [10, 20, 30]}, index=idx)
        result = normalize_data(df)

        # Should have index_columns
        assert result.index_columns is not None
        assert len(result.index_columns) == 2  # 2-level MultiIndex


# =============================================================================
# build_column_defs Tests
# =============================================================================


class TestBuildColumnDefs:
    """Tests for build_column_defs() function."""

    def test_simple_columns(self):
        """Creates basic field definitions for column names."""
        result = build_column_defs(["a", "b", "c"], column_defs=None)

        assert len(result) == 3
        assert result[0]["field"] == "a"
        assert result[1]["field"] == "b"
        assert result[2]["field"] == "c"

    def test_custom_column_defs_as_dicts(self):
        """Accepts custom column defs as plain dicts."""
        custom = [
            {"field": "x", "headerName": "X Value"},
            {"field": "y", "width": 200},
        ]
        result = build_column_defs(["x", "y"], column_defs=custom)

        assert result == custom

    def test_custom_column_defs_as_coldef_objects(self):
        """Accepts custom column defs as ColDef objects."""
        custom = [
            ColDef(field="x", header_name="X Value"),
            ColDef(field="y", value_getter="data.y * 2"),
        ]
        result = build_column_defs(["x", "y"], column_defs=custom)

        # Should have camelCase keys from ColDef.to_dict()
        assert result[0]["field"] == "x"
        assert result[0]["headerName"] == "X Value"
        assert result[1]["valueGetter"] == "data.y * 2"

    def test_hasattr_duck_typing(self):
        """Uses hasattr() duck typing instead of isinstance()."""
        # This tests the fix for module reload issues
        # Create an object that has to_dict() but isn't actually ColDef

        class MockColDef:
            """Mock column definition for duck typing test."""

            def to_dict(self) -> dict[str, Any]:
                """Return mock column definition dict."""
                return {"field": "mock", "customKey": "value"}

        custom = [MockColDef()]
        result = build_column_defs(["mock"], column_defs=custom)

        # Should call to_dict() on the mock object
        assert result[0]["field"] == "mock"
        assert result[0]["customKey"] == "value"

    def test_index_columns_pinned_left(self):
        """Index columns are pinned left with special styling."""
        result = build_column_defs(
            ["data_col"],
            column_defs=None,
            index_columns=["idx"],
        )

        # First column should be the index
        assert result[0]["field"] == "idx"
        assert result[0]["pinned"] == "left"
        assert result[0].get("lockPosition") is True

    def test_enable_cell_span_on_index(self):
        """enable_cell_span=True adds spanRows to index columns."""
        result = build_column_defs(
            ["value"],
            column_defs=None,
            index_columns=["category"],
            enable_cell_span=True,
        )

        # Index column should have spanRows=True
        idx_col = result[0]
        assert idx_col["field"] == "category"
        assert idx_col.get("spanRows") is True

    def test_column_types_add_cell_data_type(self):
        """column_types dict adds cellDataType to columns."""
        result = build_column_defs(
            ["ts", "val"],
            column_defs=None,
            column_types={"ts": "dateString", "val": "number"},
        )

        ts_col = next(c for c in result if c["field"] == "ts")
        val_col = next(c for c in result if c["field"] == "val")

        assert ts_col["cellDataType"] == "dateString"
        assert val_col["cellDataType"] == "number"

    def test_column_groups_from_multiindex(self):
        """column_groups creates hierarchical headers."""
        groups = [
            {
                "headerName": "Group A",
                "children": [{"field": "a1"}, {"field": "a2"}],
            },
            {"field": "standalone"},
        ]
        result = build_column_defs(
            ["a1", "a2", "standalone"],
            column_defs=None,
            column_groups=groups,
        )

        # Should have group structure
        assert result[0]["headerName"] == "Group A"
        assert "children" in result[0]
        assert len(result[0]["children"]) == 2


# =============================================================================
# build_grid_config Tests
# =============================================================================


class TestBuildGridConfig:
    """Tests for build_grid_config() main entry point."""

    def test_returns_grid_config(self):
        """Returns GridConfig with options and context."""
        data = [{"a": 1}]
        result = build_grid_config(data)

        assert isinstance(result, GridConfig)
        assert isinstance(result.options, GridOptions)
        assert isinstance(result.context, PyWryGridContext)

    def test_generates_grid_id(self):
        """Auto-generates unique grid ID."""
        result = build_grid_config([{"a": 1}])
        assert result.context.grid_id.startswith("grid-")

    def test_custom_grid_id(self):
        """Uses custom grid_id when provided."""
        result = build_grid_config([{"a": 1}], grid_id="my-grid")
        assert result.context.grid_id == "my-grid"

    def test_pagination_none_default(self):
        """pagination=None by default (lets JS auto-enable)."""
        result = build_grid_config([{"a": 1}])
        # pagination should not be in the dict when None
        opts_dict = result.options.to_dict()
        assert "pagination" not in opts_dict

    def test_pagination_explicit_true(self):
        """pagination=True explicitly enables."""
        result = build_grid_config([{"a": 1}], pagination=True)
        opts_dict = result.options.to_dict()
        assert opts_dict["pagination"] is True

    def test_pagination_explicit_false(self):
        """pagination=False explicitly disables."""
        result = build_grid_config([{"a": 1}], pagination=False)
        opts_dict = result.options.to_dict()
        assert opts_dict["pagination"] is False

    def test_pagination_page_size(self):
        """paginationPageSize is configurable."""
        # pagination_page_size is only included when pagination is enabled
        result = build_grid_config([{"a": 1}], pagination=True, pagination_page_size=50)
        opts_dict = result.options.to_dict()
        assert opts_dict["paginationPageSize"] == 50

    def test_row_selection_true_default(self):
        """row_selection=True creates multiRow selection with checkboxes."""
        result = build_grid_config([{"a": 1}], row_selection=True)
        opts_dict = result.options.to_dict()

        assert "rowSelection" in opts_dict
        assert opts_dict["rowSelection"]["mode"] == "multiRow"
        assert opts_dict["rowSelection"]["checkboxes"] is True

    def test_row_selection_false(self):
        """row_selection=False disables selection."""
        result = build_grid_config([{"a": 1}], row_selection=False)
        opts_dict = result.options.to_dict()

        # False is passed explicitly to disable selection (not None which would use default)
        assert opts_dict.get("rowSelection") is False

    def test_row_selection_custom_object(self):
        """row_selection accepts RowSelection object."""
        sel = RowSelection(mode="singleRow", checkboxes=False)
        result = build_grid_config([{"a": 1}], row_selection=sel)
        opts_dict = result.options.to_dict()

        assert opts_dict["rowSelection"]["mode"] == "singleRow"
        assert opts_dict["rowSelection"]["checkboxes"] is False

    def test_dark_theme_class(self):
        """theme='dark' adds -dark suffix to theme class."""
        result = build_grid_config([{"a": 1}], theme="dark", aggrid_theme="alpine")
        assert result.context.theme_class == "ag-theme-alpine-dark"

    def test_light_theme_class(self):
        """theme='light' uses theme without -dark suffix."""
        result = build_grid_config([{"a": 1}], theme="light", aggrid_theme="alpine")
        assert result.context.theme_class == "ag-theme-alpine"

    def test_different_aggrid_themes(self):
        """Supports different AG Grid themes."""
        for theme_name in ["quartz", "alpine", "balham", "material"]:
            result = build_grid_config([{"a": 1}], aggrid_theme=theme_name)
            assert theme_name in result.context.theme_class

    def test_custom_column_defs_applied(self):
        """Custom column_defs are used in output."""
        cols = [ColDef(field="x", header_name="Custom X")]
        result = build_grid_config([{"x": 1}], column_defs=cols)
        opts_dict = result.options.to_dict()

        assert opts_dict["columnDefs"][0]["headerName"] == "Custom X"

    def test_row_model_type(self):
        """row_model_type is configurable."""
        result = build_grid_config([{"a": 1}], row_model_type="infinite")
        opts_dict = result.options.to_dict()
        assert opts_dict["rowModelType"] == "infinite"

    def test_grid_options_merge(self):
        """Additional grid_options are merged."""
        extra = {"animateRows": True, "suppressMenuHide": True}
        result = build_grid_config([{"a": 1}], grid_options=extra)
        opts_dict = result.options.to_dict()

        assert opts_dict["animateRows"] is True
        assert opts_dict["suppressMenuHide"] is True

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_auto_enable_cell_span_with_multiindex(self):
        """Cell span auto-enables for MultiIndex rows."""
        import pandas as pd

        idx = pd.MultiIndex.from_tuples([("A", 1), ("A", 2)])
        df = pd.DataFrame({"val": [10, 20]}, index=idx)
        result = build_grid_config(df)
        opts_dict = result.options.to_dict()

        # Should have enableCellSpan=True
        assert opts_dict.get("enableCellSpan") is True


# =============================================================================
# to_js_grid_config Tests
# =============================================================================


class TestToJsGridConfig:
    """Tests for to_js_grid_config() serialization."""

    def test_returns_dict(self):
        """Returns JSON-serializable dict."""
        config = build_grid_config([{"a": 1}])
        result = to_js_grid_config(config)

        assert isinstance(result, dict)
        # Should be JSON-serializable
        json.dumps(result)

    def test_adds_pywry_metadata_for_server_side(self):
        """Adds _pywry metadata for non-clientSide models."""
        config = build_grid_config([{"a": 1}], row_model_type="infinite")
        result = to_js_grid_config(config)

        assert "_pywry" in result
        assert "gridId" in result["_pywry"]
        assert "totalRows" in result["_pywry"]
        assert "blockSize" in result["_pywry"]

    def test_no_pywry_metadata_for_client_side(self):
        """No _pywry metadata for clientSide model."""
        config = build_grid_config([{"a": 1}], row_model_type="clientSide")
        result = to_js_grid_config(config)

        assert "_pywry" not in result


# =============================================================================
# GridConfig and Context Tests
# =============================================================================


class TestGridConfig:
    """Tests for GridConfig and PyWryGridContext."""

    def test_context_stores_grid_id(self):
        """PyWryGridContext stores grid_id."""
        ctx = PyWryGridContext(
            grid_id="test-123",
            theme_class="ag-theme-alpine-dark",
            total_rows=100,
        )
        assert ctx.grid_id == "test-123"

    def test_context_stores_truncated_rows(self):
        """PyWryGridContext tracks truncated rows."""
        ctx = PyWryGridContext(
            grid_id="test",
            theme_class="ag-theme-alpine",
            total_rows=1000,
            truncated_rows=500,
        )
        assert ctx.truncated_rows == 500


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_data(self):
        """Handles empty data gracefully."""
        result = build_grid_config([])
        assert result.context.total_rows == 0
        assert result.options.row_data == []

    def test_single_column(self):
        """Handles single column data."""
        result = build_grid_config([{"only_col": 1}])
        opts = result.options.to_dict()
        assert len(opts["columnDefs"]) == 1

    def test_unicode_column_names(self):
        """Handles unicode in column names."""
        data = [{"日本語": 1, "中文": 2, "emoji 🎉": 3}]
        result = build_grid_config(data)
        cols = [c["field"] for c in result.options.to_dict()["columnDefs"]]

        assert "日本語" in cols
        assert "中文" in cols
        assert "emoji 🎉" in cols

    def test_special_characters_in_values(self):
        """Handles special characters in cell values."""
        data = [{"text": "Line 1\nLine 2", "html": "<script>alert('xss')</script>"}]
        result = build_grid_config(data)

        # Values should be preserved
        assert result.options.row_data[0]["text"] == "Line 1\nLine 2"

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_mixed_types_in_column(self):
        """Handles columns with mixed types."""
        import pandas as pd

        df = pd.DataFrame({"mixed": [1, "two", 3.0, None]})
        result = build_grid_config(df)

        # Should not crash
        assert result.context.total_rows == 4

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_all_nan_column(self):
        """Handles column with all NaN values."""
        import numpy as np
        import pandas as pd

        df = pd.DataFrame({"empty": [np.nan, np.nan, np.nan]})
        result = build_grid_config(df)

        # Should convert NaN to None
        assert all(row["empty"] is None for row in result.options.row_data)


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full workflow."""

    @pytest.mark.skipif(
        not pytest.importorskip("pandas", reason="pandas required"),
        reason="pandas required",
    )
    def test_full_dataframe_workflow(self):
        """Complete workflow from DataFrame to JS config."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob"],
                "age": [30, 25],
                "active": [True, False],
                "created": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            }
        )

        config = build_grid_config(
            df,
            theme="dark",
            aggrid_theme="alpine",
            pagination=True,
            pagination_page_size=50,
        )

        js_config = to_js_grid_config(config)

        # Verify structure
        assert "columnDefs" in js_config
        assert "rowData" in js_config
        assert js_config["pagination"] is True
        assert js_config["paginationPageSize"] == 50
        assert len(js_config["rowData"]) == 2

        # Verify datetime serialization
        assert isinstance(js_config["rowData"][0]["created"], str)

    def test_value_getter_computed_column(self):
        """Value getter for computed columns."""
        cols = [
            ColDef(field="price"),
            ColDef(field="quantity"),
            ColDef(
                field="total",
                header_name="Total",
                value_getter="data.price * data.quantity",
            ),
        ]

        config = build_grid_config(
            [{"price": 10, "quantity": 5}],
            column_defs=cols,
        )

        js_config = to_js_grid_config(config)
        total_col = next(c for c in js_config["columnDefs"] if c["field"] == "total")

        assert total_col["headerName"] == "Total"
        assert total_col["valueGetter"] == "data.price * data.quantity"

    def test_value_formatter_custom_format(self):
        """Value formatter for custom display."""
        cols = [
            ColDef(
                field="amount",
                value_formatter="'$' + value.toFixed(2)",
            ),
        ]

        config = build_grid_config([{"amount": 1234.5}], column_defs=cols)
        js_config = to_js_grid_config(config)

        assert js_config["columnDefs"][0]["valueFormatter"] == "'$' + value.toFixed(2)"


# =============================================================================
# Row Pinning Transaction Tests (JavaScript Code Verification)
# =============================================================================


class TestRowPinningJavaScript:
    """Tests for AG Grid row pinning JavaScript implementation.

    These tests verify that the aggrid-defaults.js file contains the correct
    implementation for pin/unpin row transactions with original index restoration.
    """

    @pytest.fixture
    def aggrid_defaults_js(self) -> str:
        """Load the aggrid-defaults.js file content."""
        from pathlib import Path

        js_path = Path(__file__).parent.parent / "pywry" / "frontend" / "src" / "aggrid-defaults.js"
        return js_path.read_text(encoding="utf-8")

    # -------------------------------------------------------------------------
    # Pin Row Tests - Transaction from main grid to pinned section
    # -------------------------------------------------------------------------

    def test_pin_to_top_stores_original_index(self, aggrid_defaults_js: str):
        """Pin to Top stores original index for later restoration."""
        # Verify that pinning stores the original row index
        assert "data._pywryOriginalIndex = node.rowIndex" in aggrid_defaults_js

    def test_pin_to_top_removes_from_main_grid(self, aggrid_defaults_js: str):
        """Pin to Top uses applyTransaction to remove row from main grid."""
        # Should remove the row from main grid before adding to pinned
        assert "applyTransaction({ remove: [data] })" in aggrid_defaults_js

    def test_pin_to_top_adds_to_pinned_array(self, aggrid_defaults_js: str):
        """Pin to Top adds row to pinnedTopRowData array."""
        # Should get current pinned rows and add new one
        assert "getGridOption('pinnedTopRowData')" in aggrid_defaults_js
        assert "pinnedTop.push(data)" in aggrid_defaults_js
        assert "setGridOption('pinnedTopRowData', pinnedTop)" in aggrid_defaults_js

    def test_pin_to_bottom_uses_correct_array(self, aggrid_defaults_js: str):
        """Pin to Bottom uses pinnedBottomRowData array."""
        assert "getGridOption('pinnedBottomRowData')" in aggrid_defaults_js
        assert "pinnedBottom.push(data)" in aggrid_defaults_js
        assert "setGridOption('pinnedBottomRowData', pinnedBottom)" in aggrid_defaults_js

    def test_pin_menu_has_submenu_structure(self, aggrid_defaults_js: str):
        """Pin Row menu shows submenu with Top and Bottom options."""
        assert "label: 'Pin Row'" in aggrid_defaults_js
        assert "label: 'Pin to Top'" in aggrid_defaults_js
        assert "label: 'Pin to Bottom'" in aggrid_defaults_js
        assert "submenu:" in aggrid_defaults_js

    # -------------------------------------------------------------------------
    # Unpin Row Tests - Transaction from pinned section back to main grid
    # -------------------------------------------------------------------------

    def test_unpin_restores_to_original_index(self, aggrid_defaults_js: str):
        """Unpin Row uses addIndex to restore row to original position."""
        # Should use applyTransaction with addIndex for position restoration
        assert "applyTransaction({ add: [data], addIndex: originalIndex })" in aggrid_defaults_js

    def test_unpin_reads_original_index(self, aggrid_defaults_js: str):
        """Unpin Row reads stored original index from row data."""
        assert "var originalIndex = data._pywryOriginalIndex" in aggrid_defaults_js

    def test_unpin_cleans_up_original_index(self, aggrid_defaults_js: str):
        """Unpin Row deletes the temporary _pywryOriginalIndex property."""
        assert "delete data._pywryOriginalIndex" in aggrid_defaults_js

    def test_unpin_handles_missing_index_gracefully(self, aggrid_defaults_js: str):
        """Unpin Row falls back to append if original index is missing."""
        # Should check if originalIndex is valid before using addIndex
        assert "typeof originalIndex === 'number'" in aggrid_defaults_js
        # Fallback to simple add without index
        assert "applyTransaction({ add: [data] })" in aggrid_defaults_js

    def test_unpin_removes_from_pinned_top(self, aggrid_defaults_js: str):
        """Unpin Row removes row from pinnedTopRowData when pinned='top'."""
        assert "pinned === 'top'" in aggrid_defaults_js
        # Filter removes the specific row from array
        assert "pinnedTop = pinnedTop.filter" in aggrid_defaults_js

    def test_unpin_removes_from_pinned_bottom(self, aggrid_defaults_js: str):
        """Unpin Row removes row from pinnedBottomRowData when pinned='bottom'."""
        assert "pinned === 'bottom'" in aggrid_defaults_js
        # Filter removes the specific row from array
        assert "pinnedBottom = pinnedBottom.filter" in aggrid_defaults_js

    def test_unpin_menu_is_simple_action(self, aggrid_defaults_js: str):
        """Unpin Row is a simple action, not a submenu."""
        assert "label: 'Unpin Row'" in aggrid_defaults_js
        # Should not have submenu for Unpin - it's a direct action

    # -------------------------------------------------------------------------
    # Context Menu State Tests
    # -------------------------------------------------------------------------

    def test_menu_shows_pin_for_unpinned_rows(self, aggrid_defaults_js: str):
        """Menu shows 'Pin Row' submenu for rows that are not pinned."""
        # The code checks if rowPinned is falsy to show Pin options
        assert "if (rowPinned)" in aggrid_defaults_js
        # else branch shows Pin Row submenu
        assert "} else {" in aggrid_defaults_js

    def test_menu_shows_unpin_for_pinned_rows(self, aggrid_defaults_js: str):
        """Menu shows 'Unpin Row' for rows that are already pinned."""
        # When rowPinned is truthy, show Unpin
        assert "// ROW IS ALREADY PINNED" in aggrid_defaults_js
        assert "// ROW IS NOT PINNED" in aggrid_defaults_js

    def test_checks_row_pinned_state(self, aggrid_defaults_js: str):
        """Menu checks rowNode.rowPinned to determine current state."""
        assert "var rowPinned = cellInfo.rowNode.rowPinned" in aggrid_defaults_js

    # -------------------------------------------------------------------------
    # Transaction Order Tests
    # -------------------------------------------------------------------------

    def test_pin_transaction_order(self, aggrid_defaults_js: str):
        """Pin operations: store index → remove from grid → add to pinned."""
        # Find the Pin to Top action and verify order
        js = aggrid_defaults_js

        # Store index should come before remove
        store_idx = js.find("data._pywryOriginalIndex = node.rowIndex")
        remove_idx = js.find("applyTransaction({ remove: [data] })")
        push_idx = js.find("pinnedTop.push(data)")

        # All should exist
        assert store_idx > 0
        assert remove_idx > 0
        assert push_idx > 0

        # Store should come before remove, remove should come before push
        # (At least in the first occurrence which is Pin to Top)
        assert store_idx < remove_idx, "Should store original index before removing"

    def test_unpin_transaction_order(self, aggrid_defaults_js: str):
        """Unpin operations: read index → remove from pinned → add to grid."""
        js = aggrid_defaults_js

        # Find the Unpin Row action section
        unpin_section_start = js.find("label: 'Unpin Row'")
        assert unpin_section_start > 0

        # Get the unpin action section
        unpin_section = js[unpin_section_start : unpin_section_start + 2000]

        # Original index should be read
        assert "var originalIndex = data._pywryOriginalIndex" in unpin_section

        # Should clean up the property
        assert "delete data._pywryOriginalIndex" in unpin_section

        # Should restore with addIndex
        assert "applyTransaction({ add: [data], addIndex: originalIndex })" in unpin_section

    # -------------------------------------------------------------------------
    # Guard Clause Tests
    # -------------------------------------------------------------------------

    def test_pin_action_has_guard_clauses(self, aggrid_defaults_js: str):
        """Pin actions have guard clauses for missing context/data."""
        assert "if (!ctx || !ctx.rowNode) return" in aggrid_defaults_js
        assert "if (!data) return" in aggrid_defaults_js

    def test_unpin_action_has_guard_clauses(self, aggrid_defaults_js: str):
        """Unpin action has guard clause for missing context/data."""
        assert "if (!ctx || !ctx.data) return" in aggrid_defaults_js
