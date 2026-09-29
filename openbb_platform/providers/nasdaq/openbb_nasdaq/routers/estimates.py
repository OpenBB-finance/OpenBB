"""Nasdaq Estimates sub-router."""

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

from openbb_nasdaq import EQUITY_INSTALLED

router = Router(prefix="/equity/estimates", description="Nasdaq analyst estimates.")


if not EQUITY_INSTALLED:

    @router.command(
        model="NasdaqPriceTargetConsensus",
        examples=[
            APIEx(
                description="The analyst price target consensus.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def consensus(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Analyst price target consensus, with the buy/hold/sell split."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqPriceTarget",
        examples=[
            APIEx(
                description="Recent upgrades and downgrades.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def price_target(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Recent analyst rating changes. Nasdaq publishes only current actions."""
        return await OBBject.from_query(OBBQuery(**locals()))
