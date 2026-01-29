# pylint: disable=W0613:unused-argument
"""基本面分析路由器。"""

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

router = Router(prefix="/fundamental")


@router.command(
    model="BalanceSheet",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "limit": 5,
                "provider": "intrinio",
            }
        ),
    ],
)
async def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的资产负债表。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BalanceSheetGrowth",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "limit": 10, "provider": "fmp"}),
    ],
)
async def balance_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取公司资产负债表项目随时间的增长情况。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CashFlowStatement",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "limit": 5,
                "provider": "intrinio",
            }
        ),
    ],
)
async def cash(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的现金流量表。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ReportedFinancials",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            description="获取 AAPL 资产负债表，限制为 10 个项目。",
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "statement_type": "balance",
                "limit": 10,
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="获取报告的损益表",
            parameters={
                "symbol": "AAPL",
                "statement_type": "income",
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="获取报告的现金流量表",
            parameters={
                "symbol": "AAPL",
                "statement_type": "cash",
                "provider": "intrinio",
            },
        ),
    ],
)
async def reported_financials(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取公司报告的财务报表。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CashFlowStatementGrowth",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "limit": 10, "provider": "fmp"}),
    ],
)
async def cash_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取公司现金流量表项目随时间的增长情况。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalDividends",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"})],
)
async def dividends(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的历史股息数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalEps",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def historical_eps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的每股收益历史数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalEmployees",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def employee_count(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的历史员工人数数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SearchAttributes",
    examples=[APIEx(parameters={"query": "ebitda", "provider": "intrinio"})],
)
async def search_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """搜索 Intrinio 数据标签以在最新或历史属性中进行搜索。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="LatestAttributes",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "tag": "ceo", "provider": "intrinio"})
    ],
)
async def latest_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 Intrinio 获取数据标签的最新值。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalAttributes",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "tag": "ebitda", "provider": "intrinio"})
    ],
)
async def historical_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 Intrinio 获取数据标签的历史值。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IncomeStatement",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "limit": 5,
                "provider": "intrinio",
            }
        ),
    ],
)
async def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的损益表。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IncomeStatementGrowth",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "limit": 10,
                "period": "annual",
                "provider": "fmp",
            }
        ),
    ],
)
async def income_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取公司损益表项目随时间的增长情况。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="KeyMetrics",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "limit": 100,
                "provider": "intrinio",
            }
        ),
    ],
)
async def metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的基本面指标。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="KeyExecutives",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def management(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的高管管理团队数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ExecutiveCompensation",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def management_compensation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司高管管理团队随时间的薪酬。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FinancialRatios",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "intrinio",
            }
        ),
    ],
)
async def ratios(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司随时间推移的广泛财务和会计比率集。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RevenueGeographic",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "quarter",
                "provider": "fmp",
            }
        ),
    ],
)
async def revenue_per_geography(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司随时间推移的收入地理细分。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RevenueBusinessLine",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "quarter",
                "provider": "fmp",
            }
        ),
    ],
)
async def revenue_per_segment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司随时间推移的业务部门收入细分。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompanyFilings",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(parameters={"limit": 100, "provider": "fmp"}),
    ],
)
async def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取上市公司申报文件。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HistoricalSplits",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def historical_splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的历史股票拆分。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EarningsCallTranscript",
    examples=[
        APIEx(
            parameters={"symbol": "AAPL", "year": 2020, "quarter": 1, "provider": "fmp"}
        )
    ],
)
async def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司的收益电话会议记录。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TrailingDividendYield",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "tiingo"}),
        APIEx(parameters={"symbol": "AAPL", "limit": 252, "provider": "tiingo"}),
    ],
)
async def trailing_dividend_yield(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定公司随时间推移的 1 年滚动股息率。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ManagementDiscussionAnalysis",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "sec"}),
        APIEx(
            description="按日历年和期间获取管理层讨论与分析部分。",
            parameters={
                "symbol": "AAPL",
                "calendar_year": 2020,
                "calendar_period": "Q4",
                "provider": "sec",
            },
        ),
        APIEx(
            description="将 'include_tables' 设置为 True 将尝试提取有效 Markdown 中的所有表格。",
            parameters={
                "symbol": "AAPL",
                "calendar_year": 2020,
                "calendar_period": "Q4",
                "provider": "sec",
                "include_tables": True,
            },
        ),
        APIEx(
            description="将 'raw_html' 设置为 True 将绕过提取并按原样返回原始 HTML 文件。"
            + " 将此用于自定义解析或访问整个 HTML 申报文件。",
            parameters={
                "symbol": "AAPL",
                "calendar_year": 2020,
                "calendar_period": "Q4",
                "provider": "sec",
                "raw_html": True,
            },
        ),
    ],
    openapi_extra={
        "widget_config": {
            "type": "markdown",
            "data": {"dataKey": "results.content", "columnsDefs": []},
            "staleTime": 86400000,
            "refetchInterval": 86400000,
            "source": "SEC",
        }
    },
)
async def management_discussion_analysis(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从给定公司的财务报表中获取管理层讨论与分析部分。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EsgScore",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "TSLA,F", "provider": "fmp"}),
    ],
)
async def esg_score(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从公司披露中获取 ESG（环境、社会和治理）评分。"""
    return await OBBject.from_query(Query(**locals()))
