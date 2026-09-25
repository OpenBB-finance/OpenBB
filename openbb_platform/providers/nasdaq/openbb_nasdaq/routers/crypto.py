"""Nasdaq Crypto sub-router."""

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

from openbb_nasdaq import CRYPTO_INSTALLED

router = Router(prefix="/crypto", description="Nasdaq crypto data.")


if not CRYPTO_INSTALLED:

    @router.command(
        model="NasdaqCryptoHistorical",
        examples=[
            APIEx(
                description="Daily crypto prices.",
                parameters={"symbol": "BTC", "provider": "nasdaq"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily OHLCV history for the crypto pairs Nasdaq quotes."""
        return await OBBject.from_query(OBBQuery(**locals()))
