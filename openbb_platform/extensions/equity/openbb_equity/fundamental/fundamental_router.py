# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/fundamental")


@router.command(model="EquityValuationMultiples")
def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Equity Valuation Multiples. Valuation multiples for a stock ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="BalanceSheet")
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Balance Sheet. Balance sheet statement."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="BalanceSheetGrowth")
def balance_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Balance Sheet Statement Growth. Information about the growth of the company balance sheet."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CashFlowStatement")
def cash(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Cash Flow Statement. Information about the cash flow statement."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CashFlowStatementGrowth")
def cash_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Cash Flow Statement Growth. Information about the growth of the company cash flow statement."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalDividends")
def dividends(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Dividends. Historical dividends data for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalEps")
def historical_eps(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical earnings-per-share for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalEmployees")
def employee_count(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Employees. Historical number of employees."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="SearchFinancialAttributes")
def search_financial_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search financial attributes for financial statements."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="FinancialAttributes")
def financial_attributes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Fetch the value of financial attributes for a selected company and fiscal period."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IncomeStatement")
def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Income Statement. Report on a company's financial performance."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IncomeStatementGrowth")
def income_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Income Statement Growth. Information about the growth of the company income statement."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="KeyMetrics")
def metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Key Metrics. Key metrics for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="KeyExecutives")
def management(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Key Executives. Key executives for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ExecutiveCompensation")
def management_compensation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get Executive Compensation. Information about the executive compensation for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CompanyOverview")
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Company Overview. General information about a company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="FinancialRatios")
def ratios(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Extensive set of ratios over time. Financial ratios for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RevenueGeographic")
def revenue_per_geography(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Revenue Geographic. Geographic revenue data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RevenueBusinessLine")
def revenue_per_segment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Revenue Business Line. Business line revenue data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CompanyFilings")
def filings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Company Filings. Company filings data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalSplits")
def historical_splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Splits. Historical splits data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EarningsCallTranscript")
def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Earnings Call Transcript. Earnings call transcript for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="TrailingDividendYield")
def trailing_dividend_yield(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Trailing 1yr dividend yield."""
    return OBBject(results=Query(**locals()).execute())
