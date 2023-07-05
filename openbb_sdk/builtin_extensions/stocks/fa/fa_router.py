# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.provider_interface import ProviderChoices, StandardParams
from openbb_sdk_core.app.query import Query
from openbb_sdk_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/fa")


@router.command(query="BalanceSheet")
def balance(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Balance Sheet."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="CashFlowStatement")
def cash(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Cash Flow Statement."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="ExecutiveCompensation")
def comp(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Executive Compensation."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="EarningsCalendar")
def earning(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Earnings Calendar."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command
def emp() -> CommandOutput[Empty]:  # type: ignore
    """Number of Employees."""
    return CommandOutput(results=Empty())


@router.command(query="AnalystEstimates")
def est(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Analyst Estimates."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="IncomeStatement")
def income(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Income Statement."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="StockInsiderTrading")
def ins(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Stock Insider Trading."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="KeyMetrics")
def metrics(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Key Metrics."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="KeyExecutives")
def mgmt(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Key Executives."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="CompanyOverview")
def overview(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Company Overview."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="InstitutionalOwnership")
def own(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Institutional Ownership."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="PriceTarget")
def pta(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Price Target."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="PriceTargetConsensus")
def pt(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Price Target Consensus."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="RevenueGeographic")
def revgeo(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Revenue Geographic."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="RevenueBusinessLine")
def revseg(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Revenue Business Line."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="ShareStatistics")
def shrs(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Share Statistics."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command
def shares() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command(query="EarningsCallTranscript")
def transcript(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Earnings Call Transcript."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="HistoricalStockSplits")
def split(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Historical Stock Splits."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="HistoricalDividends")
def cal(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Historical Dividends."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command
def customer() -> CommandOutput[Empty]:  # type: ignore
    """List of customers of the company."""
    return CommandOutput(results=Empty())


@router.command
def divs() -> CommandOutput[Empty]:  # type: ignore
    """Show historical dividends for company."""
    return CommandOutput(results=Empty())


@router.command
def dcfc() -> CommandOutput[Empty]:  # type: ignore
    """Determine the (historical) discounted cash flow."""
    return CommandOutput(results=Empty())


@router.command
def dupont() -> CommandOutput[Empty]:  # type: ignore
    """Detailed breakdown for Return on Equity (RoE)."""
    return CommandOutput(results=Empty())


@router.command
def enterprise() -> CommandOutput[Empty]:  # type: ignore
    """Enterprise value."""
    return CommandOutput(results=Empty())


@router.command
def epsfc() -> CommandOutput[Empty]:  # type: ignore
    """Earnings Estimate by Analysts - EPS."""
    return CommandOutput(results=Empty())


@router.command
def analysis() -> CommandOutput[Empty]:  # type: ignore
    """Analyse SEC filings with the help of machine learning."""
    return CommandOutput(results=Empty())


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


@router.command
def key() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


@router.command
def mktcap() -> CommandOutput[Empty]:  # type: ignore
    """Obtain the market capitalization or enterprise value."""
    return CommandOutput(results=Empty())


@router.command  # CHECK IF NEWS ARE NEEDED HERE
def news() -> CommandOutput[Empty]:  # type: ignore
    return CommandOutput(results=Empty())


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
def supplier() -> CommandOutput[Empty]:  # type: ignore
    """List of suppliers of the company."""
    return CommandOutput(results=Empty())
