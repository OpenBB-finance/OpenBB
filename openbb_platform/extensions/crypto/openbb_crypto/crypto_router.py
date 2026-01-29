"""加密货币路由器。"""

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

router = Router(prefix="", description="加密货币市场数据。")
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
    """在提供商中搜索可用的加密货币对。"""
    return await OBBject.from_query(Query(**locals()))
