"""Unified AG Grid data preparation and configuration.

This module provides Pydantic models that mirror AG Grid's API:
- ColDef: Column definition with all common options
- RowSelection: Row selection configuration
- GridOptions: Complete grid configuration

All models use camelCase (via aliases) to match AG Grid's JavaScript API exactly.
This makes it easy to reference AG Grid docs and copy examples.

Usage:
    from pywry.grid import build_grid_config, ColDef

    config = build_grid_config(df)  # Works great out-of-the-box
    config = build_grid_config(df, column_defs=[
        ColDef(field="name", header_name="Full Name", pinned="left"),
        ColDef(field="age", filter="agNumberColumnFilter"),
    ])

AG Grid API Reference: https://www.ag-grid.com/javascript-data-grid/grid-options/
"""

# pylint: disable=too-many-lines

from __future__ import annotations

import json
import uuid

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .log import debug, info, warn


# --- Thresholds ---
MAX_SAFE_ROWS = 100_000  # Browser memory limit - truncate beyond this
SERVER_SIDE_THRESHOLD = 10_000  # Recommend infinite row model above this

# --- DateTime Serialization Helpers ---


# pylint: disable=R0911,R0915
def _serialize_value(  # noqa: PLR0911
    value: Any,
) -> Any:
    """Convert a single value to JSON-serializable format.

    Handles:
    - pandas Timestamp → ISO 8601 string
    - datetime.datetime → ISO 8601 string
    - datetime.date → ISO 8601 date string
    - pandas Timedelta → human-readable string
    - datetime.timedelta → human-readable string
    - numpy types → Python native types
    - NaN/NaT → None
    """
    if value is None:
        return None

    # Check for pandas NaT and numpy NaN
    try:
        import pandas as pd  # type: ignore[import-untyped]

        if pd.isna(value):
            return None
    except (ImportError, TypeError, ValueError):
        pass

    # pandas Timedelta - check BEFORE isoformat (Timedelta has isoformat too)
    if hasattr(value, "total_seconds") and hasattr(value, "components"):
        components = value.components
        if components.days:
            return f"{components.days}d {components.hours:02d}:{components.minutes:02d}:{components.seconds:02d}"
        return f"{components.hours:02d}:{components.minutes:02d}:{components.seconds:02d}"

    # datetime.timedelta (no components attribute)
    if (
        hasattr(value, "total_seconds")
        and hasattr(value, "days")
        and not hasattr(value, "components")
    ):
        total_secs = int(value.total_seconds())
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        if value.days:
            return f"{value.days}d {hours % 24:02d}:{minutes:02d}:{seconds:02d}"
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # pandas Timestamp or datetime.datetime/date (has isoformat)
    if hasattr(value, "isoformat"):
        return value.isoformat()

    # numpy scalar types → Python native
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            pass

    return value


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a row dict to JSON-serializable format."""
    return {k: _serialize_value(v) for k, v in row.items()}


# --- AG Grid Type Aliases (following official API) ---

RowModelType = Literal["clientSide", "infinite", "serverSide", "viewport"]
DomLayoutType = Literal["normal", "autoHeight", "print"]
RowSelectionMode = Literal["singleRow", "multiRow"]
CellDataType = Literal[
    "text", "number", "boolean", "date", "dateString", "dateTimeString", "object"
]
FilterType = Literal[
    "agTextColumnFilter",
    "agNumberColumnFilter",
    "agDateColumnFilter",
    "agSetColumnFilter",
]
PinnedPosition = Literal["left", "right"]

# --- Base Model with camelCase serialization ---


class AGGridModel(BaseModel):
    """Base model for AG Grid objects with camelCase serialization."""

    model_config = ConfigDict(
        populate_by_name=True,  # Accept both snake_case and camelCase
        extra="allow",  # Allow extra fields for flexibility
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict with camelCase keys, excluding None values.

        Explicitly maps field names to aliases.
        """
        result: dict[str, Any] = {
            (field_info.alias if field_info.alias else field_name): getattr(self, field_name)
            for field_name, field_info in getattr(self, "model_fields", {}).items()
            if getattr(self, field_name) is not None
        }
        # Include extra fields (not in model_fields)
        if self.__pydantic_extra__:
            result.update({k: v for k, v in self.__pydantic_extra__.items() if v is not None})
        return result


