"""股票路由器。"""

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

from openbb_equity.calendar.calendar_router import router as calendar_router
from openbb_equity.compare.compare_router import router as compare_router
from openbb_equity.darkpool.darkpool_router import router as darkpool_router
from openbb_equity.discovery.discovery_router import router as discovery_router
from openbb_equity.estimates.estimates_router import router as estimates_router
from openbb_equity.fundamental.fundamental_router import router as fundamental_router
from openbb_equity.ownership.ownership_router import router as ownership_router
from openbb_equity.price.price_router import router as price_router
from openbb_equity.shorts.shorts_router import router as shorts_router

router = Router(prefix="", description="股票市场数据。")
router.include_router(calendar_router)
router.include_router(compare_router)
router.include_router(estimates_router)
router.include_router(darkpool_router)
router.include_router(discovery_router)
router.include_router(fundamental_router)
router.include_router(ownership_router)
router.include_router(price_router)
router.include_router(shorts_router)

# pylint: disable=import-outside-toplevel, W0613:unused-argument


@router.command(
    model="EquitySearch",
    examples=[
        APIEx(parameters={"provider": "intrinio"}),
        APIEx(
            parameters={
                "query": "AAPL",
                "is_symbol": False,
                "use_cache": True,
                "provider": "nasdaq",
            }
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """搜索股票代码、CIK、LEI 或公司名称。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityScreener", examples=[APIEx(parameters={"provider": "fmp"})]
)
async def screener(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """根据各种标准筛选公司。

    这些标准包括市值、价格、贝塔值、成交量和股息率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityInfo",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def profile(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取有关公司的常规信息。这包括公司名称、行业、板块和价格数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MarketSnapshots", examples=[APIEx(parameters={"provider": "fmp"})]
)
async def market_snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取最新的股票市场快照。这包括数千只股票的价格数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalMarketCap",
    examples=[APIEx(parameters={"provider": "fmp", "symbol": "AAPL"})],
)
async def historical_market_cap(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取股票代码的历史市值。"""
    return await OBBject.from_query(Query(**locals()))
