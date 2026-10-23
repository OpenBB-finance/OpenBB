"""Deribit Index sub-router."""

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

router = Router(prefix="/index", description="Deribit index data.")


@router.command(
    model="DeribitIndexPrice",
    widget_config={
        "name": "Deribit Index Price",
        "description": "The current level of an index, and what it would deliver at.",
        "category": "Crypto",
        "subCategory": "Index",
        "source": ["Deribit"],
        "gridData": {"w": 20, "h": 6},
        "params": [{"paramName": "index_name", "value": "btc_usd"}],
    },
    examples=[
        APIEx(
            description="The current level of the BTC index.",
            parameters={"index_name": "btc_usd", "provider": "deribit"},
        ),
        APIEx(
            description="Multiple indexes are comma-separated.",
            parameters={"index_name": "btc_usd,eth_usd", "provider": "deribit"},
        ),
    ],
)
async def price(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the current level of a Deribit index."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitIndexHistorical",
    widget_config={
        "name": "Deribit Index History",
        "description": "The published level of an index over a span.",
        "category": "Crypto",
        "subCategory": "Index",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 14},
        "params": [{"paramName": "index_name", "value": "btc_usd"}],
        "data": {
            "table": {
                "chartView": {"enabled": True, "chartType": "line"},
            }
        },
    },
    examples=[
        APIEx(
            description="The BTC index over the last day.",
            parameters={"index_name": "btc_usd", "provider": "deribit"},
        ),
        APIEx(
            description="The whole published history.",
            parameters={"index_name": "btc_usd", "span": "all", "provider": "deribit"},
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the published level of a Deribit index over a span."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitDeliveryPrices",
    widget_config={
        "name": "Deribit Delivery Prices",
        "description": "The level each index has delivered at.",
        "category": "Crypto",
        "subCategory": "Index",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 14},
        "params": [{"paramName": "index_name", "value": "btc_usd"}],
        "data": {
            "table": {
                "chartView": {"enabled": True, "chartType": "line"},
            }
        },
    },
    examples=[
        APIEx(
            description="The level the BTC index has delivered at.",
            parameters={"index_name": "btc_usd", "provider": "deribit"},
        )
    ],
)
async def delivery_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the level a Deribit index has delivered at."""
    return await OBBject.from_query(OBBQuery(**locals()))
