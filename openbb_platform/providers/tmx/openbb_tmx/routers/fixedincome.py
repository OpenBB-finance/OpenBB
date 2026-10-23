"""TMX Fixed Income sub-router."""

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

from openbb_tmx import FIXEDINCOME_INSTALLED
from openbb_tmx.utils.choices import cell_group

router = Router(prefix="/fixedincome", description="TMX fixed income data.")


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="TmxBondPrices",
        widget_config=cell_group("cusip", "The bond a click on the list selects."),
        examples=[
            APIEx(
                description="The designated bond master.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def prices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Return reference data and last prices for every CIRO-designated bond."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxBondTrades",
        examples=[
            APIEx(
                description="Reported bond trades.",
                parameters={"cusip": "135087U28", "provider": "tmx"},
            )
        ],
    )
    async def trades(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Every reported trade for a bond, across its full history."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxTreasuryPrices",
        examples=[
            APIEx(
                description="Government of Canada bond prices.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def treasury_prices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Government of Canada bond reference data and prices."""
        return await OBBject.from_query(OBBQuery(**locals()))
