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

router = Router(prefix="/fa")


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


@router.command(model="DividendCalendar")
def cal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Dividend Calendar. Show Dividend Calendar for a given start and end dates."""
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


@router.command(model="ExecutiveCompensation")
def comp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Executive Compensation. Information about the executive compensation for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockSplitCalendar")
def comsplit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Split Calendar. Show Stock Split Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalDividends")
def divs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Dividends. Historical dividends data for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EarningsCalendar")
def earning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Earnings Calendar. Earnings calendar for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalEmployees")
def emp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Employees. Historical number of employees."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AnalystEstimates")
def est(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Analyst Estimates. Analyst stock recommendations."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IncomeStatement")
def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Income Statement. Report on a company's finanacial performance."""
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


@router.command(model="StockInsiderTrading")
def ins(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Insider Trading. Information about insider trading."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="InstitutionalOwnership")
def ins_own(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Institutional Ownership. Institutional ownership data."""
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
def mgmt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Key Executives. Key executives for a given company."""
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


@router.command(model="StockOwnership")
def own(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Ownership. Information about the company ownership."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PriceTargetConsensus")
def pt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target Consensus. Price target consensus data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PriceTarget")
def pta(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target. Price target data."""
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
def revgeo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Revenue Geographic. Geographic revenue data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="RevenueBusinessLine")
def revseg(
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


@router.command(model="ShareStatistics")
def shrs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Share Statistics. Share statistics for a given company."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="HistoricalStockSplits")
def split(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Stock Splits. Historical stock splits data."""
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
