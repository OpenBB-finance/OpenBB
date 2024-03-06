"""ETF Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_etf.discovery.discovery_router import router as discovery_router

router = Router(prefix="")
router.include_router(discovery_router)

# pylint: disable=unused-argument


@router.command(
    model="EtfSearch",
    exclude_auto_examples=True,
    examples=[
        "### An empty query returns the full list of ETFs from the provider. ###",
        'obb.etf.search("", provider="fmp")',
        "#### The query will return results from text-based fields containing the term. ####"
        'obb.etf.search("commercial real estate", provider="fmp")',
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search for ETFs.

    An empty query returns the full list of ETFs from the provider.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHistorical",
    operation_id="etf_historical",
    examples=[
        'obb.etf.historical("SPY", provider="yfinance")',
        "#### This function accepts multiple tickers. ####",
        'obb.etf.historical("SPY,IWM,QQQ,DJIA", provider="yfinance")',
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF Historical Market Price."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfInfo",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.info("SPY", provider="fmp")',
        "#### This function accepts multiple tickers. ####",
        'obb.etf.info("SPY,IWM,QQQ,DJIA", provider="fmp")',
    ],
)
async def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF Information Overview."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfSectors",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.sectors("SPY", provider="fmp")',
    ],
)
async def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF Sector weighting."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfCountries",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.countries("VT", provider="fmp")',
    ],
)
async def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ETF Country weighting."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PricePerformance",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.price_performance("SPY,QQQ,IWM,DJIA", provider="fmp")',
    ],
)
async def price_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Price performance as a return, over different periods. This is a proxy for `equity.price.performance`."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHoldings",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.holdings("XLK", provider="fmp").to_df()',
        "#### Including a date (FMP, SEC) will return the holdings as per NPORT-P filings. ####",
        'obb.etf.holdings("XLK", date="2022-03-31",provider="fmp").to_df()',
        "#### The same data can be returned from the SEC directly. ####",
        'obb.etf.holdings("XLK", date="2022-03-31",provider="sec").to_df()',
    ],
)
async def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the holdings for an individual ETF."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHoldingsDate",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.holdings_date("XLK", provider="fmp").results',
    ],
)
async def holdings_date(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Use this function to get the holdings dates, if available."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfHoldingsPerformance",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.holdings_performance("XLK", provider="fmp")',
    ],
)
async def holdings_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the recent price performance of each ticker held in the ETF."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EtfEquityExposure",
    exclude_auto_examples=True,
    examples=[
        'obb.etf.equity_exposure("MSFT", provider="fmp")',
        "#### This function accepts multiple tickers. ####",
        'obb.etf.equity_exposure("MSFT,AAPL", provider="fmp")',
    ],
)
async def equity_exposure(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the exposure to ETFs for a specific stock."""
    return await OBBject.from_query(Query(**locals()))
