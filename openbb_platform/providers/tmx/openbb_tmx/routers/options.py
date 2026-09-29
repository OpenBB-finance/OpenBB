"""TMX Options sub-router."""

import logging
from typing import Annotated, Any, Literal

from fastapi import Query as FastAPIQuery
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_tmx import CHARTING_INSTALLED, DERIVATIVES_INSTALLED
from openbb_tmx.utils.choices import api_prefix

_logger = logging.getLogger(__name__)

TICKERS_ENDPOINT = f"{api_prefix()}/tmx/derivatives/options/get_tickers"

router = Router(prefix="/options", description="TMX options data and analysis.")


def _symbol_query() -> Any:
    """Build the underlying symbol query parameter."""
    return FastAPIQuery(
        description="The underlying symbol. Suffix with ':US' for OPRA-listed"
        + " contracts; a bare symbol resolves to the Montreal Exchange listing."
    )


def _column(field: str, header: str, **extra) -> dict:
    """Describe one grid column."""
    return {"field": field, "headerName": header, **extra}


_MONEY = {"cellDataType": "number"}
_PERCENT = {"cellDataType": "number", "formatterFn": "percent"}

CHAIN_COLUMNS = [
    _column("expiration", "Expiration", pinned="left", cellDataType="text"),
    _column("dte", "DTE", cellDataType="number"),
    _column("strike", "Strike", **_MONEY),
    _column("option_type", "Type", cellDataType="text"),
    _column("contract_symbol", "Contract", cellDataType="text"),
    _column("open_interest", "OI", cellDataType="number"),
    _column("volume", "Volume", cellDataType="number"),
    _column("last_trade_price", "Last", **_MONEY),
    _column("bid", "Bid", **_MONEY),
    _column("ask", "Ask", **_MONEY),
    _column("change", "Change", **_MONEY),
    _column("change_percent", "Change %", **_PERCENT),
    _column("implied_volatility", "IV", cellDataType="number"),
    _column("delta", "Delta", cellDataType="number"),
    _column("gamma", "Gamma", cellDataType="number"),
    _column("theta", "Theta", cellDataType="number"),
    _column("vega", "Vega", cellDataType="number"),
    _column("rho", "Rho", cellDataType="number"),
    _column("underlying_symbol", "Underlying", cellDataType="text"),
    _column("underlying_price", "Underlying Price", **_MONEY),
]

_STRATEGY_TAIL = [
    _column("underlying_price", "Underlying Price", **_MONEY),
    _column("cost", "Cost", **_MONEY),
    _column("cost_percent", "Cost %", **_PERCENT),
    _column("max_profit", "Max Profit", **_MONEY),
    _column("max_loss", "Max Loss", **_MONEY),
    _column("breakeven_lower", "Breakeven Lower", **_MONEY),
    _column("breakeven_lower_percent", "Breakeven Lower %", **_PERCENT),
    _column("breakeven_upper", "Breakeven Upper", **_MONEY),
    _column("breakeven_upper_percent", "Breakeven Upper %", **_PERCENT),
]

STRATEGY_COLUMNS = [
    _column("expiration", "Expiration", pinned="left", cellDataType="text"),
    _column("dte", "DTE", cellDataType="number"),
    _column("strike_1", "Strike 1", **_MONEY),
    _column("strike_2", "Strike 2", **_MONEY),
    _column("strike_1_premium", "Strike 1 Premium", **_MONEY),
    _column("strike_2_premium", "Strike 2 Premium", **_MONEY),
] + _STRATEGY_TAIL

SPREAD_COLUMNS = [
    _column("strategy", "Strategy", pinned="left", cellDataType="text"),
    _column("expiration", "Expiration", cellDataType="text"),
    _column("dte", "DTE", cellDataType="number"),
    _column("sold_strike", "Sold Strike", **_MONEY),
    _column("bought_strike", "Bought Strike", **_MONEY),
    _column("sold_premium", "Sold Premium", **_MONEY),
    _column("bought_premium", "Bought Premium", **_MONEY),
] + _STRATEGY_TAIL


def _table_widget(name: str, columns: list[dict], height: int = 12) -> dict:
    """Build the Workspace table-widget config for an options view."""
    return {
        "name": name,
        "category": "Derivatives",
        "subCategory": "Options",
        "source": ["TMX"],
        "gridData": {"w": 40, "h": height},
        "data": {"table": {"columnsDefs": columns}},
    }


