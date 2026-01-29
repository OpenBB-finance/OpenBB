"""估计路由器。"""

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

router = Router(prefix="/estimates")

# pylint: disable=unused-argument


@router.command(
    model="PriceTarget",
    examples=[
        APIEx(parameters={"provider": "benzinga"}),
        APIEx(
            description="使用 'benzinga' 作为提供商获取 Microsoft 的价格目标。",
            parameters={
                "start_date": "2020-01-01",
                "end_date": "2024-02-16",
                "limit": 10,
                "symbol": "msft",
                "provider": "benzinga",
                "action": "downgrades",
            },
        ),
    ],
)
async def price_target(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取按公司划分的分析师价格目标。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AnalystEstimates",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取收益和收入的历史分析师估计。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PriceTargetConsensus",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL,MSFT", "provider": "yfinance"}),
    ],
)
async def consensus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取一致的价格目标和建议。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AnalystSearch",
    examples=[
        APIEx(parameters={"provider": "benzinga"}),
        APIEx(parameters={"firm_name": "Wedbush", "provider": "benzinga"}),
    ],
)
async def analyst_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """搜索特定分析师并获取他们的预测记录。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ForwardSalesEstimates",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            parameters={
                "fiscal_year": 2025,
                "fiscal_period": "fy",
                "provider": "intrinio",
            }
        ),
    ],
)
async def forward_sales(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取远期销售额估计。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ForwardEbitdaEstimates",
    examples=[
        APIEx(parameters={"provider": "intrinio"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "fiscal_period": "annual",
                "provider": "intrinio",
            }
        ),
        APIEx(
            parameters={
                "symbol": "AAPL,MSFT",
                "fiscal_period": "quarter",
                "provider": "fmp",
            }
        ),
    ],
)
async def forward_ebitda(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取远期 EBITDA 估计。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ForwardEpsEstimates",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            parameters={
                "fiscal_year": 2025,
                "fiscal_period": "fy",
                "provider": "intrinio",
            }
        ),
    ],
)
async def forward_eps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取远期每股收益 (EPS) 估计。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ForwardPeEstimates",
    examples=[
        APIEx(parameters={"provider": "intrinio"}),
        APIEx(
            parameters={
                "symbol": "AAPL,MSFT,GOOG",
                "provider": "intrinio",
            }
        ),
    ],
)
async def forward_pe(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取远期市盈率 (PE) 估计。"""
    return await OBBject.from_query(Query(**locals()))
