"""The screener builder, assembled from PyWry components."""

from functools import lru_cache
from pathlib import Path
from typing import Any

_ASSETS = Path(__file__).resolve().parent.parent / "assets"
_CSS = _ASSETS / "screener_builder.css"
_JS = _ASSETS / "screener_builder.js"
_CONNECT = _ASSETS / "openbb_connect.js"

RESULTS_GRID_ID = "tmx-results-grid"

_FMT_PRICE = (
    "value == null || value === '' ? '' : "
    "Number(value).toLocaleString('en-US', {minimumFractionDigits: 2,"
    " maximumFractionDigits: 2})"
)
_FMT_COMPACT = (
    "value == null || value === '' ? '' : "
    "Intl.NumberFormat('en-US', {notation: 'compact',"
    " maximumFractionDigits: 2}).format(value)"
)
_FMT_PCT = "value == null || value === '' ? '' : Number(value).toFixed(2) + '%'"
_FMT_NORM_PCT = (
    "value == null || value === '' ? '' : (Number(value) * 100).toFixed(2) + '%'"
)
_FMT_RAW = "value == null || value === '' ? '' : String(value)"


def _num(field: str, header: str, fmt: str, width: int = 110) -> dict[str, Any]:
    """Build a right-aligned, formatted numeric column definition."""
    return {
        "field": field,
        "headerName": header,
        "type": "numericColumn",
        "cellDataType": "number",
        "valueFormatter": fmt,
        "minWidth": width,
        "wrapText": False,
        "autoHeight": False,
    }


def _txt(field: str, header: str, width: int = 110, **extra: Any) -> dict[str, Any]:
    """Build a non-wrapping text column definition."""
    return {
        "field": field,
        "headerName": header,
        "minWidth": width,
        "wrapText": False,
        "autoHeight": False,
        **extra,
    }


_COMMON_COLS: list[dict[str, Any]] = [
    _txt("symbol", "Symbol", 95, pinned="left"),
    _txt("name", "Name", 300, tooltipField="name"),
    _txt("exchange", "Exchange", 100),
    _num("price", "Price", _FMT_PRICE),
    _num("price_change", "% Change", _FMT_NORM_PCT),
    _num("market_cap", "Market Cap", _FMT_COMPACT, 120),
]

_TRADING_COLS: list[dict[str, Any]] = [
    _num("volume", "Volume", _FMT_COMPACT),
    _num("volume_avg_30d", "Vol 30D", _FMT_COMPACT),
    _num("beta", "Beta", _FMT_RAW),
    _num("standard_deviation", "Std Dev", _FMT_RAW),
    _num("high_52w", "52W High", _FMT_PRICE),
    _num("low_52w", "52W Low", _FMT_PRICE),
    _num("change_52w", "52W Change", _FMT_NORM_PCT),
    _num("performance_ytd", "YTD", _FMT_NORM_PCT),
]

_SESSION_COLS: list[dict[str, Any]] = [
    _num("open", "Open", _FMT_PRICE),
    _num("high", "High", _FMT_PRICE),
    _num("low", "Low", _FMT_PRICE),
]

_EQUITY_COLS: list[dict[str, Any]] = [
    *_COMMON_COLS,
    _num("pe_ratio", "P/E", _FMT_RAW),
    _num("pb_ratio", "P/B", _FMT_RAW),
    _num("ps_ratio", "P/S", _FMT_RAW),
    _num("dividend_yield", "Div Yield", _FMT_PCT),
    _num("dividend_rate", "Div Rate", _FMT_PRICE),
    _num("return_on_equity", "ROE", _FMT_PCT),
    _num("return_on_assets", "ROA", _FMT_PCT),
    _num("gross_margin", "Gross Margin", _FMT_PCT, 120),
    _num("revenue_ltm", "Revenue LTM", _FMT_COMPACT, 120),
    _num("free_cash_flow", "Free Cash Flow", _FMT_COMPACT, 130),
    _num("employees", "Employees", _FMT_COMPACT),
    *_TRADING_COLS,
]

_FUND_COLS: list[dict[str, Any]] = [
    *_COMMON_COLS,
    _num("dividend_yield", "Div Yield", _FMT_PCT),
    _num("dividend_rate", "Div Rate", _FMT_PRICE),
    *_TRADING_COLS,
]

_INDEX_COLS: list[dict[str, Any]] = [
    _txt("symbol", "Symbol", 95, pinned="left"),
    _txt("name", "Name", 300, tooltipField="name"),
    _txt("exchange", "Exchange", 100),
    _num("price", "Price", _FMT_PRICE),
    _num("price_change", "% Change", _FMT_NORM_PCT),
    _num("net_change", "Net Change", _FMT_PRICE, 120),
    *_SESSION_COLS,
    _num("prev_close", "Prev Close", _FMT_PRICE, 120),
    _num("volume", "Volume", _FMT_COMPACT),
    _num("high_52w", "52W High", _FMT_PRICE),
    _num("low_52w", "52W Low", _FMT_PRICE),
    _txt("currency", "Currency", 90),
]

