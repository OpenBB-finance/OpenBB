"""Deribit Options sub-router."""

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

from openbb_deribit import DERIVATIVES_INSTALLED
from openbb_deribit.utils.constants import (
    EXPIRATION_CHOICES_ENDPOINT,
    STRATEGY_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    UNDERLYING_CHOICES_ENDPOINT,
)

_logger = logging.getLogger(__name__)

router = Router(prefix="/options", description="Deribit options data and analysis.")

SURFACE_MEASURES = Literal[
    "implied_volatility", "delta", "gamma", "theta", "vega", "rho"
]
GROUPED_BY = Literal["strike", "expiration"]

_UNDERLYING = {
    "x-widget_config": {
        "groupId": "deribit_underlying",
        "type": "endpoint",
        "optionsEndpoint": UNDERLYING_CHOICES_ENDPOINT,
        "style": SYMBOL_STYLE,
    }
}


def _underlying() -> Any:
    """Build the shared, group-linked underlying parameter."""
    return FastAPIQuery(
        description="The underlying root, as it appears in the instrument name.",
        json_schema_extra=_UNDERLYING,
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
_COUNT = {"cellDataType": "number"}
_NORMALIZED = {"cellDataType": "number", "formatterFn": "normalizedPercent"}

_PERCENT = {"cellDataType": "number", "formatterFn": "percent"}

_STRATEGY_TAIL = [
    _column("cost", "Cost", **_MONEY),
    _column("cost_percent", "Cost %", **_NORMALIZED),
    _column("max_loss", "Max Loss", **_MONEY),
    _column("breakeven_lower", "Breakeven Lower", **_MONEY),
    _column("breakeven_upper", "Breakeven Upper", **_MONEY),
]

CHAIN_COLUMNS = [
    _column("contract_symbol", "Contract", pinned="left", cellDataType="text"),
    _column("expiration", "Expiration", cellDataType="text"),
    _column("dte", "DTE", **_COUNT),
    _column("strike", "Strike", **_MONEY),
    _column("option_type", "Type", cellDataType="text"),
    _column("open_interest", "OI", **_COUNT),
    _column("volume", "Volume", **_COUNT),
    _column("volume_notional", "Volume Notional", **_MONEY),
    _column("bid", "Bid", **_MONEY),
    _column("bid_size", "Bid Size", **_COUNT),
    _column("ask", "Ask", **_MONEY),
    _column("ask_size", "Ask Size", **_COUNT),
    _column("mark", "Mark", **_MONEY),
    _column("last_trade_price", "Last", **_MONEY),
    _column("high", "High", **_MONEY),
    _column("low", "Low", **_MONEY),
    _column("change_percent", "Change %", **_PERCENT, renderFn="greenRed"),
    _column("implied_volatility", "Mark IV", **_PERCENT),
    _column("bid_iv", "Bid IV", **_PERCENT),
    _column("ask_iv", "Ask IV", **_PERCENT),
    _column("delta", "Delta", cellDataType="number"),
    _column("gamma", "Gamma", cellDataType="number"),
    _column("theta", "Theta", cellDataType="number"),
    _column("vega", "Vega", cellDataType="number"),
    _column("rho", "Rho", cellDataType="number"),
    _column("settlement_price", "Settlement Price", **_MONEY),
    _column("min_price", "Min Price", **_MONEY),
    _column("max_price", "Max Price", **_MONEY),
    _column("interest_rate", "Interest Rate", **_PERCENT),
    _column("contract_size", "Contract Size", **_COUNT),
    _column("is_inverse", "Is Inverse", cellDataType="boolean"),
    _column("underlying_symbol", "Underlying", cellDataType="text"),
    _column("underlying_price", "Underlying Forward", **_MONEY),
    _column("underlying_spot_price", "Underlying Spot", **_MONEY),
    _column("timestamp", "Timestamp", cellDataType="text"),
]

OPTIMIZER_COLUMNS = [
    _column("strategy", "Strategy", pinned="left", cellDataType="text"),
    _column(
        "legs",
        "Legs",
        cellDataType="text",
        formatterFn="none",
        renderFn="cellOnClick",
        renderFnParams={
            "actionType": "groupBy",
            "groupBy": {"paramName": "legs"},
        },
    ),
    _column("contracts", "Contracts", **_COUNT),
    _column("cost", "Cost", **_MONEY),
    _column("expected_profit", "Expected Profit", **_MONEY, renderFn="greenRed"),
    _column("expected_return", "Expected Return", **_NORMALIZED, renderFn="greenRed"),
    _column("max_profit", "Max Profit", **_MONEY),
    _column("max_loss", "Max Loss", **_MONEY),
    _column("breakeven_lower", "Breakeven Lower", **_MONEY),
    _column("breakeven_upper", "Breakeven Upper", **_MONEY),
]

STRADDLE_COLUMNS = [
    _column("expiration", "Expiration", pinned="left", cellDataType="text"),
    _column("dte", "DTE", **_COUNT),
    _column("underlying_price", "Underlying Price", **_MONEY),
    _column("strike", "Strike", **_MONEY),
    _column("call_premium", "Call Premium", **_MONEY),
    _column("put_premium", "Put Premium", **_MONEY),
] + _STRATEGY_TAIL

STRANGLE_COLUMNS = [
    _column("expiration", "Expiration", pinned="left", cellDataType="text"),
    _column("dte", "DTE", **_COUNT),
    _column("underlying_price", "Underlying Price", **_MONEY),
    _column("put_strike", "Put Strike", **_MONEY),
    _column("call_strike", "Call Strike", **_MONEY),
    _column("call_premium", "Call Premium", **_MONEY),
    _column("put_premium", "Put Premium", **_MONEY),
] + _STRATEGY_TAIL

SPREAD_COLUMNS = [
    _column("strategy", "Strategy", pinned="left", cellDataType="text"),
    _column("expiration", "Expiration", cellDataType="text"),
    _column("dte", "DTE", **_COUNT),
    _column("underlying_price", "Underlying Price", **_MONEY),
    _column("bought_strike", "Bought Strike", **_MONEY),
    _column("sold_strike", "Sold Strike", **_MONEY),
    _column("bought_premium", "Bought Premium", **_MONEY),
    _column("sold_premium", "Sold Premium", **_MONEY),
    _column("cost", "Cost", **_MONEY),
    _column("cost_percent", "Cost %", **_NORMALIZED),
    _column("max_profit", "Max Profit", **_MONEY),
    _column("max_loss", "Max Loss", **_MONEY),
    _column("breakeven", "Breakeven", **_MONEY),
]


def _table_widget(name: str, description: str, columns: list, height: int = 16) -> dict:
    """Build the Workspace table-widget config for an analysis view."""
    return {
        "name": f"Deribit {name}",
        "description": description,
        "category": "Crypto",
        "subCategory": "Options",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": height},
        "data": {"table": {"columnsDefs": columns}},
    }


def _chart_widget(name: str, description: str, height: int = 18) -> dict:
    """Build the Workspace chart-widget config for a Plotly route."""
    return {
        "widget_config": {
            "name": f"Deribit {name}",
            "description": description,
            "type": "chart",
            "raw": True,
            "category": "Crypto",
            "subCategory": "Options",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": height},
            "refetchInterval": False,
        }
    }


async def _loaded(symbol: str) -> tuple:
    """Return the chain, its spot price, and how it settles."""
    from openbb_deribit.utils.options.chain import (
        is_inverse,
        load_chain,
        settlement_currency,
        underlying_price,
    )

    frame = await load_chain(symbol)

    return (
        frame,
        underlying_price(frame),
        is_inverse(frame),
        settlement_currency(frame, symbol),
    )


def _figure_json(output: Any, raw: bool) -> Any:
    """Return the drawn figure, or the rows behind it when raw is asked for.

    Parameters
    ----------
    output : Any
        The OBBject a view returned.
    raw : bool
        Whether the widget's raw toggle is on.

    Returns
    -------
    Any
        The Plotly figure as plain JSON, or the list of rows.
    """
    import json

    from openbb_deribit.utils.options.theme import CHART_CONFIG

    if raw or output.chart is None:
        return [row.model_dump() for row in (output.results or [])]

    figure_json = json.loads(output.chart.fig.to_json())
    figure_json["config"] = CHART_CONFIG

    return figure_json


async def _chain_or_404(symbol: str) -> tuple:
    """Load a chain, answering 404 when the exchange lists none.

    Raises
    ------
    HTTPException
        If the exchange publishes no option quotes for the underlying.
    """
    from fastapi import HTTPException
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        return await _loaded(symbol)
    except OpenBBError as exc:
        _logger.exception("Loading the Deribit option chain for %s failed", symbol)

        raise HTTPException(
            status_code=404,
            detail=f"Deribit lists no options on {symbol}.",
        ) from exc


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the underlyings with listed options.", parameters={})
    ],
)
async def underlying_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of every underlying with listed options."""
    from openbb_deribit.utils.choices import options_root_choices

    return await options_root_choices()


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the expirations listed on an underlying.",
            parameters={"symbol": "BTC"},
        )
    ],
)
async def expiration_choices(
    symbol: Annotated[str, _underlying()] = "BTC",
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every expiration the underlying lists."""
    from openbb_deribit.utils.options.chain import expirations, load_chain

    frame = await load_chain(symbol)

    return [
        {
            "label": f"{day}  ({int(frame[frame['expiration'] == day]['dte'].iloc[0])}d)",
            "value": str(day),
        }
        for day in expirations(frame)
    ]


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="DeribitOptionsChains",
        widget_config={
            "name": "Deribit Options Chains",
            "description": "The full option chain of an underlying, with greeks and"
            + " implied volatility.",
            "category": "Crypto",
            "subCategory": "Options",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": 20},
            "params": [{"paramName": "symbol", "value": "BTC"}],
            "data": {"table": {"columnsDefs": CHAIN_COLUMNS}},
        },
        examples=[
            APIEx(
                description="The full BTC option chain.",
                parameters={"symbol": "BTC", "provider": "deribit"},
            )
        ],
    )
    async def chains(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the full Deribit option chain of an underlying, with greeks."""
        return await OBBject.from_query(OBBQuery(**locals()))


def _quote(symbol: str) -> str:
    """Return the currency a position in this underlying is priced in."""
    return "USDC" if symbol.upper().endswith("_USDC") else "USD"


def _named(legs: list) -> str:
    """Name a position by the shape its legs make."""
    sides = {leg["option_type"] for leg in legs}
    bought = sum(1 for leg in legs if leg["quantity"] > 0)

    if len(legs) == 1:
        return f"Long {legs[0]['option_type'].capitalize()}"

    if len(sides) == 2:
        strikes = {leg["strike"] for leg in legs}

        return "Long Straddle" if len(strikes) == 1 else "Long Strangle"

    call = "call" in sides
    spread = "Bull Call Spread" if call else "Bear Put Spread"

    return spread if bought else "Custom"


def _ranked_row(item: dict) -> dict:
    """Describe one ranked strategy as a grid row."""
    crossings = item.get("breakevens") or []

    return {
        "strategy": item["strategy"],
        "legs": item["legs"],
        "contracts": item["contracts"],
        "cost": item["cost"],
        "expected_profit": item["expected_profit"],
        "expected_return": item["expected_return"],
        "max_profit": item["max_profit"],
        "max_loss": item["max_loss"],
        "breakeven_lower": crossings[0] if crossings else None,
        "breakeven_upper": crossings[-1] if len(crossings) > 1 else None,
    }


@router.command(
    methods=["GET"],
    widget_config=_table_widget(
        "Strategy Optimizer",
        "Every strategy the expiration can form, sized to a budget and ranked"
        " by what it returns if the underlying reaches a price.",
        OPTIMIZER_COLUMNS,
        18,
    ),
    examples=[
        APIEx(
            description="Rank strategies for a move to 100,000 by year end.",
            parameters={
                "symbol": "BTC",
                "target_price": 100000,
                "target_date": "2026-12-25",
            },
        )
    ],
)
async def optimizer(
    symbol: Annotated[str, _underlying()] = "BTC",
    target_price: Annotated[
        float | None,
        FastAPIQuery(description="The price the underlying is expected to reach."),
    ] = None,
    target_date: Annotated[
        str | None,
        FastAPIQuery(description="When it is expected to reach it."),
    ] = None,
    budget: Annotated[
        float,
        FastAPIQuery(description="What there is to spend, in the quote currency."),
    ] = 5000.0,
    limit: Annotated[
        int, FastAPIQuery(description="How many strategies to return.")
    ] = 12,
) -> OBBject:
    """Rank the option strategies that best serve a view on the underlying."""
    from openbb_deribit.utils.options.chain import nearest_expiration, quotes_at
    from openbb_deribit.utils.options.optimizer import rank

    frame, spot, inverse, settles = await _chain_or_404(symbol)
    target = float(target_price) if target_price else spot
    expiration = nearest_expiration(frame, target_date or frame["expiration"].min())
    ranked = rank(quotes_at(frame, expiration), spot, target, budget, inverse, limit)

    return OBBject(
        results=[_ranked_row(item) for item in ranked],
        provider="deribit",
        extra={
            "results_metadata": {
                "symbol": symbol,
                "underlying_price": spot,
                "target_price": target,
                "expiration": str(expiration),
                "quote_currency": _quote(symbol),
                "settlement_currency": settles,
            }
        },
    )


@router.command(
    methods=["GET"],
    widget_config=_table_widget(
        "Straddle",
        "A long straddle at the money, priced at every expiration.",
        STRADDLE_COLUMNS,
    ),
    examples=[APIEx(description="Price the BTC straddles.", parameters={})],
)
async def straddle(symbol: Annotated[str, _underlying()] = "BTC") -> OBBject:
    """Price a long straddle at each expiration."""
    from openbb_deribit.utils.options.strategies import straddles

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)

    return OBBject(results=straddles(frame, spot), provider="deribit")


@router.command(
    methods=["GET"],
    widget_config=_table_widget(
        "Strangle",
        "A long strangle out of the money, priced at every expiration.",
        STRANGLE_COLUMNS,
    ),
    examples=[APIEx(description="Price the BTC strangles.", parameters={})],
)
async def strangle(
    symbol: Annotated[str, _underlying()] = "BTC",
    moneyness: Annotated[
        float,
        FastAPIQuery(description="How far out of the money each leg sits, in percent."),
    ] = 5.0,
) -> OBBject:
    """Price a long strangle at each expiration."""
    from openbb_deribit.utils.options.strategies import strangles

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)

    return OBBject(
        results=strangles(frame, spot, abs(moneyness) / 100), provider="deribit"
    )


@router.command(
    methods=["GET"],
    widget_config=_table_widget(
        "Vertical Spreads",
        "A bull call and a bear put spread at every expiration.",
        SPREAD_COLUMNS,
    ),
    examples=[APIEx(description="Price the BTC vertical spreads.", parameters={})],
)
async def spreads(
    symbol: Annotated[str, _underlying()] = "BTC",
    moneyness: Annotated[
        float,
        FastAPIQuery(description="How far out the sold leg sits, in percent."),
    ] = 5.0,
) -> OBBject:
    """Price a bull call and a bear put spread at each expiration."""
    from openbb_deribit.utils.options.strategies import verticals

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)

    return OBBject(
        results=verticals(frame, spot, abs(moneyness) / 100), provider="deribit"
    )


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the strategies the optimizer ranks for a view.",
            parameters={"symbol": "BTC"},
        )
    ],
)
async def strategy_choices(
    symbol: Annotated[str, _underlying()] = "BTC",
    target_price: Annotated[float | None, FastAPIQuery()] = None,
    target_date: Annotated[str | None, FastAPIQuery()] = None,
    budget: Annotated[float, FastAPIQuery()] = 5000.0,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of the strategies the optimizer ranks for a view."""
    from openbb_deribit.utils.options.chain import nearest_expiration, quotes_at
    from openbb_deribit.utils.options.optimizer import rank

    frame, spot, inverse, _settles = await _loaded(symbol)
    target = float(target_price) if target_price else spot
    expiration = nearest_expiration(frame, target_date or frame["expiration"].min())
    ranked = rank(quotes_at(frame, expiration), spot, target, budget, inverse)

    return [
        {"label": f"{item['strategy']} — {item['legs']}", "value": item["legs"]}
        for item in ranked
    ]


async def payoff_chart(
    symbol: Annotated[str, _underlying()] = "BTC",
    target_price: Annotated[
        float | None,
        FastAPIQuery(description="The price the underlying is expected to reach."),
    ] = None,
    target_date: Annotated[
        str | None, FastAPIQuery(description="When it is expected to reach it.")
    ] = None,
    budget: Annotated[
        float,
        FastAPIQuery(description="What there is to spend, in the quote currency."),
    ] = 5000.0,
    legs: Annotated[
        str | None,
        FastAPIQuery(
            description="The contracts to draw, as 'Buy SYMBOL / Sell SYMBOL'."
            + " Click the Legs cell of a strategy in the optimizer to set it,"
            + " or pick one here. Left empty, the best strategy for the view is"
            + " drawn.",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": STRATEGY_CHOICES_ENDPOINT,
                    "optionsParams": {
                        "symbol": "$symbol",
                        "target_price": "$target_price",
                        "target_date": "$target_date",
                        "budget": "$budget",
                    },
                    "style": SYMBOL_STYLE,
                }
            },
        ),
    ] = None,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw what one position returns across a range of underlying prices.

    Naming the contracts draws exactly them, which is what clicking a strategy
    in the optimizer does. Nothing is ranked in that case: the contracts are
    read straight off the chain and priced.

    Raises
    ------
    HTTPException
        If the expiration lists no strategy, or does not list the position.
    """
    from fastapi import HTTPException

    from openbb_deribit.utils.options.chain import nearest_expiration, quotes_at
    from openbb_deribit.utils.options.create_payoff import create_payoff
    from openbb_deribit.utils.options.optimizer import draw, rank, rebuild, score

    frame, spot, inverse, settles = await _chain_or_404(symbol)
    target = float(target_price) if target_price else spot
    expiration = nearest_expiration(frame, target_date or frame["expiration"].min())
    quotes = quotes_at(frame, expiration)

    if legs:
        try:
            built = rebuild(legs, quotes)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        scored = score(
            {"strategy": _named(built), "legs": built}, spot, target, inverse
        )

        if scored is None:
            raise HTTPException(
                status_code=404,
                detail="That position is opened for a credit, so a budget does"
                " not size it. Pick one the optimizer ranked.",
            )

        chosen = draw(scored, spot, target, budget, inverse)
    else:
        ranked = rank(quotes, spot, target, budget, inverse, 1)

        if not ranked:
            raise HTTPException(
                status_code=404,
                detail=f"No strategy on the {expiration} expiration can be sized"
                f" to {budget:,.0f} {_quote(symbol)}.",
            )

        chosen = ranked[0]

    output = create_payoff(
        {
            **chosen,
            "spot": spot,
            "target": target,
            "quote": _quote(symbol),
            "settles": settles,
        },
        theme,
    )

    return _figure_json(output, raw)


async def smile_chart(
    symbol: Annotated[str, _underlying()] = "BTC",
    expirations: Annotated[
        str | None,
        FastAPIQuery(
            description="The expirations to draw. Left empty, the nearest one is"
            + " drawn on its own.",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "multiSelect": True,
                    "optionsEndpoint": EXPIRATION_CHOICES_ENDPOINT,
                    "optionsParams": {"symbol": "$symbol"},
                    "style": SYMBOL_STYLE,
                }
            },
        ),
    ] = None,
    moneyness: Annotated[
        float,
        FastAPIQuery(description="How far either side of spot to keep, in percent."),
    ] = 25.0,
    otm: Annotated[
        bool,
        FastAPIQuery(description="Keep only the out-of-the-money side of each strike."),
    ] = True,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw implied volatility against strike, one line per expiration."""
    from openbb_deribit.utils.options.create_smile import (
        chosen_expirations,
        create_smile,
        smile_rows,
    )

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)
    drawn = chosen_expirations(frame, expirations)
    rows = smile_rows(
        frame[frame["expiration"].isin(drawn)], spot, otm, abs(moneyness) / 100
    )
    output = create_smile({"rows": rows, "spot": spot, "symbol": symbol}, theme)

    return _figure_json(output, raw)


