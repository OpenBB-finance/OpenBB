# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""Stocks Router."""

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

from openbb_equity.compare.compare_router import router as compare_router
from openbb_equity.discovery.discovery_router import router as discovery_router
from openbb_equity.dps.dps_router import router as dps_router
from openbb_equity.fundamental.fundamental_router import router as fundamental_router
from openbb_equity.options.options_router import router as options_router

router = Router(prefix="")
router.include_router(fundamental_router)
router.include_router(compare_router)
router.include_router(options_router)
router.include_router(discovery_router)

router.include_router(dps_router)
# router.include_router(gov_router)
# router.include_router(ins_router)


@router.command(model="StockHistorical")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Historical price. Load stock data for a specific ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CompanyNews")
def news(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Company News. Get news for one or more companies."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockMultiples")
def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Multiples. Valuation multiples for a stock ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockSearch")
def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Search. Search for a company or stock ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockQuote")
def quote(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Quote. Load stock data for a specific ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockInfo")
def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Info. Get general price and performance metrics of a stock."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockNBBO")
def nbbo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Stock Quote. Load stock data for a specific ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PricePerformance")
def price_performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price performance as a return, over different periods."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CalendarIpo")
def calendar_ipo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Upcoming and Historical IPO Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="CalendarDividend")
def calendar_dividend(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Upcoming and Historical Dividend Calendar."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="MarketSnapshots")
def market_snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get a current, complete, market snapshot."""
    return OBBject(results=Query(**locals()).execute())
