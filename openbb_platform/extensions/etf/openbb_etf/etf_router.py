"""ETF 路由器。"""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_etf.discovery.discovery_router import router as discovery_router

router = Router(prefix="", description="交易所交易基金 (ETF) 市场数据。")
router.include_router(discovery_router)

# pylint: disable=unused-argument


@router.command(
    model="EtfSearch",
    examples=[
        APIEx(
            description="空查询将返回提供商的所有 ETF 列表。",
            parameters={"provider": "fmp"},
        ),
        APIEx(
            description="查询将返回包含该术语的基于文本的字段的结果。",
            parameters={"query": "commercial real estate", "provider": "fmp"},
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """搜索 ETF。

    空查询将返回提供商的所有 ETF 列表。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHistorical",
    operation_id="etf_historical",
    examples=[
        APIEx(parameters={"symbol": "SPY", "provider": "fmp"}),
        APIEx(parameters={"symbol": "SPY", "provider": "yfinance"}),
        APIEx(
            description="此函数接受多个股票代码。",
            parameters={"symbol": "SPY,IWM,QQQ,DJIA", "provider": "yfinance"},
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF 历史市场价格。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfInfo",
    examples=[
        APIEx(parameters={"symbol": "SPY", "provider": "fmp"}),
        APIEx(
            description="此函数接受多个股票代码。",
            parameters={"symbol": "SPY,IWM,QQQ,DJIA", "provider": "fmp"},
        ),
    ],
)
async def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF 信息概览。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfSectors",
    examples=[APIEx(parameters={"symbol": "SPY", "provider": "fmp"})],
)
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF 行业权重。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfCountries",
    examples=[APIEx(parameters={"symbol": "VT", "provider": "fmp"})],
)
async def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF 国家权重。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfPricePerformance",
    examples=[
        APIEx(parameters={"symbol": "QQQ", "provider": "fmp"}),
        APIEx(parameters={"symbol": "SPY,QQQ,IWM,DJIA", "provider": "fmp"}),
    ],
)
async def price_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """不同时期的价格表现（收益率）。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHoldings",
    examples=[
        APIEx(parameters={"symbol": "XLK", "provider": "fmp"}),
        APIEx(
            description="可以直接从 SEC 返回相同的数据。",
            parameters={"symbol": "XLK", "date": "2022-03-31", "provider": "sec"},
        ),
    ],
)
async def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取单个 ETF 的持仓。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="NportDisclosure",
    examples=[
        APIEx(
            parameters={"symbol": "XLK", "provider": "fmp", "year": 2025, "quarter": 1}
        ),
        APIEx(
            description="可以直接从 SEC 返回相同的数据。",
            parameters={"symbol": "XLK", "provider": "sec", "year": 2025, "quarter": 1},
        ),
        PythonEx(
            description="SEC 响应中的 `extra['results_metadata']` 字段包含额外的披露信息，例如流量和回报。",
            code=[
                "response = obb.etf.nport_disclosure(symbol='XLK', provider='sec', year=2025, quarter=1)",
                "print(response.extra['results_metadata'])",
            ],
        ),
    ],
)
async def nport_disclosure(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取指定 ETF 或共同基金的 SEC NPORT-P 披露文件（仅限美国）。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfEquityExposure",
    examples=[
        APIEx(parameters={"symbol": "MSFT", "provider": "fmp"}),
        APIEx(
            description="此函数接受多个股票代码。",
            parameters={"symbol": "MSFT,AAPL", "provider": "fmp"},
        ),
    ],
)
async def equity_exposure(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取特定股票的 ETF 敞口。"""
    return await OBBject.from_query(Query(**locals()))
