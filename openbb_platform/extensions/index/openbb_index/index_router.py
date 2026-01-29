"""指数路由器。"""

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

from openbb_index.price.price_router import router as price_router

router = Router(prefix="", description="指数数据。")
router.include_router(price_router)

# pylint: disable=unused-argument


@router.command(
    model="IndexConstituents",
    examples=[
        APIEx(parameters={"symbol": "dowjones", "provider": "fmp"}),
        APIEx(
            description="FMP 以外的提供商将使用股票代码。",
            parameters={"symbol": "BEP50P", "provider": "cboe"},
        ),
    ],
)
async def constituents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取指数成分股。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSnapshots",
    examples=[
        APIEx(parameters={"provider": "tmx"}),
        APIEx(parameters={"region": "us", "provider": "cboe"}),
    ],
)
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """指数快照。提供商的所有指数的当前水平，按 `region` 分组。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AvailableIndices",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(parameters={"provider": "yfinance"}),
    ],
)
async def available(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """给定提供商提供的所有可用指数。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSearch",
    examples=[
        APIEx(parameters={"provider": "cboe"}),
        APIEx(parameters={"query": "SPX", "provider": "cboe"}),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """筛选包含查询内容的指数行。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SP500Multiples",
    examples=[
        APIEx(parameters={"provider": "multpl"}),
        APIEx(parameters={"series_name": "shiller_pe_year", "provider": "multpl"}),
    ],
)
async def sp500_multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史标准大普尔 500 倍数和席勒市盈率。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IndexSectors",
    examples=[APIEx(parameters={"symbol": "^TX60", "provider": "tmx"})],
)
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取指数行业。指数的行业权重。"""
    return await OBBject.from_query(Query(**locals()))