async def term_structure_chart(
    symbol: Annotated[str, _underlying()] = "BTC",
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw at-the-money implied volatility against time to expiration."""
    from openbb_deribit.utils.options.create_term_structure import (
        create_term_structure,
        term_rows,
    )

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)
    output = create_term_structure(
        {"rows": term_rows(frame, spot), "symbol": symbol}, theme
    )

    return _figure_json(output, raw)


async def surface_chart(
    symbol: Annotated[str, _underlying()] = "BTC",
    measure: Annotated[
        SURFACE_MEASURES,
        FastAPIQuery(description="What to raise into the third dimension."),
    ] = "implied_volatility",
    moneyness: Annotated[
        float,
        FastAPIQuery(description="How far either side of spot to keep, in percent."),
    ] = 25.0,
    dte_min: Annotated[
        int, FastAPIQuery(description="The nearest expiration to keep, in days.")
    ] = 1,
    dte_max: Annotated[
        int, FastAPIQuery(description="The furthest expiration to keep, in days.")
    ] = 120,
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw a measure over time to expiration and strike."""
    from openbb_deribit.utils.options.create_surface import create_surface, surface_rows

    frame, spot, _inverse, _settles = await _chain_or_404(symbol)
    rows = surface_rows(frame, spot, measure, abs(moneyness) / 100, dte_min, dte_max)
    output = create_surface({"rows": rows, "measure": measure, "symbol": symbol}, theme)

    return _figure_json(output, raw)


async def stats_chart(
    symbol: Annotated[str, _underlying()] = "BTC",
    by: Annotated[
        GROUPED_BY, FastAPIQuery(description="What to group the totals by.")
    ] = "expiration",
    raw: Annotated[bool, _excluded_query()] = False,
    theme: Annotated[str, _excluded_query()] = "dark",
):
    """Draw call and put open interest and volume."""
    from openbb_deribit.utils.options.create_stats import create_stats, stats_rows

    frame, _spot, _inverse, _settles = await _chain_or_404(symbol)
    output = create_stats(
        {"rows": stats_rows(frame, by), "by": by, "symbol": symbol}, theme
    )

    return _figure_json(output, raw)


CHART_ROUTES = (
    (
        "/payoff",
        payoff_chart,
        "Options Payoff",
        "What one ranked strategy returns across a range of underlying prices.",
        18,
    ),
    (
        "/smile",
        smile_chart,
        "Volatility Smile",
        "Implied volatility by strike, per expiration.",
        16,
    ),
    (
        "/term_structure",
        term_structure_chart,
        "Volatility Term Structure",
        "At-the-money implied volatility against time to expiration.",
        16,
    ),
    (
        "/surface",
        surface_chart,
        "Volatility Surface",
        "A measure raised over time to expiration and strike.",
        20,
    ),
    (
        "/stats",
        stats_chart,
        "Options Statistics",
        "Open interest and volume, split between calls and puts.",
        16,
    ),
)

for _path, _endpoint, _name, _description, _height in CHART_ROUTES:
    router.api_router.add_api_route(
        path=_path,
        endpoint=_endpoint,
        methods=["GET"],
        openapi_extra=_chart_widget(_name, _description, _height),
    )
