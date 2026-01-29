"""股票发现路由器。"""

# pylint: disable=unused-argument
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

router = Router(prefix="/discovery")


@router.command(
    model="EquityGainers",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取股票涨幅榜。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityLosers",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取股票跌幅榜。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityActive",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取基于交易量的最活跃交易股票。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityUndervaluedLargeCaps",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def undervalued_large_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取潜在被低估的大盘股。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityUndervaluedGrowth",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def undervalued_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取潜在被低估的成长股。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityAggressiveSmallCaps",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def aggressive_small_caps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取基于盈利增长的顶级小盘股。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GrowthTechEquities",
    examples=[
        APIEx(parameters={"provider": "yfinance"}),
        APIEx(parameters={"sort": "desc", "provider": "yfinance"}),
    ],
)
async def growth_tech(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取基于收入和盈利增长的顶级科技股。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TopRetail",
    examples=[APIEx(parameters={"provider": "nasdaq"})],
)
async def top_retail(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """追踪个人投资者每天超过 300 亿美元的交易。

    它提供了超过 9,500 只在美国交易的股票、
    ADR 和 ETP 的零售活动和情绪的每日视图。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DiscoveryFilings",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="获取 2023 年的申报文件，限制为 100 个结果",
            parameters={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "limit": 100,
                "provider": "fmp",
            },
        ),
    ],
)
async def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取向 EDGAR 数据库报告的 SEC 申报文件的 URL，例如 10-K、10-Q、8-K 等。

    SEC 申报文件包括表格 10-K、表格 10-Q、表格 8-K、代理声明、表格 3、4 和 5、附表 13、表格 114、
    外国投资披露等。年度 10-K 报告需要
    每年提交，其中包括公司的财务报表、管理层讨论与分析
    以及经审计的财务报表。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="LatestFinancialReports",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(parameters={"provider": "sec", "date": "2024-09-30"}),
    ],
)
async def latest_financial_reports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取所有公司的最新季度、年度和当前报告。"""
    return await OBBject.from_query(Query(**locals()))
