# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/fundamental")


@router.command(model="EquityValuationMultiples")
async def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get equity valuation multiples for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="BalanceSheet")
async def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the balance sheet for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="BalanceSheetGrowth")
async def balance_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the growth of a company's balance sheet items over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CashFlowStatement")
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
        "# Get reported income statement",
        "obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='income)",
        "# Get reported cash flow statement",
        "obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='cash')",
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


@router.command(model="CashFlowStatementGrowth")
async def cash_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the growth of a company's cash flow statement items over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalDividends")
async def dividends(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical dividend data for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalEps")
async def historical_eps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical earnings per share data for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalEmployees")
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
    exclude_auto_examples=True,
    examples=[
        "obb.equity.fundamental.search_attributes(query='ebitda')",
    ],
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
    exclude_auto_examples=True,
    examples=[
        "obb.equity.fundamental.latest_attributes(tag='ceo')",
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
    exclude_auto_examples=True,
    examples=[
        "obb.equity.fundamental.historical_attributes(tag='ebitda')",
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


@router.command(model="IncomeStatement")
async def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the income statement for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="IncomeStatementGrowth")
async def income_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the growth of a company's income statement items over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="KeyMetrics")
async def metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get fundamental metrics for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="KeyExecutives")
async def management(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get executive management team data for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ExecutiveCompensation")
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
)
async def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get company general business and stock data for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FinancialRatios")
async def ratios(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get an extensive set of financial and accounting ratios for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RevenueGeographic")
async def revenue_per_geography(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the revenue geographic breakdown for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RevenueBusinessLine")
async def revenue_per_segment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the revenue breakdown by business segment for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CompanyFilings")
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


@router.command(model="HistoricalSplits")
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
    exclude_auto_examples=True,
    examples=[
        "obb.equity.fundamental.transcript(symbol='AAPL', year=2020)",
    ],
)
async def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get earnings call transcripts for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TrailingDividendYield")
async def trailing_dividend_yield(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the 1 year trailing dividend yield for a given company over time."""
    return await OBBject.from_query(Query(**locals()))
