"""Nasdaq Economy sub-router."""

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

from openbb_nasdaq import ECONOMY_INSTALLED

router = Router(prefix="/economy", description="Nasdaq economic data.")


if not ECONOMY_INSTALLED:

    @router.command(
        model="NasdaqEconomicCalendar",
        examples=[
            APIEx(
                description="Upcoming and historical macro events.",
                parameters={"provider": "nasdaq"},
            )
        ],
    )
    async def calendar(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Macroeconomic events, with consensus, actual, and revised values."""
        return await OBBject.from_query(OBBQuery(**locals()))
