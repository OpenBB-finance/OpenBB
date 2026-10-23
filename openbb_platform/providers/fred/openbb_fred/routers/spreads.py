"""FRED Spreads sub-router."""

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

router = Router(prefix="/fixedincome/spreads", description="FRED rate spreads.")


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FredSelectedTreasuryBill",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def treasury_effr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Select Treasury Bill."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSelectedTreasuryConstantMaturity",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def tcm_effr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Select Treasury Constant Maturity."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredTreasuryConstantMaturity",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def tcm(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Treasury Constant Maturity."""
        return await OBBject.from_query(OBBQuery(**locals()))
