# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""Stocks Router."""


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

from openbb_stocks.ca.ca_router import router as ca_router
from openbb_stocks.dd.dd_router import router as dd_router
from openbb_stocks.disc.disc_router import router as disc_router
from openbb_stocks.dps.dps_router import router as dps_router
from openbb_stocks.fa.fa_router import router as fa_router
from openbb_stocks.gov.gov_router import router as gov_router
from openbb_stocks.ins.ins_router import router as ins_router
from openbb_stocks.options.options_router import router as options_router

router = Router(prefix="")
router.include_router(fa_router)
router.include_router(ca_router)
router.include_router(dd_router)
router.include_router(dps_router)
router.include_router(disc_router)
router.include_router(gov_router)
router.include_router(ins_router)
router.include_router(options_router)


@router.command(model="StockEOD")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Load stock data for a specific ticker."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="StockNews")
def news(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Get news for one or more stock tickers."""
    return Obbject(results=Query(**locals()).execute())


@router.command(model="StockMultiples")
def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Get valuation multiples for a stock ticker."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def tob() -> Obbject[Empty]:
    """View top of book for loaded ticker (US exchanges only)."""
    return Obbject(results=Empty())


@router.command
def quote() -> Obbject[Empty]:
    """View the current price for a specific stock ticker."""
    return Obbject(results=Empty())


@router.command
def search() -> Obbject[Empty]:
    """Search a specific stock ticker for analysis."""
    return Obbject(results=Empty())