class ColDef(AGGridModel):
    """AG Grid Column Definition.

    See: https://www.ag-grid.com/javascript-data-grid/column-definitions/

    Use snake_case in Python, serializes to camelCase for AG Grid.

    Example:
        ColDef(field="name", header_name="Full Name", min_width=100)
        # Serializes to: {"field": "name", "headerName": "Full Name", "minWidth": 100}
    """

    # Identity
    field: str | None = None
    col_id: str | None = Field(default=None, alias="colId")
    header_name: str | None = Field(default=None, alias="headerName")
    header_tooltip: str | None = Field(default=None, alias="headerTooltip")

    # Display
    hide: bool | None = None
    pinned: PinnedPosition | None = None
    width: int | None = None
    min_width: int | None = Field(default=None, alias="minWidth")
    max_width: int | None = Field(default=None, alias="maxWidth")
    flex: int | None = None

    # Interaction
    sortable: bool | None = None  # Inherit from defaultColDef
    filter: bool | str | None = None
    resizable: bool | None = None
    editable: bool | None = None

    # Cell rendering
    cell_data_type: CellDataType | None = Field(default=None, alias="cellDataType")
    value_getter: str | None = Field(default=None, alias="valueGetter")  # JS expression
    value_formatter: str | None = Field(default=None, alias="valueFormatter")
    value_setter: str | None = Field(default=None, alias="valueSetter")  # For editable
    cell_renderer: str | None = Field(default=None, alias="cellRenderer")
    cell_class: str | list[str] | None = Field(default=None, alias="cellClass")
    cell_style: dict[str, str] | None = Field(default=None, alias="cellStyle")
    auto_height: bool | None = Field(default=None, alias="autoHeight")
    wrap_text: bool | None = Field(default=None, alias="wrapText")

    # Row grouping / Aggregation
    row_group: bool | None = Field(default=None, alias="rowGroup")
    enable_row_group: bool | None = Field(default=None, alias="enableRowGroup")
    agg_func: str | None = Field(default=None, alias="aggFunc")  # 'sum', 'avg', etc.

    # Row Spanning (modern AG Grid API)
    # Set to True to merge cells with equal values, or provide JS callback string
    # Requires enableCellSpan=True on GridOptions
    span_rows: bool | str | None = Field(default=None, alias="spanRows")

    # Pinning helpers
    lock_position: bool | str | None = Field(default=None, alias="lockPosition")
    lock_pinned: bool | None = Field(default=None, alias="lockPinned")
    lock_visible: bool | None = Field(default=None, alias="lockVisible")


