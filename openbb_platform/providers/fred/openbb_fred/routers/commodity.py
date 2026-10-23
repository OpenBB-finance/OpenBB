"""FRED Commodity sub-router."""

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

from openbb_fred import COMMODITY_INSTALLED

router = Router(prefix="/commodity/price", description="FRED commodity prices.")


if not COMMODITY_INSTALLED:

    @router.command(
        model="FredCommoditySpotPrices",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def spot(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Commodity Spot Prices."""
        return await OBBject.from_query(OBBQuery(**locals()))
