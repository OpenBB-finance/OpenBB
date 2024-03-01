# pylint: disable=W0613:unused-argument
"""Fundamental Analysis Router."""

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model import CommandContext, Example, OBBject
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
    api_examples=[Example(parameters={"symbol": "AAPL"})],
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "limit": 5})
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
    api_examples=[Example(parameters={"symbol": "AAPL", "limit": 10})],
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "limit": 5})
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
    api_examples=[
        Example(
            parameters={
                "symbol": "AAPL",
                "period": "annual",
                "statement_type": "balance",
                "limit": 100,
            }
        ),
        Example(
            description="Get reported income statement",
            parameters={"symbol": "AAPL", "statement_type": "income"},
        ),
        Example(
            description="Get reported cash flow statement",
            parameters={"symbol": "AAPL", "statement_type": "cash"},
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
    api_examples=[Example(parameters={"symbol": "AAPL", "limit": 10})],
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
    model="HistoricalDividends", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    model="HistoricalEps", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    model="HistoricalEmployees", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    api_examples=[Example(parameters={"query": "ebitda"})],
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
    api_examples=[Example(parameters={"tag": "ceo"})],
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
    api_examples=[Example(parameters={"tag": "ebitda"})],
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "limit": 5})
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "limit": 10, "period": "annual"})
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "limit": 100})
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
    model="KeyExecutives", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    model="ExecutiveCompensation", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    api_examples=[Example(parameters={"symbol": "AAPL"})],
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "limit": 12})
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "structure": "flat"})
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
    api_examples=[
        Example(parameters={"symbol": "AAPL", "period": "annual", "structure": "flat"})
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
    model="CompanyFilings", api_examples=[Example(parameters={"limit": 100})]
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
    model="HistoricalSplits", api_examples=[Example(parameters={"symbol": "AAPL"})]
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
    api_examples=[Example(parameters={"symbol": "AAPL", "year": 2020})],
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
    api_examples=[Example(parameters={"symbol": "AAPL", "limit": 252})],
)
async def trailing_dividend_yield(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the 1 year trailing dividend yield for a given company over time."""
    return await OBBject.from_query(Query(**locals()))
