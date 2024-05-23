"""Crypto Router."""

import asyncio

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
    BinanceStreamFetcher,
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


# pylint: disable=unused-argument
async def crypto_historical():
    "Define the POC."
    full_url = "wss://stream.binance.com:9443/ws/ethbtc@miniTicker"
    await BinanceStreamFetcher.connect(full_url)
    try:
        await asyncio.sleep(10)  # Keep connection open for 60 seconds
    finally:
        await BinanceStreamFetcher.disconnect()

    # Adjusted setup for existing asyncio event loops
    loop = asyncio.get_event_loop()

    if loop.is_running():
        # Scheduling the coroutine to run and handling with the existing event loop
        loop.create_task(crypto_historical())
    else:
        # If the loop is not running, run until complete
        loop.run_until_complete(crypto_historical())