class ColGroupDef(AGGridModel):
    """AG Grid Column Group Definition.

    See: https://www.ag-grid.com/javascript-data-grid/column-groups/
    """

    header_name: str = Field(alias="headerName")
    children: list[ColDef | ColGroupDef] = Field(default_factory=list)
    group_id: str | None = Field(default=None, alias="groupId")
    marry_children: bool | None = Field(default=None, alias="marryChildren")
    open_by_default: bool | None = Field(default=None, alias="openByDefault")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict, recursively converting children."""
        result = self.model_dump(by_alias=True, exclude_none=True, exclude={"children"})
        result["children"] = [c.to_dict() for c in self.children]
        return result


class DefaultColDef(AGGridModel):
    """Default column definition applied to all columns.

    These defaults make the grid useful out-of-the-box.
    """

    # Interaction - enabled by default
    sortable: bool = True
    filter: bool = True  # Auto-detects: text, number, date
    resizable: bool = True
    floating_filter: bool = Field(default=False, alias="floatingFilter")  # Filter via menu only

    # Sizing
    min_width: int = Field(default=80, alias="minWidth")
    flex: int = 1  # Columns share available space

    # Row grouping ready
    enable_row_group: bool = Field(default=True, alias="enableRowGroup")
    enable_pivot: bool = Field(default=True, alias="enablePivot")
    enable_value: bool = Field(default=True, alias="enableValue")


class RowSelection(AGGridModel):
    """AG Grid Row Selection configuration.

    See: https://www.ag-grid.com/javascript-data-grid/row-selection-multi-row/

    enableClickSelection options:
    - False: Only checkboxes select rows
    - 'enableDeselection': Ctrl+click to deselect only
    - 'enableSelection': Click to select only
    - True: Click to select, Ctrl+click to deselect (default)
    """

    mode: RowSelectionMode = "multiRow"
    checkboxes: bool = True
    header_checkbox: bool = Field(default=True, alias="headerCheckbox")
    # Default to True - click selects, Ctrl+click deselects
    enable_click_selection: bool | str = Field(default=True, alias="enableClickSelection")
    hide_disabled_checkboxes: bool = Field(default=False, alias="hideDisabledCheckboxes")


class GridOptions(AGGridModel):
    """AG Grid options following the official API.

    This mirrors AG Grid's GridOptions interface.
    Includes sensible defaults that make the grid powerful out-of-the-box.

    See: https://www.ag-grid.com/javascript-data-grid/grid-options/
    """

    # === Column Definitions ===
    column_defs: list[dict[str, Any]] = Field(default_factory=list, alias="columnDefs")
    default_col_def: dict[str, Any] | None = Field(default=None, alias="defaultColDef")

    # === Row Data ===
    row_data: list[dict[str, Any]] | None = Field(default=None, alias="rowData")
    row_model_type: RowModelType = Field(default="clientSide", alias="rowModelType")

    # === Selection (enabled by default) ===
    row_selection: dict[str, Any] | bool | None = Field(default=None, alias="rowSelection")
    cell_selection: bool | None = Field(default=True, alias="cellSelection")

    # === Layout ===
    dom_layout: DomLayoutType = Field(default="normal", alias="domLayout")

    # === Pagination ===
    # None = let JS auto-decide based on row count (enabled for >10 rows)
    pagination: bool | None = None
    pagination_page_size: int = Field(default=100, alias="paginationPageSize")
    pagination_page_size_selector: list[int] | bool = Field(
        default_factory=lambda: [25, 50, 100, 250, 500],
        alias="paginationPageSizeSelector",
    )

    # === Row Grouping (enabled by default) ===
    group_display_type: str = Field(default="singleColumn", alias="groupDisplayType")
    row_group_panel_show: str = Field(default="always", alias="rowGroupPanelShow")
    group_default_expanded: int = Field(default=1, alias="groupDefaultExpanded")

    # === Infinite/Server-Side Row Model ===
    cache_block_size: int = Field(default=500, alias="cacheBlockSize")
    max_concurrent_datasource_requests: int = Field(
        default=2, alias="maxConcurrentDatasourceRequests"
    )
    infinite_initial_row_count: int = Field(default=1, alias="infiniteInitialRowCount")

    # === Editing ===
    single_click_edit: bool | None = Field(default=None, alias="singleClickEdit")
    undo_redo_cell_editing: bool = Field(default=True, alias="undoRedoCellEditing")
    undo_redo_cell_editing_limit: int = Field(default=20, alias="undoRedoCellEditingLimit")

    # === Clipboard ===
    copy_headers_to_clipboard: bool = Field(default=True, alias="copyHeadersToClipboard")

    # === Rendering ===
    animate_rows: bool = Field(default=True, alias="animateRows")

    # === Cell Spanning (for row spanning) ===
    enable_cell_span: bool = Field(default=False, alias="enableCellSpan")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization to AG Grid.

        Handles conditional inclusion based on row model type.
        """
        # Start with base serialization
        result = self.model_dump(by_alias=True, exclude_none=True)

        # Remove row data for non-clientSide models (they use datasource)
        if self.row_model_type != "clientSide":
            result.pop("rowData", None)

        # Only include pagination fields if pagination is explicitly enabled
        # (when None, JS auto-decides and handles page size itself)
        if self.pagination is not True:
            result.pop("paginationPageSize", None)
            result.pop("paginationPageSizeSelector", None)

        # Only include infinite/server-side fields for those models
        if self.row_model_type not in ("infinite", "serverSide"):
            result.pop("cacheBlockSize", None)
            result.pop("maxConcurrentDatasourceRequests", None)
            result.pop("infiniteInitialRowCount", None)

        return result


