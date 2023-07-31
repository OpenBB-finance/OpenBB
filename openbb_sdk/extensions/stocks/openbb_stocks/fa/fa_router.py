# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
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
def analysis() -> CommandOutput[Empty]:  # type: ignore
    """Analyse SEC filings with the help of machine learning."""
    return CommandOutput(results=Empty())


@router.command(model="BalanceSheet")
def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Balance Sheet."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="BalanceSheetGrowth")
def balance_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Balance Sheet Statement Growth."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="DividendCalendar")
def cal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Show Dividend Calendar for a given start and end dates."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="CashFlowStatement")
def cash(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Cash Flow Statement."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="CashFlowStatementGrowth")
def cash_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Cash Flow Statement Growth."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="ExecutiveCompensation")
def comp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Executive Compensation."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="StockSplitCalendar")
def comsplit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Stock Split Calendar."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def customer() -> CommandOutput[Empty]:  # type: ignore
    """List of customers of the company."""
    return CommandOutput(results=Empty())


@router.command
def dcfc() -> CommandOutput[Empty]:  # type: ignore
    """Determine the (historical) discounted cash flow."""
    return CommandOutput(results=Empty())


@router.command(model="HistoricalDividends")
def divs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Historical Dividends."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def dupont() -> CommandOutput[Empty]:  # type: ignore
    """Detailed breakdown for Return on Equity (RoE)."""
    return CommandOutput(results=Empty())


@router.command(model="EarningsCalendar")
def earning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Earnings Calendar."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="HistoricalEmployees")
def emp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Number of Employees."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def enterprise() -> CommandOutput[Empty]:  # type: ignore
    """Enterprise value."""
    return CommandOutput(results=Empty())


@router.command
def epsfc() -> CommandOutput[Empty]:  # type: ignore
    """Earnings Estimate by Analysts - EPS."""
    return CommandOutput(results=Empty())


@router.command(model="AnalystEstimates")
def est(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Analyst Estimates."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def fama_coe() -> CommandOutput[Empty]:  # type: ignore
    """Fama French 3 Factor Model - Coefficient of Earnings."""
    return CommandOutput(results=Empty())


@router.command
def fama_raw() -> CommandOutput[Empty]:  # type: ignore
    """Fama French 3 Factor Model - Raw Data."""
    return CommandOutput(results=Empty())


@router.command
def fraud() -> CommandOutput[Empty]:  # type: ignore
    """Key fraud ratios including M-score, Z-score and McKee."""
    return CommandOutput(results=Empty())


@router.command
def growth() -> CommandOutput[Empty]:  # type: ignore
    """Growth of financial statement items and ratios."""
    return CommandOutput(results=Empty())


@router.command
def historical_5() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command(model="IncomeStatement")
def income(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Income Statement."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="IncomeStatementGrowth")
def income_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Income Statement Growth."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="StockInsiderTrading")
def ins(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Stock Insider Trading."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def key() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command(model="KeyMetrics")
def metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Key Metrics."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="KeyExecutives")
def mgmt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Key Executives."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def mktcap() -> CommandOutput[Empty]:  # type: ignore
    """Obtain the market capitalization or enterprise value."""
    return CommandOutput(results=Empty())


@router.command  # CHECK IF NEWS IS NEEDED HERE
def news() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command(model="CompanyOverview")
def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Company Overview."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="InstitutionalOwnership")
def own(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Institutional Ownership."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="PriceTargetConsensus")
def pt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Price Target Consensus."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="PriceTarget")
def pta(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Price Target."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def rating() -> CommandOutput[Empty]:  # type: ignore
    """Analyst prices and ratings over time of the company."""
    return CommandOutput(results=Empty())


@router.command
def ratios() -> CommandOutput[Empty]:  # type: ignore
    """Extensive set of ratios over time."""
    return CommandOutput(results=Empty())


@router.command
def revfc() -> CommandOutput[Empty]:  # type: ignore
    """Earning Estimate by Analysts - Revenue."""
    return CommandOutput(results=Empty())


@router.command(model="RevenueGeographic")
def revgeo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Revenue Geographic."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="RevenueBusinessLine")
def revseg(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Revenue Business Line."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def rot() -> CommandOutput[Empty]:  # type: ignore
    """Number of analyst ratings over time on a monthly basis."""
    return CommandOutput(results=Empty())


@router.command
def score() -> CommandOutput[Empty]:  # type: ignore
    """Value investing scores for any time period."""
    return CommandOutput(results=Empty())


@router.command
def sec() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def shares() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command(model="ShareStatistics")
def shrs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Share Statistics."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(model="HistoricalStockSplits")
def split(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Historical Stock Splits."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def supplier() -> CommandOutput[Empty]:  # type: ignore
    """List of suppliers of the company."""
    return CommandOutput(results=Empty())


@router.command(model="EarningsCallTranscript")
def transcript(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Earnings Call Transcript."""
    return CommandOutput(results=Query(**locals()).execute())
