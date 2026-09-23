"""Nasdaq News sub-router."""

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

from openbb_nasdaq import NEWS_INSTALLED

router = Router(prefix="/news", description="Nasdaq news.")


if not NEWS_INSTALLED:

    @router.command(
        model="NasdaqCompanyNews",
        examples=[
            APIEx(
                description="Articles and press releases by symbol.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def company(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Company news and press releases indexed by Nasdaq."""
        return await OBBject.from_query(OBBQuery(**locals()))