class PyWryGridContext(BaseModel):
    """PyWry-specific context for grid rendering.

    This contains metadata that PyWry needs but AG Grid doesn't care about.
    Kept separate from GridOptions to maintain clean API boundaries.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    grid_id: str
    theme_class: str
    total_rows: int = 0
    truncated_rows: int = 0
    original_data: list[dict[str, Any]] = Field(default_factory=list, repr=False)


class GridConfig(BaseModel):
    """Combined configuration: AG Grid options + PyWry context.

    This is what rendering functions receive. It cleanly separates:
    - options: What AG Grid needs (follows their API)
    - context: What PyWry needs (grid_id, theme, etc.)
    """

    options: GridOptions
    context: PyWryGridContext


class GridData(BaseModel):
    """Normalized grid data from various input formats."""

    row_data: list[dict[str, Any]]
    columns: list[str]
    total_rows: int
    # For MultiIndex columns - nested structure for ColGroupDef
    column_groups: list[dict[str, Any]] | None = None
    # For MultiIndex rows - index columns that were flattened
    index_columns: list[str] = Field(default_factory=list)
    # Column type hints from pandas dtypes (for auto-configuring AG Grid)
    column_types: dict[str, str] = Field(default_factory=dict)


def _detect_column_types(data: Any) -> dict[str, str]:
    """Detect AG Grid cellDataType from pandas dtypes.

    Returns a dict mapping column names to AG Grid cell data types:
    - datetime64 → 'dateTimeString' (we serialize as ISO string with time)
    - timedelta64 → 'text' (we serialize as readable string)
    - bool → 'boolean'
    - int/float → 'number'
    - object/string with numeric strings → 'text' (force string to prevent number conversion)
    - object/string → None (let AG Grid infer)
    """
    if not hasattr(data, "dtypes"):
        return {}

    column_types: dict[str, str] = {}
    for col, dtype in data.dtypes.items():
        dtype_str = str(dtype)
        col_str = str(col)

        if "datetime64" in dtype_str:
            column_types[col_str] = "dateTimeString"  # ISO string with time
        elif "timedelta64" in dtype_str:
            column_types[col_str] = "text"  # Human-readable string
        elif dtype_str in {"bool", "boolean"}:
            column_types[col_str] = "boolean"
        elif "int" in dtype_str or "float" in dtype_str:
            column_types[col_str] = "number"
        elif dtype.kind in ("O", "U", "S") or "str" in dtype_str or dtype_str == "object":
            # dtype.kind: O=object, U=unicode string, S=byte string
            # Also check for "str" in dtype_str for pandas 3.0+ StringDtype
            # Check if this is a string column with numeric-looking strings
            # that should NOT be converted to numbers (leading zeros, pure digit strings)
            # Examples: "007", "0123", "12345" (IDs, codes, etc.)
            sample = data[col].dropna().head(100)
            is_numeric_string = False
            for val in sample:
                val_str = str(val)
                # Check for strings with leading zeros (must preserve as text)
                if len(val_str) > 1 and val_str[0] == "0" and val_str.isdigit():
                    is_numeric_string = True
                    break
            if is_numeric_string:
                column_types[col_str] = "text"
        # else: default to no type hint (AG Grid will infer)

    return column_types


def _flatten_multiindex_columns(data: Any) -> tuple[Any, list[dict[str, Any]] | None]:
    """Handle MultiIndex columns by flattening and creating column group structure.

    Example: MultiIndex([('A', 'x'), ('A', 'y'), ('B', 'z')])
    Should become: [
        {headerName: 'A', children: [{field: 'A_x'}, {field: 'A_y'}]},
        {headerName: 'B', children: [{field: 'B_z'}]}
    ]

    Returns
    -------
    tuple
        (flattened DataFrame, column_groups structure for AG Grid)
    """
    from collections import defaultdict  # pylint: disable=import-outside-toplevel

    # Check if columns are MultiIndex
    if not hasattr(data, "columns") or not hasattr(data.columns, "nlevels"):
        return data, None

    if data.columns.nlevels <= 1:
        return data, None

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    flat_columns: list[str] = []

    for col_tuple in data.columns:
        # Join tuple levels with underscore for flat field name
        if isinstance(col_tuple, tuple):
            flat_name = "_".join(str(level) for level in col_tuple)
            group_name = str(col_tuple[0])
            leaf_name = "_".join(str(level) for level in col_tuple[1:])
        else:
            flat_name = str(col_tuple)
            group_name = flat_name
            leaf_name = flat_name

        flat_columns.append(flat_name)
        groups[group_name].append(
            {
                "field": flat_name,
                "headerName": leaf_name,
            }
        )

    # Flatten the DataFrame columns
    data_copy = data.copy()
    data_copy.columns = flat_columns

    # Build AG Grid column groups
    column_groups: list[dict[str, Any]] = []
    for group_name, children in groups.items():
        if len(children) == 1 and children[0]["headerName"] == group_name:
            # Single column, no need for group
            column_groups.append({"field": children[0]["field"]})
        else:
            column_groups.append(
                {
                    "headerName": group_name,
                    "children": children,
                }
            )

    return data_copy, column_groups


def _flatten_multiindex_rows(data: Any) -> tuple[Any, list[str]]:
    """Handle MultiIndex rows by resetting index to columns.

    For AG Grid row spanning, the index levels become regular columns
    that can be used with rowSpan configuration.

    Returns
    -------
    tuple
        (DataFrame with reset index, list of index column names)
    """
    if not hasattr(data, "index") or not hasattr(data.index, "nlevels"):
        return data, []

    # Check if index is meaningful (not just RangeIndex)
    index = data.index
    is_default_index = (
        hasattr(index, "name")
        and index.name is None
        and hasattr(index, "names")
        and all(n is None for n in index.names)
        and (not hasattr(index, "nlevels") or index.nlevels == 1)
    )
    if is_default_index:
        return data, []

    # Get index level names
    if hasattr(index, "names"):
        index_names = [
            name if name is not None else f"index_{i}" for i, name in enumerate(index.names)
        ]
    else:
        index_names = [index.name if index.name else "index"]

    # Reset index to make it regular columns
    data_copy = data.reset_index()

    return data_copy, index_names


def normalize_data(data: Any) -> GridData:
    """Convert various data formats to normalized GridData.

    Handles:
    - pandas DataFrame (including MultiIndex columns and rows)
    - list of dicts: [{'a': 1}, {'a': 2}]
    - dict of lists: {'a': [1, 2], 'b': [3, 4]}
    - single dict: {'a': 1, 'b': 2}

    For pandas MultiIndex:
    - MultiIndex columns → column_groups for AG Grid ColGroupDef
    - MultiIndex rows → flattened to regular columns (can use for row spanning)
    """
    row_data: list[dict[str, Any]] = []
    columns: list[str] = []
    column_groups: list[dict[str, Any]] | None = None
    index_columns: list[str] = []
    column_types: dict[str, str] = {}

    try:
        # pandas DataFrame (duck typing)
        if hasattr(data, "to_dict") and hasattr(data, "columns"):
            # Detect column types BEFORE any transformations
            column_types = _detect_column_types(data)

            # Handle MultiIndex columns FIRST (before resetting index)
            data, column_groups = _flatten_multiindex_columns(data)

            # Handle MultiIndex rows (reset index to columns)
            data, index_columns = _flatten_multiindex_rows(data)

            # Update column types after flattening (may have new column names)
            column_types.update(_detect_column_types(data))

            # Now convert to records
            row_data = data.to_dict(orient="records")
            columns = list(data.columns)

            if index_columns:
                debug(f"Flattened {len(index_columns)} index levels to columns: {index_columns}")
            if column_groups:
                debug(f"Created {len(column_groups)} column groups from MultiIndex")

        # dict - could be column-oriented or single row
        elif isinstance(data, dict):
            first_value = next(iter(data.values()), None)
            if isinstance(first_value, (list, tuple)):
                columns = list(data.keys())
                num_rows = len(first_value) if first_value else 0
                row_data = [{col: data[col][i] for col in columns} for i in range(num_rows)]
            else:
                columns = list(data.keys())
                row_data = [data]
        # list - assume list of dicts
        elif isinstance(data, list):
            row_data = list(data)
            if row_data and isinstance(row_data[0], dict):
                columns = list(row_data[0].keys())
                # Infer types from actual values
                column_types = _infer_column_types_from_values(row_data, columns)
        else:
            row_data = list(data)
            if row_data and isinstance(row_data[0], dict):
                columns = list(row_data[0].keys())
    except (ValueError, TypeError) as e:
        warn(f"Failed to convert data: {e}")
        row_data = []
        columns = []

    # Serialize datetime-like values to JSON-compatible format
    row_data = [_serialize_row(row) for row in row_data]

    return GridData(
        row_data=row_data,
        columns=columns,
        total_rows=len(row_data),
        column_groups=column_groups,
        index_columns=index_columns,
        column_types=column_types,
    )


def _infer_column_types_from_values(
    row_data: list[dict[str, Any]], columns: list[str]
) -> dict[str, str]:
    """Infer AG Grid cellDataType from Python values in list of dicts.

    Used when data is passed as list of dicts instead of DataFrame,
    so we can't use pandas dtypes.

    Returns a dict mapping column names to AG Grid cell data types:
    - int/float values → 'number'
    - bool values → 'boolean'
    - strings that look like numbers with leading zeros → 'text'
    """
    if not row_data or not columns:
        return {}

    column_types: dict[str, str] = {}
    # Sample first 100 rows for type inference
    sample = row_data[:100]

    for col in columns:
        values = [row.get(col) for row in sample if row.get(col) is not None]
        if not values:
            continue

        # Check first non-None value for type
        first_val = values[0]

        if isinstance(first_val, bool):
            column_types[col] = "boolean"
        elif isinstance(first_val, (int, float)):
            column_types[col] = "number"
        elif isinstance(first_val, str):
            # Check for leading zeros (should stay as text)
            has_leading_zero = any(
                isinstance(v, str) and len(v) > 1 and v[0] == "0" and v.isdigit() for v in values
            )
            if has_leading_zero:
                column_types[col] = "text"
            # Otherwise let AG Grid infer

    return column_types


def _build_datetime_col_def(col_def: dict[str, Any], col_type: str) -> None:
    """Configure datetime columns with proper AG Grid date filter including time.

    For dateTimeString columns, enables the time component in the date filter
    so users can filter by both date and time using the native datetime picker.
    """
    if col_type == "dateTimeString":
        col_def["filterParams"] = {"includeBlanksInEquals": True}


def _build_number_col_def(col_def: dict[str, Any], col_type: str) -> None:
    """Configure number columns for temporal patterns only.

    The dataTypeDefinitions.number.valueFormatter in JavaScript handles all formatting.
    We only intervene for temporal columns to prevent unwanted formatting.
    """
    if col_type != "number":
        return

    # Check column name for temporal patterns - don't format years, dates, etc.
    field_name = col_def.get("field", "").lower()
    temporal_patterns = ("year", "date", "period", "month", "day", "quarter", "week")
    if any(pattern in field_name for pattern in temporal_patterns):
        # Disable data type formatter for temporal columns
        col_def["cellDataType"] = False


def build_column_defs(  # noqa: C901, PLR0912  # pylint: disable=too-many-branches
    columns: list[str],
    column_defs: list[dict[str, Any] | ColDef] | None = None,
    column_groups: list[dict[str, Any]] | None = None,
    index_columns: list[str] | None = None,
    enable_cell_span: bool = False,
    column_types: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Build AG Grid column definitions.

    If column_defs is provided, use it. Otherwise auto-generate from column names.
    Supports column groups from MultiIndex and special handling for index columns.

    Parameters
    ----------
    columns : list[str]
        Column names from the data.
    column_defs : list | None
        Custom column definitions (overrides auto-generation).
    column_groups : list | None
        Column group structure from MultiIndex columns.
    index_columns : list[str] | None
        Index columns that were flattened from MultiIndex rows.
    enable_cell_span : bool
        If True, index columns get spanRows=True for automatic row spanning.
    column_types : dict[str, str] | None
        Detected column types from pandas dtypes (e.g., {'timestamp': 'dateString'}).
    """
    index_set = set(index_columns or [])
    types = column_types or {}

    if column_defs is not None:
        # User provided custom column defs - but still add spanRows to index columns
        result: list[dict[str, Any]] = []
        for c in column_defs:
            # Use duck typing - check for to_dict method instead of isinstance
            # (isinstance fails after module reload due to class identity mismatch)
            col_dict = c.to_dict() if hasattr(c, "to_dict") else dict(c)
            # Auto-add spanRows to index columns when cell spanning is enabled
            if enable_cell_span and col_dict.get("field") in index_set:
                col_dict.setdefault("spanRows", True)
            result.append(col_dict)
        return result

    result = []

    # Add index columns first (pinned left, with optional row spanning)
    if index_columns:
        for col in index_columns:
            col_def: dict[str, Any] = {
                "field": col,
                "headerName": col,
                "pinned": "left",
                "lockPosition": True,
                "cellClass": "ag-row-group-cell",
            }
            # Enable row spanning on index columns when enableCellSpan is True
            if enable_cell_span:
                col_def["spanRows"] = True
            # Add cellDataType and datetime filter params if detected
            if col in types:
                col_def["cellDataType"] = types[col]
                _build_datetime_col_def(col_def, types[col])
                _build_number_col_def(col_def, types[col])
            result.append(col_def)

    # If we have column groups from MultiIndex, use them
    if column_groups:
        for group in column_groups:
            if "children" in group:
                # This is a column group - add cellDataType to children
                children_with_types = []
                for child in group["children"]:
                    child_field = child.get("field", "")
                    if child_field in types:
                        child_with_type = {**child, "cellDataType": types[child_field]}
                        _build_datetime_col_def(child_with_type, types[child_field])
                        _build_number_col_def(child_with_type, types[child_field])
                        children_with_types.append(child_with_type)
                    else:
                        children_with_types.append(child)
                result.append(
                    {
                        "headerName": group["headerName"],
                        "children": children_with_types,
                        "marryChildren": True,  # Keep grouped columns together
                    }
                )
            else:
                # Single column (not a group)
                col_def = {"field": group["field"]}
                if group["field"] in types:
                    col_def["cellDataType"] = types[group["field"]]
                    _build_datetime_col_def(col_def, types[group["field"]])
                    _build_number_col_def(col_def, types[group["field"]])
                result.append(col_def)
        return result

    # Simple case - just create field definitions for non-index columns
    for col in columns:
        if col not in index_set:
            col_def = {"field": col}
            if col in types:
                col_def["cellDataType"] = types[col]
                _build_datetime_col_def(col_def, types[col])
                _build_number_col_def(col_def, types[col])
            result.append(col_def)

    return result


