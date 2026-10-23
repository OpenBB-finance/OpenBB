"""Nasdaq Ownership sub-router."""

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

from openbb_nasdaq import EQUITY_INSTALLED

router = Router(
    prefix="/equity/ownership", description="Nasdaq ownership and short interest data."
)


if not EQUITY_INSTALLED:

    @router.command(
        model="NasdaqInsiderTrading",
        examples=[
            APIEx(
                description="Recent insider transactions.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def insider_trading(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Insider transactions reported to the SEC."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqInstitutionalOwnership",
        examples=[
            APIEx(
                description="The largest institutional holders.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def institutional(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Institutional holders, their positions, and the change since the prior filing."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEquityShortInterest",
        examples=[
            APIEx(
                description="The bi-monthly short interest series.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def short_interest(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Bi-monthly settlement short interest, with days to cover."""
        return await OBBject.from_query(OBBQuery(**locals()))
