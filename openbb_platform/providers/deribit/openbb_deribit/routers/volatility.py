"""Deribit Volatility sub-router."""

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

router = Router(prefix="/volatility", description="Deribit volatility data.")


@router.command(
    model="DeribitHistoricalVolatility",
    widget_config={
        "name": "Deribit Realized Volatility",
        "description": "The volatility a currency has actually realized.",
        "category": "Crypto",
        "subCategory": "Volatility",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 14},
        "params": [{"paramName": "currency", "value": "BTC"}],
        "data": {
            "table": {
                "chartView": {"enabled": True, "chartType": "line"},
            }
        },
    },
    examples=[
        APIEx(
            description="The volatility BTC has realized.",
            parameters={"currency": "BTC", "provider": "deribit"},
        )
    ],
)
async def realized(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the volatility a Deribit currency has actually realized."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitVolatilityIndex",
    widget_config={
        "name": "Deribit Volatility Index",
        "description": "The DVOL index, as candles over a span.",
        "category": "Crypto",
        "subCategory": "Volatility",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 14},
        "params": [{"paramName": "currency", "value": "BTC"}],
        "data": {
            "table": {
                "chartView": {"enabled": True, "chartType": "line"},
            }
        },
    },
    examples=[
        APIEx(
            description="The BTC volatility index over the last month.",
            parameters={"currency": "BTC", "provider": "deribit"},
        ),
        APIEx(
            description="Daily candles over a named span.",
            parameters={
                "currency": "ETH",
                "interval": "1d",
                "start_date": "2026-01-01",
                "end_date": "2026-06-30",
                "provider": "deribit",
            },
        ),
    ],
)
async def index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Deribit DVOL volatility index, as candles over a span."""
    return await OBBject.from_query(OBBQuery(**locals()))