# --- Main Entry Point ---


def build_grid_config(  # pylint: disable=too-many-arguments
    data: Any,
    *,
    column_defs: list[dict[str, Any] | ColDef] | None = None,
    grid_options: dict[str, Any] | None = None,
    row_model_type: RowModelType = "clientSide",
    theme: Literal["dark", "light"] = "dark",
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    grid_id: str | None = None,
    pagination: bool | None = None,
    pagination_page_size: int = 100,
    cache_block_size: int = 500,
    row_selection: RowSelection | dict[str, Any] | bool = False,
    enable_cell_span: bool | None = None,
) -> GridConfig:
    """Build complete grid configuration from data.

    This is the main entry point. Creates a fully-configured grid
    with sensible defaults that work great out-of-the-box.

    Features enabled by default:
    - Multi-row selection with checkboxes
    - Sortable, filterable, resizable columns
    - Floating filter row
    - Row grouping with drag panel
    - Cell text selection
    - Undo/redo for edits
    - Copy with headers

    Parameters
    ----------
    data : Any
        Input data (DataFrame, list, dict).
    column_defs : list | None
        Custom column definitions. Can be dicts or ColDef objects.
    grid_options : dict | None
        Additional AG Grid options to merge.
    row_model_type : str
        'clientSide' (default), 'infinite', 'serverSide', or 'viewport'.
    theme : str
        'dark' or 'light'.
    aggrid_theme : str
        AG Grid theme: 'quartz', 'alpine', 'balham', 'material'.
    grid_id : str | None
        Custom grid ID (auto-generated if None).
    pagination : bool
        Enable pagination.
    pagination_page_size : int
        Rows per page.
    cache_block_size : int
        Block size for infinite row model.
    row_selection : RowSelection | dict | bool
        Row selection config. True = multiRow with checkboxes.
        False = disabled. Or pass RowSelection/dict for custom.
    enable_cell_span : bool | None
        Enable row spanning for index columns. None (default) = auto-detect
        from MultiIndex rows. True = force enable. False = force disable.

    Returns
    -------
    GridConfig
        Complete configuration with options and context.
    """
    # Generate unique grid ID
    gid = grid_id or f"grid-{uuid.uuid4().hex[:8]}"

    # Normalize input data
    grid_data = normalize_data(data)
    row_data = grid_data.row_data
    columns = grid_data.columns
    total_rows = grid_data.total_rows

    # Auto-enable cell spanning if we have index columns from MultiIndex
    # (user can still explicitly disable with enable_cell_span=False)
    use_cell_span = enable_cell_span
    if use_cell_span is None:
        use_cell_span = bool(grid_data.index_columns)

    # Build column definitions (with MultiIndex support)
    col_defs = build_column_defs(
        columns,
        column_defs,
        column_groups=grid_data.column_groups,
        index_columns=grid_data.index_columns,
        enable_cell_span=use_cell_span,
        column_types=grid_data.column_types,
    )

    # Theme class
    theme_class = f"ag-theme-{aggrid_theme}-dark" if theme == "dark" else f"ag-theme-{aggrid_theme}"

    # Handle large datasets
    truncated_rows = 0
    original_data = row_data

    if row_model_type != "clientSide":
        info(f"{row_model_type} row model for {total_rows:,} rows (grid: {gid})")
        row_data_for_grid = None
    elif total_rows > MAX_SAFE_ROWS:
        warn(
            f"Dataset has {total_rows:,} rows, truncating to {MAX_SAFE_ROWS:,}. "
            "Use row_model_type='infinite' for full data."
        )
        row_data_for_grid = row_data[:MAX_SAFE_ROWS]
        truncated_rows = total_rows - MAX_SAFE_ROWS
    elif total_rows > SERVER_SIDE_THRESHOLD:
        debug(
            f"Large dataset ({total_rows:,} rows). "
            "Consider row_model_type='infinite' for better performance."
        )
        row_data_for_grid = row_data
    else:
        row_data_for_grid = row_data

    # Build row selection config
    row_sel_dict: dict[str, Any] | bool | None = None
    if row_selection is True:
        row_sel_dict = RowSelection().to_dict()
    elif row_selection is False:
        row_sel_dict = False  # Pass False as-is, not None
    elif isinstance(row_selection, RowSelection):
        row_sel_dict = row_selection.to_dict()
    elif isinstance(row_selection, dict):
        row_sel_dict = row_selection

    options = GridOptions(
        columnDefs=col_defs,
        defaultColDef=DefaultColDef().to_dict(),
        rowData=row_data_for_grid,
        rowModelType=row_model_type,
        rowSelection=row_sel_dict,
        domLayout="normal",
        pagination=pagination,
        paginationPageSize=pagination_page_size,
        cacheBlockSize=cache_block_size,
        enableCellSpan=use_cell_span,
        **(grid_options or {}),
    )

    context = PyWryGridContext(
        grid_id=gid,
        theme_class=theme_class,
        total_rows=total_rows,
        truncated_rows=truncated_rows,
        original_data=original_data,
    )

    return GridConfig(options=options, context=context)


