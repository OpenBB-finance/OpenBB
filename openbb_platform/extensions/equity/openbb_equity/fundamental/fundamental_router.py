# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.deprecation import OpenBBDeprecationWarning
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
    model="EquityValuationMultiples",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get equity valuation multiples for a given company."""
    return await OBBject.from_query(Query(**locals()))


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
    """Get the balance sheet for a given company."""
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
    """Get the growth of a company's balance sheet items over time."""
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
    """Get the cash flow statement for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ReportedFinancials",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            description="Get AAPL balance sheet with a limit of 10 items.",
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "statement_type": "balance",
                "limit": 10,
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="Get reported income statement",
            parameters={
                "symbol": "AAPL",
                "statement_type": "income",
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="Get reported cash flow statement",
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
    """Get financial statements as reported by the company."""
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
    """Get the growth of a company's cash flow statement items over time."""
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
    """Get historical dividend data for a given company."""
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
    """Get historical earnings per share data for a given company."""
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
    """Get historical employee count data for a given company."""
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
    """Search Intrinio data tags to search in latest or historical attributes."""
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
    """Get the latest value of a data tag from Intrinio."""
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
    """Get the historical values of a data tag from Intrinio."""
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
    """Get the income statement for a given company."""
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
    """Get the growth of a company's income statement items over time."""
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
    """Get fundamental metrics for a given company."""
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
    """Get executive management team data for a given company."""
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
    """Get executive management team compensation for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompanyOverview",
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint is deprecated; use `/equity/profile` instead.",
        since=(4, 1),
        expected_removal=(4, 3),
    ),
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get company general business and stock data for a given company."""
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
    """Get an extensive set of financial and accounting ratios for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RevenueGeographic",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "structure": "flat",
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
    """Get the revenue geographic breakdown for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RevenueBusinessLine",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "structure": "flat",
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
    """Get the revenue breakdown by business segment for a given company over time."""
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
    """Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more. SEC
    filings include Form 10-K, Form 10-Q, Form 8-K, the proxy statement, Forms 3, 4, and 5, Schedule 13, Form 114,
    Foreign Investment Disclosures and others. The annual 10-K report is required to be
    filed annually and includes the company's financial statements, management discussion and analysis,
    and audited financial statements.
    """
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
    """Get historical stock splits for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EarningsCallTranscript",
    examples=[APIEx(parameters={"symbol": "AAPL", "year": 2020, "provider": "fmp"})],
)
async def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get earnings call transcripts for a given company."""
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
    """Get the 1 year trailing dividend yield for a given company over time."""
    return await OBBject.from_query(Query(**locals()))
