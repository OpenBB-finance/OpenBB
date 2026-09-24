"""Nasdaq ETF sub-router."""

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

from openbb_nasdaq import ETF_INSTALLED
from openbb_nasdaq.utils.constants import GHOST_ETF_SYMBOL_PARAM

router = Router(prefix="/etf", description="Nasdaq ETF data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the Nasdaq-traded fund directory.", parameters={})
    ],
)
async def symbol_choices() -> list[dict]:
    """``[{label, value}]`` of every Nasdaq-traded ETF and mutual fund."""
    from openbb_nasdaq.utils.helpers import get_etf_symbol_choices

    return await get_etf_symbol_choices()


if not ETF_INSTALLED:

    @router.command(
        model="NasdaqEtfInfo",
        examples=[
            APIEx(
                description="The 'Key Data' block for a fund.",
                parameters={"symbol": "QQQ", "provider": "nasdaq"},
            )
        ],
    )
    async def info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fund key data - AUM, expense ratio, beta, alpha, and average volumes."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEtfHistorical",
        examples=[
            APIEx(
                description="Daily fund prices.",
                parameters={"symbol": "QQQ", "provider": "nasdaq"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily OHLCV history for ETFs and mutual funds."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEtfHoldings",
        examples=[
            APIEx(
                description="The fund's ten largest positions.",
                parameters={"symbol": "QQQ", "provider": "nasdaq"},
            ),
            APIEx(
                description="Mutual funds are served from the fund profile.",
                parameters={"symbol": "PRGFX", "provider": "nasdaq"},
            ),
        ],
    )
    async def holdings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the top ten holdings of an ETF or mutual fund, with weights."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEtfEquityExposure",
        examples=[
            APIEx(
                description="The funds holding an equity in their top ten.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def equity_exposure(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the funds carrying an equity as a top-ten holding, with weights."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEtfSearch",
        widget_config={"params": [GHOST_ETF_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="Screen the ETF universe.",
                parameters={"sector": "biotech", "provider": "nasdaq"},
            )
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Screen ETFs by fund family, sector, asset class, region, and performance."""
        return await OBBject.from_query(OBBQuery(**locals()))