# --- Serialization Helpers ---


def to_js_grid_config(config: GridConfig) -> dict[str, Any]:
    """Convert GridConfig to JSON-serializable dict for JS.

    Used by anywidget backend which passes config as JSON.
    """
    result = config.options.to_dict()

    # Add PyWry-specific config for IPC
    if config.options.row_model_type != "clientSide":
        result["_pywry"] = {
            "gridId": config.context.grid_id,
            "totalRows": config.context.total_rows,
            "blockSize": config.options.cache_block_size,
        }

    return result


def build_grid_html(config: GridConfig) -> str:
    """Generate the HTML/JS snippet for the AG Grid."""
    options_dict = config.options.to_dict()

    # Add PyWry metadata for IPC
    if config.options.row_model_type != "clientSide":
        options_dict["_pywry"] = {
            "gridId": config.context.grid_id,
            "totalRows": config.context.total_rows,
            "blockSize": config.options.cache_block_size,
        }

    grid_config_json = json.dumps(options_dict)

    return f"""
<div id="myGrid" class="pywry-grid {config.context.theme_class}" style="width:100%;height:100%;"></div>
<script>
    (function() {{
        function initGrid() {{
            if (typeof agGrid === 'undefined') {{
                setTimeout(initGrid, 50);
                return;
            }}

            var gridConfig = {grid_config_json};
            const gridDiv = document.querySelector('#myGrid');

            if (gridDiv) {{
                const gridId = '{config.context.grid_id}';

                var gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS
                    ? window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId)
                    : gridConfig;

                window.__PYWRY_GRID_API__ = agGrid.createGrid(gridDiv, gridOptions);

                if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
                    window.PYWRY_AGGRID_REGISTER_LISTENERS(window.__PYWRY_GRID_API__, gridDiv, gridId);
                }}
            }}
        }}
        initGrid();
    }})();
</script>
"""
