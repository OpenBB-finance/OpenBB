"""Cboe Options sub-router."""

import logging
from datetime import date as dateType
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

from openbb_cboe import DERIVATIVES_INSTALLED
from openbb_cboe.utils.constants import EQUITY_CHOICES_ENDPOINT, TICKERS_ENDPOINT

_logger = logging.getLogger(__name__)

router = Router(prefix="/options", description="Cboe options data and analysis.")

_SYMBOL_CONFIG = {
    "x-widget_config": {
        "groupId": "symbol",
        "type": "endpoint",
        "optionsEndpoint": EQUITY_CHOICES_ENDPOINT,
        "style": {"popupWidth": 600},
    }
}


def _symbol_query(description: str = "The underlying ticker symbol.") -> Any:
    """Build the shared, group-linked underlying symbol query parameter."""
    return FastAPIQuery(description=description, json_schema_extra=_SYMBOL_CONFIG)


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


def _excluded_query(description: str = "") -> Any:
    """Build a query parameter that is accepted but hidden from the widget UI."""
    return FastAPIQuery(
        description=description,
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


def _column(field: str, header: str, **extra) -> dict:
    """Describe one grid column."""
    return {"field": field, "headerName": header, **extra}


_MONEY = {"cellDataType": "number"}
_PERCENT = {"cellDataType": "number", "formatterFn": "percent"}
_NORMALIZED = {"cellDataType": "number", "formatterFn": "normalizedPercent"}

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

STRADDLE_COLUMNS = [
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
        "source": ["Cboe"],
        "gridData": {"w": 40, "h": height},
        "data": {"table": {"columnsDefs": columns}},
    }


async def _chart_json(builder, symbol: str, theme: str, raw: bool, **kwargs):
    """Load the cached chain, build the view, and return rows or figure JSON."""
    import json

    from fastapi import HTTPException
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.options.data_handler import load_symbol
    from openbb_cboe.utils.options.theme import CHART_CONFIG

    try:
        data = await load_symbol(symbol)
    except OpenBBError as exc:
        _logger.exception("Loading Cboe options data for %s failed", symbol)
        raise HTTPException(
            status_code=404, detail="No options data found for the requested symbol."
        ) from exc

    output = builder(data, theme=theme, **kwargs)

    if raw or output.chart is None:
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

    from openbb_cboe.utils.options.data_handler import (
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


@router.command(
    methods=["GET"],
    widget_config=_table_widget("Straddle", STRADDLE_COLUMNS),
)
async def straddle(
    symbol: Annotated[str, _symbol_query()] = "SPY",
    strike: Annotated[
        float | None, _strike_query("Target strike. Default is nearest OTM.")
    ] = None,
) -> OBBject:
    """Price a long straddle at each expiration."""
    from openbb_cboe.utils.options.data_handler import load_symbol
    from openbb_cboe.utils.options.strategies import to_strategies

    data = await load_symbol(symbol)

    return OBBject(
        results=to_strategies(data.strategies(days=-1, straddle_strike=strike)),
        provider="cboe",
    )


@router.command(
    methods=["GET"],
    widget_config=_table_widget("Strangle", STRADDLE_COLUMNS),
)
async def strangle(
    symbol: Annotated[str, _symbol_query()] = "SPY",
    moneyness: Annotated[
        float,
        FastAPIQuery(description="Percent out-of-the-money for both legs."),
    ] = 5,
) -> OBBject:
    """Price a long strangle at each expiration for a given moneyness."""
    from openbb_cboe.utils.options.data_handler import load_symbol
    from openbb_cboe.utils.options.strategies import to_strategies

    data = await load_symbol(symbol)
    df = data.strategies(days=-1, strangle_moneyness=1 if moneyness == 0 else moneyness)

    return OBBject(results=to_strategies(df), provider="cboe")


@router.command(
    methods=["GET"],
    widget_config=_table_widget("Spreads", SPREAD_COLUMNS),
)
async def spreads(
    symbol: Annotated[str, _symbol_query()] = "SPY",
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
) -> OBBject:
    """Price all four vertical spreads at each expiration."""
    from pandas import concat

    from openbb_cboe.utils.options.data_handler import load_symbol
    from openbb_cboe.utils.options.strategies import to_spreads

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

    frames = [data.strategies(days=-1, **{kind: [legs]}) for kind, legs in specs]

    return OBBject(results=to_spreads(concat(frames)), provider="cboe")


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="CboeOptionsChains",
        widget_config=_table_widget("Chains", CHAIN_COLUMNS, height=16),
        examples=[
            APIEx(
                description="The full options chain for a symbol.",
                parameters={"symbol": "AAPL", "provider": "cboe"},
            )
        ],
    )
    async def chains(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Delayed Cboe options chains, with greeks and implied volatility."""
        return await OBBject.from_query(OBBQuery(**locals()))


async def smile_chart(
    symbol: Annotated[str, _symbol_query()] = "SPY",
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
    from openbb_cboe.utils.options.create_smile import create_smile

    return await _chart_json(
        create_smile, symbol, theme, raw, expirations=expirations, otm=otm, skew=skew
    )


async def surface_chart(
    symbol: Annotated[str, _symbol_query()] = "SPY",
    metric: Annotated[
        Literal[
            "implied_volatility", "delta", "gamma", "theta", "vega", "rho", "dex", "gex"
        ],
        _choice_query(
            "The surface metric. Cboe publishes greeks alongside implied volatility.",
            [
                ("Implied Volatility", "implied_volatility"),
                ("Delta", "delta"),
                ("Gamma", "gamma"),
                ("Theta", "theta"),
                ("Vega", "vega"),
                ("Rho", "rho"),
                ("Delta Exposure", "dex"),
                ("Gamma Exposure", "gex"),
            ],
        ),
    ] = "implied_volatility",
    option_type: Annotated[
        Literal["otm", "itm", "puts", "calls"],
        _choice_query(
            "Which side of the chain to plot.",
            [
                ("Out-Of-The-Money", "otm"),
                ("In-The-Money", "itm"),
                ("Puts", "puts"),
                ("Calls", "calls"),
            ],
        ),
    ] = "otm",
    dte_min: Annotated[
        int | None, FastAPIQuery(description="Minimum days to expiry.")
    ] = None,
    dte_max: Annotated[
        int | None, FastAPIQuery(description="Maximum days to expiry.")
    ] = None,
    moneyness: Annotated[
        float | None,
        FastAPIQuery(description="Percent from the underlying price to include."),
    ] = None,
    oi: Annotated[
        bool, FastAPIQuery(description="Drop contracts with no open interest.")
    ] = False,
    volume: Annotated[
        bool, FastAPIQuery(description="Drop contracts that have not traded.")
    ] = False,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Implied-volatility or greeks 3-D surface over DTE and strike."""
    from openbb_cboe.utils.options.create_surface import create_surface

    dte_range = [dte_min or 0, dte_max or 5000] if (dte_min or dte_max) else None

    return await _chart_json(
        create_surface,
        symbol,
        theme,
        raw,
        option_type=option_type,
        metric=metric,
        dte_range=dte_range,
        moneyness=moneyness,
        oi=oi,
        volume=volume,
    )


async def stats_chart(
    symbol: Annotated[str, _symbol_query()] = "SPY",
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
    from openbb_cboe.utils.options.create_stats import create_stats

    return await _chart_json(
        create_stats, symbol, theme, raw, by=by, metric=metric, date=date, unit=unit
    )


async def term_structure_chart(
    symbol: Annotated[str, _symbol_query()] = "SPY",
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
    """Price or IV term structure across expirations."""
    from openbb_cboe.utils.options.create_term_structure import create_term_structure

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


OPTIMIZER_COLUMNS = [
    _column("strategy_label", "Strategy", pinned="left", cellDataType="text"),
    _column("expiry", "Expiration", cellDataType="text"),
    _column("strike1", "Strike 1", **_MONEY),
    _column("strike2", "Strike 2", **_MONEY),
    _column("current_price", "Current Offer", **_MONEY),
    _column("profit", "Profit At Target", **_MONEY),
    _column("return", "Return At Target", **_NORMALIZED),
    _column("annualized_return", "Annualized Return", **_PERCENT),
    _column("prob_of_profit", "Probability Of Profit", **_NORMALIZED),
    _column("prob_itm", "Probability ITM", **_NORMALIZED),
    _column("prob_of_tgt_price", "Probability Of Target", **_NORMALIZED),
    _column("regt_margin", "Reg-T Margin", **_MONEY),
    _column("target_stock_price", "Target Price", **_MONEY),
]

SENTIMENT_CHOICES = [
    ("Very Bearish", "very_bearish"),
    ("Bearish", "bearish"),
    ("Neutral", "neutral"),
    ("Bullish", "bullish"),
    ("Very Bullish", "very_bullish"),
]

STRATEGY_CHOICES = [
    ("Buy Call Spread", "buy_call_spread"),
    ("Buy Put Spread", "buy_put_spread"),
    ("Sell Call Spread", "sell_call_spread"),
    ("Sell Put Spread", "sell_put_spread"),
    ("Sell Call", "sell_call"),
    ("Sell Put", "sell_put"),
    ("Buy Call", "buy_call"),
    ("Buy Put", "buy_put"),
    ("Buy Straddle", "buy_straddle"),
    ("Sell Straddle", "sell_straddle"),
    ("Buy Strangle", "buy_strangle"),
    ("Sell Strangle", "sell_strangle"),
    ("Call Calendar Spread", "call_calendar"),
    ("Put Calendar Spread", "put_calendar"),
]

STRATEGY_FILTERS = {
    "buy_call_spread": ("Long Spread", "c"),
    "buy_put_spread": ("Long Spread", "p"),
    "sell_call_spread": ("Short Spread", "c"),
    "sell_put_spread": ("Short Spread", "p"),
    "sell_call": ("Naked Short", "c"),
    "sell_put": ("Naked Short", "p"),
    "buy_call": ("Naked Long", "c"),
    "buy_put": ("Naked Long", "p"),
}

ASSEMBLED = {
    "buy_straddle": ("straddle", False, "Buy Straddle"),
    "sell_straddle": ("straddle", True, "Sell Straddle"),
    "buy_strangle": ("strangle", False, "Buy Strangle"),
    "sell_strangle": ("strangle", True, "Sell Strangle"),
    "call_calendar": ("calendar", "c", "Call Calendar Spread"),
    "put_calendar": ("calendar", "p", "Put Calendar Spread"),
}


def _default_expiration(expirations: list[str]) -> str:
    """Return the expiration nearest thirty days out."""
    from openbb_cboe.utils.helpers import ny_today

    if not expirations:
        return ""

    today = ny_today()

    return min(
        expirations,
        key=lambda expiry: abs((dateType.fromisoformat(expiry) - today).days - 30),
    )


def _dte(expiry: str) -> int:
    """Return the days remaining until an expiration."""
    from openbb_cboe.utils.helpers import ny_today

    return max((dateType.fromisoformat(expiry) - ny_today()).days, 0) if expiry else 0


def _describe(info: dict, expiration: str | None) -> dict:
    """Describe the underlying and the expiration being traded."""
    details = info.get("details") or {}
    expirations = info.get("expirations") or []
    expiry = (
        expiration
        if expiration and expiration in expirations
        else _default_expiration(expirations)
    )

    return {
        "spot": float(details.get("current_price") or 0),
        "iv30": float(details.get("iv30") or 0),
        "dte": _dte(expiry),
        "expiry": expiry,
        "expirations": expirations,
    }


async def _optimize(
    symbol: str,
    expiration: str | None,
    sentiment: str,
    target: float | None,
) -> tuple[list[dict], dict]:
    """Rank every strategy for a symbol, and describe the underlying.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    expiration : str | None
        The expiration to trade. Defaults to the nearest one.
    sentiment : str
        The view the target price is derived from.
    target : float | None
        An explicit target price, overriding the sentiment.
    """
    from openbb_cboe.utils.options.trade_optimizer import (
        get_strategies,
        get_symbol_info,
        target_price,
    )

    info = await get_symbol_info(symbol)
    context = _describe(info, expiration)
    price = target or target_price(
        context["spot"], context["iv30"], context["dte"], sentiment
    )
    rows = await get_strategies(symbol, context["expiry"], price)

    return rows, context


def _targets(spot: float, moneyness: float = 0.0) -> list[float]:
    """Return the target prices that quote the strikes a position needs."""
    if not moneyness:
        return [spot * 0.9, spot, spot * 1.1]

    low, high = spot * (1 - moneyness), spot * (1 + moneyness)

    return [low * 0.97, low, spot, high, high * 1.03]


async def _quote_book(symbol: str, expiry: str, targets: list[float]) -> dict:
    """Collect every single-leg quote the optimizer names at a set of targets.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    expiry : str
        The expiration to quote.
    targets : list[float]
        The target prices to ask about.
    """
    from asyncio import create_task, gather

    from openbb_cboe.utils.options.data_handler import get_chain_marks
    from openbb_cboe.utils.options.legs import naked_quotes
    from openbb_cboe.utils.options.trade_optimizer import get_strategies

    chain = create_task(get_chain_marks(symbol, expiry))
    responses = await gather(
        *[get_strategies(symbol, expiry, round(target, 2)) for target in targets]
    )
    marks = await chain
    marks["dte"] = marks.get("dte") or _dte(expiry)
    quotes: dict = {}

    for rows in responses:
        for key, quote in naked_quotes(rows, marks).items():
            quotes.setdefault(key, quote)

    return {
        "quotes": quotes,
        "forward": marks["forward"],
        "discount": marks["discount"],
        "dte": marks["dte"],
    }


def _far_expiration(expirations: list[str], near: str) -> str:
    """Return the expiration a month past the one being traded."""
    later = [expiry for expiry in expirations if expiry > near]

    if not later:
        return near

    return min(later, key=lambda expiry: abs(_dte(expiry) - _dte(near) - 30))


async def _naked(symbol: str, wanted: tuple, context: dict) -> dict:
    """Quote a single contract the ranked results left out."""
    from openbb_cboe.utils.options.create_payoff import STRATEGY_LABELS
    from openbb_cboe.utils.options.legs import build_naked

    strategy, option_type = wanted
    spot = context["spot"]
    book = await _quote_book(symbol, context["expiry"], _targets(spot))
    position = build_naked(
        book, context["spot"], option_type, sell=strategy == "Naked Short"
    )
    position["label"] = STRATEGY_LABELS.get(wanted, strategy)

    return position


async def _assemble(
    symbol: str,
    strategy: str,
    context: dict,
    far_expiration: str | None,
    moneyness: float,
) -> dict:
    """Build a position the optimizer prices but does not rank.

    Raises
    ------
    OpenBBError
        If the second expiration of a calendar is the one already traded.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.options.legs import (
        build_calendar,
        build_straddle,
        build_strangle,
    )

    kind, variant, label = ASSEMBLED[strategy]
    spot = context["spot"]
    targets = _targets(spot, moneyness / 100 if kind == "strangle" else 0)
    near = await _quote_book(symbol, context["expiry"], targets)

    if kind == "straddle":
        position = build_straddle(near, spot, sell=bool(variant))
    elif kind == "strangle":
        position = build_strangle(near, spot, moneyness / 100, sell=bool(variant))
    else:
        expiry = (
            far_expiration
            if far_expiration and far_expiration in context["expirations"]
            else _far_expiration(context["expirations"], context["expiry"])
        )

        if expiry == context["expiry"]:
            raise OpenBBError(
                "A calendar spread needs a second expiration to sell against."
            )

        far = await _quote_book(symbol, expiry, targets)
        position = build_calendar(near, far, spot, option_type=str(variant))

    position["label"] = label

    return position


@router.command(
    methods=["GET"],
    widget_config=_table_widget("Trade Optimizer", OPTIMIZER_COLUMNS, height=16),
)
async def trade_optimizer(
    symbol: Annotated[str, _symbol_query()] = "SPY",
    expiration: Annotated[str | None, _expiry_query("The expiration to trade.")] = None,
    sentiment: Annotated[
        Literal["very_bearish", "bearish", "neutral", "bullish", "very_bullish"],
        _choice_query("The view the target price is derived from.", SENTIMENT_CHOICES),
    ] = "neutral",
    target_price: Annotated[
        float | None,
        FastAPIQuery(description="An explicit target price, overriding the sentiment."),
    ] = None,
) -> list[dict]:
    """Rank the option strategies that reach a target price by an expiration."""
    from openbb_cboe.utils.options.create_payoff import STRATEGY_LABELS

    rows, _ = await _optimize(symbol, expiration, sentiment, target_price)

    for row in rows:
        row["strategy_label"] = STRATEGY_LABELS.get(
            (row.get("strategy"), row.get("type")), row.get("strategy")
        )

    rows.sort(key=lambda row: row.get("return") or 0, reverse=True)
    fields = [column["field"] for column in OPTIMIZER_COLUMNS]

    return [{field: row.get(field) for field in fields} for row in rows]


async def payoff_chart(
    symbol: Annotated[str, _symbol_query()] = "SPY",
    expiration: Annotated[str | None, _expiry_query("The expiration to trade.")] = None,
    sentiment: Annotated[
        Literal["very_bearish", "bearish", "neutral", "bullish", "very_bullish"],
        _choice_query("The view the target price is derived from.", SENTIMENT_CHOICES),
    ] = "neutral",
    strategy: Annotated[
        str,
        _choice_query("The strategy to draw.", STRATEGY_CHOICES),
    ] = "buy_call_spread",
    target_price: Annotated[
        float | None,
        FastAPIQuery(description="An explicit target price, overriding the sentiment."),
    ] = None,
    rank: Annotated[
        int, FastAPIQuery(description="Which ranked strategy to draw, best first.")
    ] = 1,
    far_expiration: Annotated[
        str | None,
        _expiry_query("The long expiration of a calendar spread."),
    ] = None,
    moneyness: Annotated[
        float,
        FastAPIQuery(description="Percent out-of-the-money for each strangle wing."),
    ] = 5,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw the payoff of one optimized strategy at expiration."""
    import json

    from fastapi import HTTPException
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.options.create_payoff import create_payoff
    from openbb_cboe.utils.options.theme import CHART_CONFIG
    from openbb_cboe.utils.options.trade_optimizer import (
        get_symbol_info,
        target_price as implied_target,
    )

    data: dict = {"symbol": symbol.upper()}

    try:
        if strategy in ASSEMBLED:
            context = _describe(await get_symbol_info(symbol), expiration)
            data["position"] = await _assemble(
                symbol, strategy, context, far_expiration, moneyness
            )
            data["target"] = target_price or implied_target(
                context["spot"], context["iv30"], context["dte"], sentiment
            )
        else:
            rows, context = await _optimize(symbol, expiration, sentiment, target_price)
            wanted = STRATEGY_FILTERS.get(strategy, ("Long Spread", "c"))
            matches = [
                row
                for row in rows
                if (row.get("strategy"), row.get("type")) == wanted
                and (wanted[0].startswith("Naked") or row.get("strike2"))
            ]

            if matches:
                data["strategy"] = matches[min(max(rank, 1), len(matches)) - 1]
            elif wanted[0].startswith("Naked"):
                data["position"] = await _naked(symbol, wanted, context)
            else:
                raise OpenBBError(
                    f"The optimizer returned no {strategy} for this view of {symbol}."
                )

        data["spot"] = context["spot"]
        output = create_payoff(data, theme=theme)
    except OpenBBError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    figure = output.chart.fig if output.chart else None

    if raw or figure is None:
        return [r.model_dump() for r in (output.results or [])]

    figure_json = json.loads(figure.to_json())
    figure_json["config"] = CHART_CONFIG

    return figure_json


CHART_ROUTES = (
    ("/smile", smile_chart, "Cboe Options Smile"),
    ("/surface", surface_chart, "Cboe Options Surface"),
    ("/stats", stats_chart, "Cboe Options Stats"),
    ("/term_structure", term_structure_chart, "Cboe Options Term Structure"),
    ("/payoff", payoff_chart, "Trade Optimizer Payoff"),
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
            "source": ["Cboe"],
            "gridData": {"w": 40, "h": 18},
            "refetchInterval": False,
        }
    }


for _path, _endpoint, _name in CHART_ROUTES:
    router.api_router.add_api_route(
        path=_path,
        endpoint=_endpoint,
        methods=["GET"],
        openapi_extra=_chart_widget(_name),
    )
