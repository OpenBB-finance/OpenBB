"""所有权路由器。"""

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

router = Router(prefix="/ownership")

# pylint: disable=unused-argument


@router.command(
    model="EquityOwnership",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "page": 0, "provider": "fmp"}),
    ],
)
async def major_holders(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的主要持有者随时间变化的数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InstitutionalOwnership",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={"symbol": "AAPL", "year": 2024, "quarter": 2, "provider": "fmp"}
        ),
    ],
)
async def institutional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """在 13-F 申报文件中报告的给定公司机构所有权的净统计数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InsiderTrading",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "limit": 500, "provider": "intrinio"}),
    ],
)
async def insider_trading(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取有关公司管理团队和董事会交易的数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ShareStatistics",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def share_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的流通股数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="Form13FHR",
    examples=[
        APIEx(parameters={"symbol": "NVDA", "provider": "sec"}),
        APIEx(
            description="输入特定报告的日期（日历季度末）。",
            parameters={"symbol": "BRK-A", "date": "2016-09-30", "provider": "sec"},
        ),
        PythonEx(
            description="查找 Michael Burry 申报文件的示例。",
            code=[
                'cik = obb.regulators.sec.institutions_search("Scion Asset Management").results[0].cik',
                "# Use the `limit` parameter to return N number of reports from the most recent.",
                "obb.equity.ownership.form_13f(cik, limit=2).to_df()",
            ],
        ),
    ],
)
async def form_13f(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取 13F 表格。
    
    证券交易委员会 (SEC) 的 13F 表格是季度报告，
    要求所有管理资产至少为 1 亿美元的机构投资经理提交。
    经理需要在日历季度最后一天后的 45 天内提交 13F 表格。
    大多数基金会等到此期间结束时才提交，以向竞争对手和公众隐瞒其投资策略。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GovernmentTrades",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "chamber": "all", "provider": "fmp"}),
        APIEx(parameters={"limit": 500, "chamber": "all", "provider": "fmp"}),
    ],
)
async def government_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取政府交易数据，包括来自参议院和众议院的数据。"""
    return await OBBject.from_query(Query(**locals()))