def _expiry_query(description: str, multi: bool = False) -> Any:
    """Build an expiration query parameter backed by the tickers endpoint."""
    config: dict = {
        "type": "endpoint",
        "optionsEndpoint": TICKERS_ENDPOINT,
        "optionsParams": {"expiry_list": True, "symbol": "$symbol"},
    }

    if multi:
        config["multiSelect"] = True

    return FastAPIQuery(
        description=description, json_schema_extra={"x-widget_config": config}
    )


def _strike_query(description: str) -> Any:
    """Build a strike query parameter backed by the tickers endpoint."""
    return FastAPIQuery(
        description=description,
        json_schema_extra={
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": TICKERS_ENDPOINT,
                "optionsParams": {"strike_list": True, "symbol": "$symbol"},
            }
        },
    )


def _choice_query(description: str, options: list[tuple[str, str]]) -> Any:
    """Build a query parameter rendered as a labelled dropdown."""
    return FastAPIQuery(
        description=description,
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"label": label, "value": value} for label, value in options
                ]
            }
        },
    )


def _strategies(data, **kwargs):
    """Price one set of strategies over a loaded chain.

    Parameters
    ----------
    data : OptionsChainsData
        The loaded chain.
    **kwargs : Any
        The legs to price, as ``OptionsChainsData.strategies`` accepts them.

    Returns
    -------
    DataFrame
        The priced strategies, empty when the chain qualifies none.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import DataFrame
    from pandas.errors import UndefinedVariableError

    try:
        return data.strategies(**kwargs)
    except (OpenBBError, UndefinedVariableError):
        return DataFrame()


def _excluded_query(description: str = "") -> Any:
    """Build a query parameter that is accepted but hidden from the widget UI."""
    return FastAPIQuery(
        description=description,
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


@router.command(
    methods=["GET"],
    widget_config=_table_widget("TMX Options Straddle", STRATEGY_COLUMNS),
    examples=[
        APIEx(
            description="Long straddle cost at each expiration.",
            parameters={"symbol": "AC"},
        )
    ],
)
async def straddle(
    symbol: Annotated[str, _symbol_query()] = "AC",
    strike: Annotated[
        float | None, _strike_query("Target strike. Default is nearest OTM.")
    ] = None,
) -> list[dict]:
    """Price a long straddle at each expiration."""
    from openbb_tmx.utils.options.data_handler import load_symbol
    from openbb_tmx.utils.options.strategies import to_strategies

    data = await load_symbol(symbol)

    return [
        row.model_dump()
        for row in to_strategies(_strategies(data, days=-1, straddle_strike=strike))
    ]


@router.command(
    methods=["GET"],
    widget_config=_table_widget("TMX Options Strangle", STRATEGY_COLUMNS),
    examples=[
        APIEx(
            description="Long strangle cost at each expiration.",
            parameters={"symbol": "AC"},
        )
    ],
)
async def strangle(
    symbol: Annotated[str, _symbol_query()] = "AC",
    moneyness: Annotated[
        float,
        FastAPIQuery(description="Percent out-of-the-money for both legs."),
    ] = 5,
) -> list[dict]:
    """Price a long strangle at each expiration for a given moneyness."""
    from openbb_tmx.utils.options.data_handler import load_symbol
    from openbb_tmx.utils.options.strategies import to_strategies

    data = await load_symbol(symbol)
    frame = _strategies(
        data, days=-1, strangle_moneyness=1 if moneyness == 0 else moneyness
    )

    return [row.model_dump() for row in to_strategies(frame)]


@router.command(
    methods=["GET"],
    widget_config=_table_widget("TMX Options Spreads", SPREAD_COLUMNS),
    examples=[
        APIEx(
            description="Vertical spreads at each expiration.",
            parameters={"symbol": "AC", "spread_type": "call"},
        )
    ],
)
async def spreads(
    symbol: Annotated[str, _symbol_query()] = "AC",
    spread_type: Annotated[
        Literal["call", "put", "both"],
        _choice_query(
            "Vertical call spreads, put spreads, or both.",
            [("Call Spreads", "call"), ("Put Spreads", "put"), ("Both", "both")],
        ),
    ] = "both",
    near_moneyness: Annotated[
        float,
        FastAPIQuery(description="Percent out-of-the-money for the near leg."),
    ] = 2.5,
    far_moneyness: Annotated[
        float,
        FastAPIQuery(description="Percent out-of-the-money for the far leg."),
    ] = 7.5,
) -> list[dict]:
    """Price the vertical spreads at each expiration."""
    from pandas import concat

    from openbb_tmx.utils.options.data_handler import load_symbol
    from openbb_tmx.utils.options.strategies import to_spreads

    data = await load_symbol(symbol)
    last = data.underlying_price[0]
    near_m, far_m = near_moneyness / 100, far_moneyness / 100
    near_call, far_call = last * (1 + near_m), last * (1 + far_m)
    near_put, far_put = last * (1 - near_m), last * (1 - far_m)
    specs: list = []

    if spread_type in ("call", "both"):
        specs += [
            ("vertical_calls", (far_call, near_call)),
            ("vertical_calls", (near_call, far_call)),
        ]

    if spread_type in ("put", "both"):
        specs += [
            ("vertical_puts", (near_put, far_put)),
            ("vertical_puts", (far_put, near_put)),
        ]

    frames = [
        frame
        for kind, legs in specs
        if not (frame := _strategies(data, days=-1, **{kind: [legs]})).empty
    ]

    if not frames:
        return []

    return [row.model_dump() for row in to_spreads(concat(frames))]


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="TmxOptionsChains",
        widget_config=_table_widget("TMX Options Chains", CHAIN_COLUMNS, height=16),
        examples=[
            APIEx(
                description="The full options chain for a symbol.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def chains(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Complete option chain across every expiry, with greeks."""
        return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="CoveredCallScreener",
    examples=[
        APIEx(
            description="Screen listed calls for covered-write returns.",
            parameters={"provider": "tmx"},
        )
    ],
)
async def covered_calls(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Screen listed calls by annualized premium return and potential capital gain."""
    return await OBBject.from_query(OBBQuery(**locals()))


async def _load_chain(symbol: str, use_cache: bool = True):
    """Load a validated options chain for the symbol.

    Parameters
    ----------
    symbol : str
        The underlying symbol.
    use_cache : bool
        Whether to use the on-disk response cache.

    Returns
    -------
    TmxOptionsChainsData
        The chain, carrying the analytics from the standard model.
    """
    from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher

    return await TmxOptionsChainsFetcher.fetch_data(
        {"symbol": symbol, "use_cache": use_cache}, {}
    )


async def _chart_json(builder, symbol: str, theme: str, raw: bool, **kwargs):
    """Load the cached chain, build the view, and return rows or figure JSON."""
    import json

    from fastapi import HTTPException
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.options.data_handler import load_symbol
    from openbb_tmx.utils.options.theme import CHART_CONFIG

    try:
        data = await load_symbol(symbol)
    except OpenBBError as exc:
        _logger.exception("Loading TMX options data for %s failed", symbol)
        raise HTTPException(
            status_code=404, detail="No options data found for the requested symbol."
        ) from exc

    output = builder(data, theme=theme, **kwargs)

    if raw:
        return [r.model_dump() for r in (output.results or [])]

    figure_json = json.loads(output.chart.fig.to_json())
    figure_json["config"] = CHART_CONFIG

    return figure_json


@router.command(methods=["GET"], widget_config={"exclude": True})
async def get_tickers(
    symbol: str = "",
    expiry_list: bool = False,
    strike_list: bool = False,
) -> list:
    """Serve expiry/strike dropdown choices for a symbol, loading it on first call."""
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.options.data_handler import (
        get_expirations,
        get_strikes,
        load_symbol,
    )

    if not symbol:
        return []

    try:
        await load_symbol(symbol)
    except OpenBBError:
        return []

    if expiry_list:
        return get_expirations(symbol)

    if strike_list:
        return get_strikes(symbol)

    return []


async def smile_chart(
    symbol: Annotated[str, _symbol_query()] = "AC",
    expirations: Annotated[
        str | None,
        _expiry_query("Up to five expiration dates (comma-separated).", multi=True),
    ] = None,
    otm: Annotated[
        bool, FastAPIQuery(description="Show only out-of-the-money contracts.")
    ] = False,
    skew: Annotated[
        bool, FastAPIQuery(description="Plot skew relative to ATM instead of IV.")
    ] = False,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Implied-volatility smile / skew across strikes."""
    from openbb_tmx.utils.options.create_smile import create_smile

    return await _chart_json(
        create_smile, symbol, theme, raw, expirations=expirations, otm=otm, skew=skew
    )


async def surface_chart(
    symbol: Annotated[str, _symbol_query()] = "AC",
    metric: Annotated[
        str,
        _choice_query(
            "The surface to plot.",
            [
                ("Implied Volatility", "implied_volatility"),
                ("Last Price", "last_trade_price"),
                ("Open Interest", "open_interest"),
                ("Volume", "volume"),
            ],
        ),
    ] = "implied_volatility",
    option_type: Annotated[
        Literal["otm", "itm", "calls", "puts"],
        _choice_query(
            "The contracts to plot.",
            [
                ("Out Of The Money", "otm"),
                ("In The Money", "itm"),
                ("Calls", "calls"),
                ("Puts", "puts"),
            ],
        ),
    ] = "otm",
    dte_min: Annotated[
        int | None, FastAPIQuery(description="Minimum days until expiration.")
    ] = None,
    dte_max: Annotated[
        int | None, FastAPIQuery(description="Maximum days until expiration.")
    ] = None,
    moneyness: Annotated[
        float | None,
        FastAPIQuery(description="Percent from the underlying price to include."),
    ] = None,
    strike_min: Annotated[
        float | None, FastAPIQuery(description="Lowest strike to include.")
    ] = None,
    strike_max: Annotated[
        float | None, FastAPIQuery(description="Highest strike to include.")
    ] = None,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Plot the chain as a surface over days to expiry and strike."""
    from openbb_tmx.utils.options.create_surface import create_surface

    return await _chart_json(
        create_surface,
        symbol,
        theme,
        raw,
        metric=metric,
        option_type=option_type,
        dte_min=dte_min,
        dte_max=dte_max,
        moneyness=moneyness,
        strike_min=strike_min,
        strike_max=strike_max,
    )


async def stats_chart(
    symbol: Annotated[str, _symbol_query()] = "AC",
    by: Annotated[
        Literal["strike", "expiration"],
        _choice_query(
            "Aggregate by strike or expiration.",
            [("Expiration", "expiration"), ("Strike", "strike")],
        ),
    ] = "expiration",
    metric: Annotated[
        Literal["oi", "volume"],
        _choice_query(
            "Open interest or volume.",
            [("Open Interest", "oi"), ("Volume", "volume")],
        ),
    ] = "oi",
    date: Annotated[
        str | None,
        _expiry_query("Expiry to view by strike (switches 'by' to strike)."),
    ] = None,
    unit: Annotated[
        Literal["value", "percent", "pcr"],
        _choice_query(
            "Raw values, share of total, or put/call ratio.",
            [("Value", "value"), ("Percent", "percent"), ("Put/Call Ratio", "pcr")],
        ),
    ] = "value",
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Open-interest or volume statistics by strike or expiration."""
    from openbb_tmx.utils.options.create_stats import create_stats

    return await _chart_json(
        create_stats, symbol, theme, raw, by=by, metric=metric, date=date, unit=unit
    )


async def term_structure_chart(
    symbol: Annotated[str, _symbol_query()] = "AC",
    strike: Annotated[
        float | None, _strike_query("Target strike. Default is nearest OTM per expiry.")
    ] = None,
    moneyness: Annotated[
        float | None,
        FastAPIQuery(description="Percent out-of-the-money instead of a fixed strike."),
    ] = None,
    metric: Annotated[
        Literal["iv", "price"],
        _choice_query(
            "Implied volatility or price.",
            [("Implied Volatility", "iv"), ("Price", "price")],
        ),
    ] = "iv",
    option_type: Annotated[
        Literal["both", "calls", "puts"],
        _choice_query(
            "Which side of the chain to plot.",
            [("Both", "both"), ("Calls", "calls"), ("Puts", "puts")],
        ),
    ] = "both",
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Implied volatility or price across expirations."""
    from openbb_tmx.utils.options.create_term_structure import create_term_structure

    return await _chart_json(
        create_term_structure,
        symbol,
        theme,
        raw,
        strike=strike,
        moneyness=moneyness,
        metric=metric,
        option_type=option_type,
    )


CHART_ROUTES = (
    ("/smile", smile_chart, "TMX Options Smile"),
    ("/surface", surface_chart, "TMX Options Surface"),
    ("/stats", stats_chart, "TMX Options Stats"),
    ("/term_structure", term_structure_chart, "TMX Options Term Structure"),
)


def _chart_widget(name: str) -> dict:
    """Build the Workspace chart-widget config for a Plotly route."""
    return {
        "widget_config": {
            "name": name,
            "type": "chart",
            "raw": True,
            "category": "Derivatives",
            "subCategory": "Options",
            "source": ["TMX"],
            "gridData": {"w": 40, "h": 18},
            "refetchInterval": False,
        }
    }


if CHARTING_INSTALLED:
    for _path, _endpoint, _name in CHART_ROUTES:
        router.api_router.add_api_route(
            path=_path,
            endpoint=_endpoint,
            methods=["GET"],
            openapi_extra=_chart_widget(_name),
        )
