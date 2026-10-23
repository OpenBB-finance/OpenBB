"""Cboe Futures sub-router."""

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

router = Router(prefix="/futures", description="Cboe futures data.")

CURVE_COLUMNS = [
    {
        "field": "expiration",
        "headerName": "Expiration",
        "pinned": "left",
        "chartDataType": "category",
    },
    {
        "field": "price",
        "headerName": "Price",
        "cellDataType": "number",
        "chartDataType": "series",
    },
    {
        "field": "symbol",
        "headerName": "Symbol",
        "cellDataType": "text",
        "chartDataType": "excluded",
    },
    {
        "field": "date",
        "headerName": "Date",
        "cellDataType": "dateString",
        "chartDataType": "excluded",
    },
]


@router.command(
    model="CboeFuturesSettlements",
    widget_config={
        "name": "Cboe Futures Settlement Prices",
        "description": "Daily settlement prices. Sessions that settled nothing"
        + " fall back to the most recent one that did.",
        "category": "Derivatives",
        "subCategory": "Futures",
        "source": ["Cboe"],
        "gridData": {"w": 20, "h": 12},
    },
    examples=[
        APIEx(
            description="Settlement prices for the most recent session.",
            parameters={"provider": "cboe"},
        ),
        APIEx(
            description="Final settlement prices for expired contracts.",
            parameters={"final_settlement": True, "provider": "cboe"},
        ),
    ],
)
async def settlement_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the settlement prices for Cboe futures contracts."""
    return await OBBject.from_query(OBBQuery(**locals()))


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="CboeFuturesInstruments",
        widget_config={
            "name": "Cboe Futures Instruments",
            "description": "The futures products Cboe lists, and what each tracks.",
            "category": "Derivatives",
            "subCategory": "Futures",
            "source": ["Cboe"],
            "gridData": {"w": 20, "h": 12},
        },
        examples=[
            APIEx(
                description="List the Cboe futures roots and their underlying symbols.",
                parameters={"provider": "cboe"},
            )
        ],
    )
    async def instruments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the Cboe futures roots, names, and their underlying symbols."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeFuturesCurve",
        widget_config={
            "name": "VIX Futures Curve",
            "description": "The VX term structure, at mid-morning TWAP or"
            + " end-of-day levels.",
            "category": "Derivatives",
            "subCategory": "Futures",
            "source": ["Cboe"],
            "gridData": {"w": 40, "h": 15},
            "data": {
                "table": {
                    "chartView": {"enabled": True, "chartType": "line"},
                    "columnsDefs": CURVE_COLUMNS,
                }
            },
        },
        examples=[
            APIEx(
                description="The current VIX futures term structure.",
                parameters={"provider": "cboe"},
            ),
            APIEx(
                description="The curve as of one or more historical dates.",
                parameters={
                    "symbol": "VX_EOD",
                    "date": "2024-06-25,2024-06-26",
                    "provider": "cboe",
                },
            ),
        ],
    )
    async def curve(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the VIX (VX) futures term structure, at mid-morning TWAP or end-of-day levels."""
        return await OBBject.from_query(OBBQuery(**locals()))
