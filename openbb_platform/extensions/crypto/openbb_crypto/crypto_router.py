"""Crypto Router."""

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

from openbb_crypto.price.price_router import router as price_router
from openbb_crypto.tvl.tvl_router import router as tvl_router
from openbb_crypto.yields.yields_router import router as yields_router
from openbb_crypto.fees.fees_router import router as fees_router
from openbb_crypto.revenue.revenue_router import router as revenue_router
from openbb_crypto.volumes.volumes_router import router as volumes_router
from openbb_crypto.coins.coins_router import router as coins_router

router = Router(prefix="", description="Cryptocurrency market data.")
router.include_router(price_router)
router.include_router(tvl_router)
router.include_router(yields_router)
router.include_router(fees_router)
router.include_router(revenue_router)
router.include_router(volumes_router)
router.include_router(coins_router)


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
