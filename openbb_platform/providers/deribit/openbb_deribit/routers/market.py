"""Deribit Market sub-router."""

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

router = Router(prefix="/market", description="Deribit market data.")


@router.command(
    model="DeribitBookSummary",
    widget_config={
        "name": "Deribit Book Summary",
        "description": "The top of book and trailing session statistics of every"
        + " instrument in a currency.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 15},
        "params": [{"paramName": "currency", "value": "BTC"}],
    },
    examples=[
        APIEx(
            description="Every BTC instrument's top of book.",
            parameters={"currency": "BTC", "provider": "deribit"},
        ),
        APIEx(
            description="Only the futures.",
            parameters={"currency": "BTC", "kind": "future", "provider": "deribit"},
        ),
        APIEx(
            description="One named instrument.",
            parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
        ),
    ],
)
async def book_summary(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the top of book and session statistics of Deribit instruments."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitOrderBook",
    widget_config={
        "name": "Deribit Order Book",
        "description": "The resting depth of one instrument, one row per level.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 20, "h": 15},
        "params": [{"paramName": "symbol", "value": "BTC-PERPETUAL"}],
        "data": {
            "table": {
                "chartView": {"enabled": False},
            }
        },
    },
    examples=[
        APIEx(
            description="The resting depth of the BTC perpetual.",
            parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
        ),
        APIEx(
            description="A book read by its numeric instrument identifier.",
            parameters={"instrument_id": 210838, "provider": "deribit"},
        ),
    ],
)
async def order_book(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the resting depth of a Deribit instrument, one row per level."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitTicker",
    widget_config={
        "name": "Deribit Ticker",
        "description": "The live quote, session statistics, and greeks of one"
        + " instrument.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 8},
        "params": [{"paramName": "symbol", "value": "BTC-PERPETUAL"}],
    },
    examples=[
        APIEx(
            description="The live quote of the BTC perpetual.",
            parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
        ),
        APIEx(
            description="Multiple instruments are comma-separated.",
            parameters={"symbol": "BTC-PERPETUAL,ETH-PERPETUAL", "provider": "deribit"},
        ),
    ],
)
async def ticker(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the live quote, session statistics, and greeks of a Deribit instrument."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitTrades",
    widget_config={
        "name": "Deribit Trades",
        "description": "The prints that crossed, by instrument or across a currency.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 15},
        "params": [{"paramName": "symbol", "value": "BTC-PERPETUAL"}],
        "data": {
            "table": {
                "chartView": {"enabled": False},
            }
        },
    },
    examples=[
        APIEx(
            description="The most recent prints on the BTC perpetual.",
            parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
        ),
        APIEx(
            description="Every BTC option print over a span.",
            parameters={
                "currency": "BTC",
                "kind": "option",
                "start_date": "2026-09-01",
                "end_date": "2026-09-02",
                "provider": "deribit",
            },
        ),
    ],
)
async def trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Deribit prints that crossed, by instrument or across a currency."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitTradeVolumes",
    widget_config={
        "name": "Deribit Trade Volumes",
        "description": "Traded volume by currency and product, over one, seven,"
        + " and thirty days.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 12},
    },
    examples=[
        APIEx(
            description="Traded volume by currency and product.",
            parameters={"provider": "deribit"},
        )
    ],
)
async def trade_volumes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Deribit's traded volume by currency and product."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitBlockRfqTrades",
    widget_config={
        "name": "Deribit Block RFQ Trades",
        "description": "The block requests that traded, one row per leg.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 15},
    },
    examples=[
        APIEx(
            description="The block requests that most recently traded.",
            parameters={"provider": "deribit"},
        )
    ],
)
async def block_rfq_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Deribit block requests that traded, one row per leg."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitSettlements",
    widget_config={
        "name": "Deribit Settlements",
        "description": "The settlements, deliveries, and bankruptcies the exchange"
        + " has processed.",
        "category": "Crypto",
        "subCategory": "Market Data",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 15},
        "params": [{"paramName": "currency", "value": "BTC"}],
    },
    examples=[
        APIEx(
            description="The most recent BTC settlements.",
            parameters={"currency": "BTC", "provider": "deribit"},
        ),
        APIEx(
            description="Only the deliveries of one instrument.",
            parameters={
                "symbol": "BTC-PERPETUAL",
                "settlement_type": "settlement",
                "provider": "deribit",
            },
        ),
    ],
)
async def settlements(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the settlements, deliveries, and bankruptcies Deribit has processed."""
    return await OBBject.from_query(OBBQuery(**locals()))
