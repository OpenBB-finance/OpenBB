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

from openbb_stocks.ca.ca_router import router as ca_router
from openbb_stocks.fa.fa_router import router as fa_router
from openbb_stocks.options.options_router import router as options_router

# TODO: Uncomment once they have some commands.
# from openbb_stocks.gov.gov_router import router as gov_router
# from openbb_stocks.ins.ins_router import router as ins_router
# from openbb_stocks.dps.dps_router import router as dps_router


router = Router(prefix="")
router.include_router(fa_router)
router.include_router(ca_router)
router.include_router(options_router)

# router.include_router(dps_router)
# router.include_router(gov_router)
# router.include_router(ins_router)


@router.command(model="StockHistorical")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Load stock data for a specific ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockNews")
def news(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get news for one or more stock tickers."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockMultiples")
def multiples(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get valuation multiples for a stock ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockSearch")
def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Search for a company or stock ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockQuote")
def quote(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Load stock data for a specific ticker."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="StockInfo")
def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get general price and performance metrics of a stock."""
    return OBBject(results=Query(**locals()).execute())
