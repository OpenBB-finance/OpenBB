"""FRED Corporate sub-router."""

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
    prefix="/fixedincome/corporate", description="FRED corporate bond data."
)


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FredCommercialPaper",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def commercial_paper(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Commercial Paper."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredHighQualityMarketCorporateBond",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def hqm(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """High Quality Market Corporate Bond."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSpotRate",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def spot_rates(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Spot Rates."""
        return await OBBject.from_query(OBBQuery(**locals()))
