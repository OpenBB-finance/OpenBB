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
    """Historical Dividends. Historical dividends data for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalEps")
async def historical_eps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical earnings-per-share for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalEmployees")
async def employee_count(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical Employees. Historical number of employees."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SearchAttributes")
async def search_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search Intrinio data tags."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="LatestAttributes")
async def latest_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Fetch the latest value of a data tag from Intrinio."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalAttributes")
async def historical_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Fetch the historical values of a data tag from Intrinio."""
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
    """Key Metrics. Key metrics for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="KeyExecutives")
async def management(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Key Executives. Key executives for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="ExecutiveCompensation")
async def management_compensation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Executive Compensation. Information about the executive compensation for a given company."""
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
    """Company Overview. General information about a company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FinancialRatios")
async def ratios(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Extensive set of ratios over time. Financial ratios for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RevenueGeographic")
async def revenue_per_geography(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Revenue Geographic. Geographic revenue data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RevenueBusinessLine")
async def revenue_per_segment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Revenue Business Line. Business line revenue data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CompanyFilings")
async def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Company Filings. Company filings data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="HistoricalSplits")
async def historical_splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Historical Splits. Historical splits data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="EarningsCallTranscript")
async def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Earnings Call Transcript. Earnings call transcript for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TrailingDividendYield")
async def trailing_dividend_yield(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Trailing 1yr dividend yield."""
    return await OBBject.from_query(Query(**locals()))
