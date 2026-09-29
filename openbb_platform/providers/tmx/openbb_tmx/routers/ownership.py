"""TMX Ownership sub-router."""

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

from openbb_tmx import EQUITY_INSTALLED

router = Router(prefix="/equity/ownership", description="TMX ownership data.")


if not EQUITY_INSTALLED:

    @router.command(
        model="TmxInsiderTrading",
        examples=[
            APIEx(
                description="Insider activity summary.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def insider_trading(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Insider buying and selling activity."""
        return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="TmxInsiderTransactions",
    widget_config={
        "name": "TMX Insider Transactions",
        "description": "Individual insider filings published to SEDI.",
        "source": ["TMX"],
        "gridData": {"w": 40, "h": 15},
    },
    examples=[
        APIEx(
            description="Every insider filing over the past year.",
            parameters={"symbol": "AC", "provider": "tmx"},
        )
    ],
)
async def insider_transactions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Individual insider filings, as reported to SEDI."""
    return await OBBject.from_query(OBBQuery(**locals()))