_FUTURE_COLS: list[dict[str, Any]] = [
    _txt("symbol", "Symbol", 95, pinned="left"),
    _txt("name", "Name", 300, tooltipField="name"),
    _txt("exchange", "Exchange", 100),
    _txt("expiration", "Month", 110),
    _num("price", "Last", _FMT_PRICE),
    _num("settlement_price", "Settlement", _FMT_PRICE, 120),
    _num("net_change", "Net Change", _FMT_PRICE, 120),
    *_SESSION_COLS,
    _num("volume", "Volume", _FMT_COMPACT),
    _num("open_interest", "Open Interest", _FMT_COMPACT, 130),
    _num("transactions", "Transactions", _FMT_COMPACT, 125),
]

COLUMN_DEFS_BY_ASSET: dict[str, list[dict[str, Any]]] = {
    "Equity": _EQUITY_COLS,
    "ETF": _FUND_COLS,
    "Mutual Fund": _FUND_COLS,
    "Money Market Fund": _FUND_COLS,
    "Index": _INDEX_COLS,
    "Future": _FUTURE_COLS,
}

COLUMNS: list[dict[str, Any]] = _EQUITY_COLS

ALWAYS_VISIBLE = {"symbol", "name"}


def columns_for(asset: str) -> list[dict[str, Any]]:
    """Return the column definitions for one asset type.

    Parameters
    ----------
    asset : str
        The asset type the screen ran against.

    Returns
    -------
    list[dict]
        The columns that asset type publishes.
    """
    return COLUMN_DEFS_BY_ASSET.get(asset) or _EQUITY_COLS


def _present(value: Any) -> bool:
    """Report whether a cell carries something worth a column."""
    if value is None:
        return False

    return bool(value.strip()) if isinstance(value, str) else True


def prune_empty_columns(
    rows: "list[dict]",
    columns: "list[dict]",
    required: "set[str] | None" = None,
) -> list[dict]:
    """Drop the columns no row carries a value for.

    Parameters
    ----------
    rows : list[dict]
        The screened rows.
    columns : list[dict]
        The candidate column definitions.
    required : set[str] or None
        Columns to keep whether or not a row populates them.

    Returns
    -------
    list[dict]
        The columns worth rendering.
    """
    if not columns or not rows:
        return list(columns)

    keep = set(required or ALWAYS_VISIBLE)

    for row in rows:
        for column in columns:
            field = column.get("field")

            if field and field not in keep and _present(row.get(field)):
                keep.add(field)

    return [column for column in columns if column.get("field") in keep]


def _category_options(fields: "list[dict]"):
    """Build the distinct category options, ordered by label."""
    from pywry import Option

    seen: dict[str, str] = {}

    for field in fields:
        seen.setdefault(field["category"], field["category_label"])

    return [
        Option(label=label, value=value)
        for value, label in sorted(seen.items(), key=lambda kv: kv[1].lower())
    ]


