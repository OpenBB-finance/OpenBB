"""FRED Government sub-router."""

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

from openbb_fred import FIXEDINCOME_INSTALLED

router = Router(
    prefix="/fixedincome/government", description="FRED government bond data."
)


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FredTipsYields",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def tips_yields(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get current Treasury inflation-protected securities yields."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredYieldCurve",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def yield_curve(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get yield curve data by country and date."""
        return await OBBject.from_query(OBBQuery(**locals()))
