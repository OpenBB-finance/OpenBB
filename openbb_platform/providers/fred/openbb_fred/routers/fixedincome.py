"""FRED Fixed Income sub-router."""

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

router = Router(prefix="/fixedincome", description="FRED fixed income data.")


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FredBondIndices",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def bond_indices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Bond Indices."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredMortgageIndices",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def mortgage_indices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Mortgage Indices."""
        return await OBBject.from_query(OBBQuery(**locals()))
