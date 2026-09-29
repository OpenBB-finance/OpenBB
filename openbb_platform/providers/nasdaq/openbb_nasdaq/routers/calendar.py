"""Nasdaq Calendar sub-router."""

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
from openbb_nasdaq.utils.constants import GHOST_SYMBOL_PARAM

router = Router(prefix="/equity/calendar", description="Nasdaq market calendars.")


if not EQUITY_INSTALLED:

    @router.command(
        model="NasdaqCalendarEarnings",
        widget_config={"params": [GHOST_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="Upcoming and historical earnings releases.",
                parameters={"provider": "nasdaq"},
            )
        ],
    )
    async def earnings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Company earnings releases, with consensus and surprise."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqCalendarDividend",
        widget_config={"params": [GHOST_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="Upcoming and historical dividend payments.",
                parameters={"provider": "nasdaq"},
            )
        ],
    )
    async def dividend(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Ex-dividend, record, and payment dates."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqCalendarIpo",
        widget_config={"params": [GHOST_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="IPO announcements and pricings.",
                parameters={"provider": "nasdaq"},
            )
        ],
    )
    async def ipo(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """IPO and secondary offering announcements, pricings, and withdrawals."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqCalendarSplits",
        widget_config={"params": [GHOST_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="Upcoming stock splits.",
                parameters={"provider": "nasdaq"},
            )
        ],
    )
    async def splits(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Announced stock splits and their effective dates."""
        return await OBBject.from_query(OBBQuery(**locals()))
