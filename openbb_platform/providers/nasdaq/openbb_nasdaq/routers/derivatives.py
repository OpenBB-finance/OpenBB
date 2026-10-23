"""Nasdaq Derivatives sub-router."""

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

from openbb_nasdaq import DERIVATIVES_INSTALLED

router = Router(prefix="/options", description="Nasdaq options data.")


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="NasdaqOptionsChains",
        examples=[
            APIEx(
                description="The full chain, with front-expiration greeks.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            ),
            APIEx(
                description="One expiration, with greeks on every contract.",
                parameters={
                    "symbol": "NVDA",
                    "expiration": "2026-08-07",
                    "provider": "nasdaq",
                },
            ),
        ],
    )
    async def chains(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Delayed Nasdaq options chains.

        Narrowing with `expiration` populates greeks, implied volatility, and the
        full quote detail on every contract returned. Without it, Nasdaq only
        publishes greeks for the front expiration.
        """
        return await OBBject.from_query(OBBQuery(**locals()))
