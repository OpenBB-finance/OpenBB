# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/fa")


@router.command
def analysis() -> Obbject[Empty]:  # type: ignore
    """Analyse SEC filings with the help of machine learning."""
    return Obbject(results=Empty())


@router.command(model="BalanceSheet")
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Balance Sheet."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="BalanceSheetGrowth")
def balance_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Balance Sheet Statement Growth."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="DividendCalendar")
def cal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Show Dividend Calendar for a given start and end dates."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="CashFlowStatement")
def cash(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Cash Flow Statement."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="CashFlowStatementGrowth")
def cash_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Cash Flow Statement Growth."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="ExecutiveCompensation")
def comp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Executive Compensation."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="StockSplitCalendar")
def comsplit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Stock Split Calendar."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def customer() -> Obbject[Empty]:  # type: ignore
    """List of customers of the company."""
    return Obbject(results=Empty())


@router.command
def dcfc() -> Obbject[Empty]:  # type: ignore
    """Determine the (historical) discounted cash flow."""
    return Obbject(results=Empty())


@router.command(model="HistoricalDividends")
def divs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Historical Dividends."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def dupont() -> Obbject[Empty]:  # type: ignore
    """Detailed breakdown for Return on Equity (RoE)."""
    return Obbject(results=Empty())


@router.command(model="EarningsCalendar")
def earning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Earnings Calendar."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="HistoricalEmployees")
def emp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Number of Employees."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def enterprise() -> Obbject[Empty]:  # type: ignore
    """Enterprise value."""
    return Obbject(results=Empty())


@router.command
def epsfc() -> Obbject[Empty]:  # type: ignore
    """Earnings Estimate by Analysts - EPS."""
    return Obbject(results=Empty())


@router.command(model="AnalystEstimates")
def est(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Analyst Estimates."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def fama_coe() -> Obbject[Empty]:  # type: ignore
    """Fama French 3 Factor Model - Coefficient of Earnings."""
    return Obbject(results=Empty())


@router.command
def fama_raw() -> Obbject[Empty]:  # type: ignore
    """Fama French 3 Factor Model - Raw Data."""
    return Obbject(results=Empty())


@router.command
def fraud() -> Obbject[Empty]:  # type: ignore
    """Key fraud ratios including M-score, Z-score and McKee."""
    return Obbject(results=Empty())


@router.command
def growth() -> Obbject[Empty]:  # type: ignore
    """Growth of financial statement items and ratios."""
    return Obbject(results=Empty())


@router.command
def historical_5() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command(model="IncomeStatement")
def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Income Statement."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="IncomeStatementGrowth")
def income_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Income Statement Growth."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="StockInsiderTrading")
def ins(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Stock Insider Trading."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="InstitutionalOwnership")
def ins_own(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Institutional Ownership."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def key() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command(model="KeyMetrics")
def metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Key Metrics."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="KeyExecutives")
def mgmt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Key Executives."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def mktcap() -> Obbject[Empty]:  # type: ignore
    """Obtain the market capitalization or enterprise value."""
    return Obbject(results=Empty())


@router.command  # CHECK IF NEWS IS NEEDED HERE
def news() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command(model="CompanyOverview")
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Company Overview."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="StockOwnership")
def own(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Stock Ownership."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="PriceTargetConsensus")
def pt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Price Target Consensus."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="PriceTarget")
def pta(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Price Target."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def rating() -> Obbject[Empty]:  # type: ignore
    """Analyst prices and ratings over time of the company."""
    return Obbject(results=Empty())


@router.command
def ratios() -> Obbject[Empty]:  # type: ignore
    """Extensive set of ratios over time."""
    return Obbject(results=Empty())


@router.command
def revfc() -> Obbject[Empty]:  # type: ignore
    """Earning Estimate by Analysts - Revenue."""
    return Obbject(results=Empty())


@router.command(model="RevenueGeographic")
def revgeo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Revenue Geographic."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="RevenueBusinessLine")
def revseg(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Revenue Business Line."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def rot() -> Obbject[Empty]:  # type: ignore
    """Number of analyst ratings over time on a monthly basis."""
    return Obbject(results=Empty())


@router.command
def score() -> Obbject[Empty]:  # type: ignore
    """Value investing scores for any time period."""
    return Obbject(results=Empty())


@router.command
def sec() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command
def shares() -> Obbject[Empty]:  # type: ignore
    return Obbject(results=Empty())


@router.command(model="ShareStatistics")
def shrs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Share Statistics."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="HistoricalStockSplits")
def split(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Historical Stock Splits."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def supplier() -> Obbject[Empty]:  # type: ignore
    """List of suppliers of the company."""
    return Obbject(results=Empty())


@router.command(model="EarningsCallTranscript")
def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Earnings Call Transcript."""
    return Obbject(results=Query(**locals()).execute())
