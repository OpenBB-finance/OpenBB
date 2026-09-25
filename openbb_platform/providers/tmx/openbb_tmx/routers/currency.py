"""TMX Currency sub-router."""

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

from openbb_tmx import CURRENCY_INSTALLED

router = Router(prefix="/currency", description="TMX currency data.")


if not CURRENCY_INSTALLED:

    @router.command(
        model="TmxCurrencyHistorical",
        widget_config={
            "name": "TMX Currency Historical Price",
            "description": "Currency rates, charted over the TMX quote feed.",
            "category": "Markets",
            "type": "advanced_charting",
            "endpoint": "api/v1/tmx/udf",
            "gridData": {"w": 40, "h": 20},
            "data": {"defaultSymbol": "USDCAD", "updateFrequency": 60000},
        },
        examples=[
            APIEx(
                description="Currency pair history.",
                parameters={"symbol": "USDCAD", "provider": "tmx"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical rates for a currency pair."""
        return await OBBject.from_query(OBBQuery(**locals()))
