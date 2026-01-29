# pylint: disable=W0613:unused-argument
"""比较分析路由器。"""

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

router = Router(prefix="/compare")


@router.command(
    model="EquityPeers",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def peers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的最接近的同行。

    同行由在同一交易所交易、在同一行业运营且市值相当的公司组成。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompareGroups",
    examples=[
        APIEx(parameters={"provider": "finviz"}),
        APIEx(
            description="按部门分组并分析估值。",
            parameters={"group": "sector", "metric": "valuation", "provider": "finviz"},
        ),
        APIEx(
            description="按行业分组并分析表现。",
            parameters={
                "group": "industry",
                "metric": "performance",
                "provider": "finviz",
            },
        ),
        APIEx(
            description="按国家分组并分析估值。",
            parameters={
                "group": "country",
                "metric": "valuation",
                "provider": "finviz",
            },
        ),
    ],
)
async def groups(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取按部门、行业或国家/地区分组的公司数据，并显示绩效或估值指标。

    估值指标包括市盈率、市净率、市销率和价格现金流比率。
    绩效指标包括不同时间段的股价变化。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompareCompanyFacts",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(
            parameters={
                "provider": "sec",
                "fact": "PaymentsForRepurchaseOfCommonStock",
                "year": 2023,
            }
        ),
        APIEx(
            parameters={
                "provider": "sec",
                "symbol": "NVDA,AAPL,AMZN,MSFT,GOOG,SMCI",
                "fact": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "year": 2024,
            }
        ),
    ],
)
async def company_facts(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """比较报告的公司事实和基本面数据点。"""
    return await OBBject.from_query(Query(**locals()))
