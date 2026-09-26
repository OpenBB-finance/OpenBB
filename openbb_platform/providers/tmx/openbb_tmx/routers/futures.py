"""TMX Futures sub-router."""

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

from openbb_tmx import DERIVATIVES_INSTALLED
from openbb_tmx.utils.choices import cell_group

router = Router(prefix="/futures", description="TMX futures data.")


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="TmxFuturesInstruments",
        widget_config=cell_group(
            "symbol", "The contract a click on the instrument list selects."
        ),
        examples=[
            APIEx(
                description="The Montreal Exchange universe.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def instruments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Every instrument listed on the Montreal Exchange."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxFuturesHistorical",
        widget_config={
            "name": "TMX Futures Historical Price",
            "description": "Futures prices, charted over the TMX quote feed.",
            "category": "Markets",
            "type": "advanced_charting",
            "endpoint": "api/v1/tmx/udf",
            "gridData": {"w": 40, "h": 20},
            "data": {"defaultSymbol": "CGB", "updateFrequency": 60000},
        },
        examples=[
            APIEx(
                description="Futures price history.",
                parameters={"symbol": "CGB", "provider": "tmx"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical prices for a futures contract."""
        return await OBBject.from_query(OBBQuery(**locals()))
