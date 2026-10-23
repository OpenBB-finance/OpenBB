"""Cboe Equity sub-router."""

from typing import Annotated

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

from openbb_cboe import EQUITY_INSTALLED

router = Router(prefix="/equity", description="Cboe equity data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get symbol choices from the Cboe company directory.",
            parameters={},
        )
    ],
)
async def symbol_choices(
    use_cache: Annotated[
        bool,
        FastAPIQuery(
            description="When True, the company directory is cached for 24 hours."
        ),
    ] = True,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every symbol in the Cboe company directory."""
    from openbb_cboe.utils.helpers import get_equity_choices

    return await get_equity_choices(use_cache=use_cache)


_HISTORICAL_COLUMNS = [
    {
        "field": "date",
        "headerName": "Date",
        "pinned": "left",
        "chartDataType": "category",
    },
    {
        "field": "close",
        "headerName": "Close",
        "cellDataType": "number",
        "chartDataType": "series",
    },
    {
        "field": "open",
        "headerName": "Open",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
    {
        "field": "high",
        "headerName": "High",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
    {
        "field": "low",
        "headerName": "Low",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
    {
        "field": "volume",
        "headerName": "Volume",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
]


if not EQUITY_INSTALLED:

    @router.command(
        model="CboeEquitySearch",
        examples=[
            APIEx(
                description="Search the Cboe company directory by company name.",
                parameters={"query": "ETF", "provider": "cboe"},
            ),
            APIEx(
                description="Search by ticker symbol instead of name.",
                parameters={"query": "SPY", "is_symbol": True, "provider": "cboe"},
            ),
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the Cboe US company directory for listed options symbols."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeEquityQuote",
        widget_config={
            "name": "Quote",
            "description": "Delayed quote, with 30/60/90-day implied and realized"
            + " volatility.",
            "source": ["Cboe"],
            "gridData": {"w": 40, "h": 6},
            "params": [{"paramName": "symbol", "value": "SPY"}],
        },
        examples=[
            APIEx(
                description="Delayed quote, with implied and realized volatility.",
                parameters={"symbol": "AAPL", "provider": "cboe"},
            ),
            APIEx(
                description="Multiple symbols are comma-separated.",
                parameters={"symbol": "AAPL,MSFT", "provider": "cboe"},
            ),
        ],
    )
    async def quote(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Delayed Cboe quotes, with 30/60/90-day implied and realized volatility."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeEquityHistorical",
        widget_config={
            "name": "Underlying Asset History",
            "description": "Daily closing price of the underlying asset.",
            "source": ["Cboe"],
            "gridData": {"w": 40, "h": 14},
            "params": [{"paramName": "symbol", "value": "SPY"}],
            "data": {
                "table": {
                    "chartView": {"enabled": True, "chartType": "line"},
                    "columnsDefs": _HISTORICAL_COLUMNS,
                }
            },
        },
        examples=[
            APIEx(
                description="Daily historical prices. ETFs use this endpoint as well.",
                parameters={"symbol": "AAPL", "provider": "cboe"},
            ),
            APIEx(
                description="One-minute bars for the most recent trading day.",
                parameters={"symbol": "AAPL", "interval": "1m", "provider": "cboe"},
            ),
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical equity and ETF prices from Cboe, daily or one-minute."""
        return await OBBject.from_query(OBBQuery(**locals()))
