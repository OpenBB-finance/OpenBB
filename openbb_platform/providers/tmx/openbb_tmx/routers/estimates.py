"""TMX Estimates sub-router."""

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

from openbb_tmx import EQUITY_INSTALLED

router = Router(prefix="/equity/estimates", description="TMX analyst estimates.")


if not EQUITY_INSTALLED:

    @router.command(
        model="TmxPriceTargetConsensus",
        examples=[
            APIEx(
                description="Analyst consensus and price targets.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def consensus(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Analyst consensus, ratings breakdown, and price targets."""
        return await OBBject.from_query(OBBQuery(**locals()))