def build_screener_content(theme: str = "dark", transport: str = "iframe"):
    """Build the component tree every screener surface shares.

    Parameters
    ----------
    theme : str
        Either 'dark' or 'light'.
    transport : str
        'iframe' fetches results over the builder's own HTTP route, 'bridge'
        emits ``screener:run`` to a PyWry backend and renders the reply.

    Returns
    -------
    tuple
        The content, the toolbars, the modals, and the grid theme.
    """
    from pywry import (
        Button,
        Div,
        HtmlContent,
        Modal,
        NumberInput,
        Option,
        Select,
        TabGroup,
        TextInput,
        Toolbar,
    )
    from pywry.grid import build_grid_config, build_grid_html

    from openbb_tmx.utils.screener_catalog import build_screener_catalog
    from openbb_tmx.utils.screener_presets import list_presets

    try:
        presets = list_presets()
    except Exception:  # noqa: BLE001
        presets = []

    grid_theme = "light" if str(theme).lower() == "light" else "dark"
    catalog = build_screener_catalog()
    fields = catalog["fields"]

    grid_html = build_grid_html(
        build_grid_config(
            [],
            column_defs=COLUMNS,  # ty: ignore[invalid-argument-type]
            grid_id=RESULTS_GRID_ID,
            theme=grid_theme,
            aggrid_theme="balham",
            row_selection=False,
            pagination=True,
            pagination_page_size=50,
        )
    )

    body = (
        '<div class="tmx-screener">'
        '<div class="tmx-conditions" id="tmx-conditions"></div>'
        '<div class="tmx-results-head">'
        '<span class="tmx-results-title">Results</span>'
        '<span id="tmx-status">Add a filter, then apply.</span>'
        '<span id="tmx-count" class="tmx-count"></span>'
        "</div>"
        f'<div class="tmx-grid-wrap">{grid_html}</div>'
        "</div>"
    )

    presets_bar = Toolbar(
        position="top",
        class_name="tmx-presets",
        items=[
            Select(
                component_id="tmx-preset",
                label="Preset",
                event="screener:preset-pick",
                searchable=True,
                options=[Option(label="- Presets -", value="")]
                + [Option(label=p["label"], value=p["name"]) for p in presets],
                selected="",
            ),
            Button(label="New", event="screener:preset-new", variant="secondary"),
            Button(
                label="Save As", event="screener:preset-saveas", variant="secondary"
            ),
            Button(
                label="Delete",
                event="screener:preset-delete-click",
                variant="secondary",
            ),
        ],
    )

    actions = Toolbar(
        position="top",
        class_name="tmx-actions",
        items=[
            TabGroup(
                component_id="tmx-asset",
                event="screener:asset",
                options=[
                    Option(label=a["label"], value=a["value"])
                    for a in catalog["asset_types"]
                ],
                selected=catalog["default_asset"],
            ),
            Button(
                label="+ Add Filter",
                event="screener:open-add-filter",
                variant="secondary",
            ),
            Select(
                component_id="tmx-sort-field",
                label="Sort by",
                event="screener:sortfield",
                searchable=True,
                options=[
                    Option(label=o["label"], value=o["value"])
                    for o in catalog["sort_fields"]
                ],
                selected=catalog["default_sort"],
            ),
            Select(
                component_id="tmx-sort-type",
                label="Order",
                event="screener:sorttype",
                options=[
                    Option(label=s["label"], value=s["value"])
                    for s in catalog["sort_types"]
                ],
                selected="DESC",
            ),
            NumberInput(
                component_id="tmx-limit",
                label="Limit",
                event="screener:limit",
                value=100,
                min=1,
            ),
            Button(label="Reset", event="screener:reset", variant="secondary"),
            Button(label="Apply", event="screener:apply", variant="primary"),
        ],
    )

    add_filter_modal = Modal(
        component_id="tmx-add-filter",
        title="Add Filter",
        size="md",
        reset_on_close=False,
        items=[
            Select(
                component_id="tmx-mf-category",
                label="Category",
                event="screener:mf-category",
                searchable=True,
                options=_category_options(fields),
            ),
            Select(
                component_id="tmx-mf-field",
                label="Filter",
                event="screener:mf-field",
                searchable=True,
                options=[],
            ),
            Select(
                component_id="tmx-mf-operator",
                label="Condition",
                event="screener:mf-operator",
                options=[],
            ),
            Div(
                class_name="tmx-mf-value-wrap",
                content='<div id="tmx-mf-value" class="tmx-mf-value"></div>',
            ),
            Button(label="Add filter", event="screener:add-filter", variant="primary"),
        ],
    )

    save_preset_modal = Modal(
        component_id="tmx-save-preset",
        title="Save Preset",
        size="sm",
        reset_on_close=False,
        items=[
            TextInput(
                component_id="tmx-save-name",
                label="Preset name",
                event="screener:save-name",
                placeholder="my screen",
            ),
            Button(label="Save", event="screener:preset-do-save", variant="primary"),
        ],
    )

    delete_preset_modal = Modal(
        component_id="tmx-delete-preset",
        title="Delete Preset",
        size="sm",
        reset_on_close=False,
        items=[
            Div(
                class_name="tmx-modal-hint",
                content='<span id="tmx-delete-msg">Delete this preset?</span>',
            ),
            Button(
                label="Delete", event="screener:preset-do-delete", variant="primary"
            ),
        ],
    )

    content = HtmlContent(
        html=body,
        inline_css=_CSS.read_text(encoding="utf-8"),
        json_data={
            "assetTypes": catalog["asset_types"],
            "defaultAsset": catalog["default_asset"],
            "fields": fields,
            "operators": catalog["operators"],
            "sortFields": catalog["sort_fields"],
            "defaultSort": catalog["default_sort"],
            "assetDefaults": catalog["asset_defaults"],
            "theme": grid_theme,
            "transport": transport,
            "addFilterModalId": "tmx-add-filter",
            "saveModalId": "tmx-save-preset",
            "deleteModalId": "tmx-delete-preset",
            "presetSelectId": "tmx-preset",
            "presets": presets,
            "resultsGridId": RESULTS_GRID_ID,
            "columnDefsByAsset": COLUMN_DEFS_BY_ASSET,
        },
        init_script=_JS.read_text(encoding="utf-8")
        + _CONNECT.read_text(encoding="utf-8"),
    )
    modals = [add_filter_modal, save_preset_modal, delete_preset_modal]

    return content, [presets_bar, actions], modals, grid_theme


@lru_cache(maxsize=4)
def build_screener_builder_html(theme: str = "dark") -> str:
    """Build the screener-builder page.

    Parameters
    ----------
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    str
        The complete HTML document.
    """
    from pywry.models import ThemeMode, WindowConfig
    from pywry.templates import build_html

    content, toolbars, modals, grid_theme = build_screener_content(
        theme, transport="iframe"
    )

    return build_html(
        content,
        WindowConfig(
            title="OpenBB - TMX Screener Builder",
            theme=ThemeMode.LIGHT if grid_theme == "light" else ThemeMode.DARK,
            enable_aggrid=True,
            aggrid_theme="balham",
        ),
        window_label="tmx_screener_builder",
        toolbars=toolbars,
        modals=modals,
    )
