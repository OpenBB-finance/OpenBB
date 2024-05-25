"""Crypto Router."""

# import asyncio

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from providers.binance.openbb_binance.models.crypto_historical import (
    BinanceCryptoHistoricalFetcher,
)

from openbb_crypto.price.price_router import router as price_router

router = Router(prefix="", description="Cryptocurrency market data.")
router.include_router(price_router)


# pylint: disable=unused-argument
@router.command(
    model="CryptoSearch",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(parameters={"query": "BTCUSD", "provider": "fmp"}),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search available cryptocurrency pairs within a provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    methods=["GET"],
)
async def stream_price(symbol: str = "ethbtc", lifetime: int = 10) -> OBBject:
    """Define the POC."""
    generator = BinanceCryptoHistoricalFetcher().stream_data(
        params={"symbol": symbol, "lifetime": lifetime},
        credentials=None,
    )
    return OBBject(results=generator, provider="binance")
