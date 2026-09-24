"""TMX Calendar sub-router."""

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

router = Router(prefix="/equity/calendar", description="TMX corporate calendars.")


if not EQUITY_INSTALLED:

    @router.command(
        model="TmxCalendarEarnings",
        examples=[
            APIEx(
                description="Earnings calendar with estimates.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def earnings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Earnings calendar, with estimated and actual EPS."""
        return await OBBject.from_query(OBBQuery(**locals()))
