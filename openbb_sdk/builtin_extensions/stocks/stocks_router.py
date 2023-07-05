# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""Stocks Router."""
from typing import Optional

from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_sdk_core.app.query import Query
from openbb_sdk_core.app.router import Router
from pydantic import BaseModel

from builtin_extensions.stocks.ca.ca_router import router as ca_router
from builtin_extensions.stocks.dd.dd_router import router as dd_router
from builtin_extensions.stocks.disc.disc_router import router as disc_router
from builtin_extensions.stocks.dps.dps_router import router as dps_router
from builtin_extensions.stocks.fa.fa_router import router as fa_router
from builtin_extensions.stocks.gov.gov_router import router as gov_router
from builtin_extensions.stocks.ins.ins_router import router as ins_router
from builtin_extensions.stocks.options.options_router import router as options_router

router = Router(prefix="")
router.include_router(fa_router)
router.include_router(ca_router)
router.include_router(dd_router)
router.include_router(dps_router)
router.include_router(disc_router)
router.include_router(gov_router)
router.include_router(ins_router)
router.include_router(options_router)


@router.command(query="StockEOD")
def load(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
    extra_params: Optional[ExtraParams] = None,
) -> CommandOutput[BaseModel]:
    """Load stock data for a specific ticker."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command(query="StockNews")
def news(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
    extra_params: Optional[ExtraParams] = None,
) -> CommandOutput[BaseModel]:
    """Get news for one or more stock tickers."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )


@router.command
def tob() -> CommandOutput[Empty]:
    """View top of book for loaded ticker (US exchanges only)."""
    return CommandOutput(results=Empty())


@router.command
def quote() -> CommandOutput[Empty]:
    """View the current price for a specific stock ticker."""
    return CommandOutput(results=Empty())


@router.command
def search() -> CommandOutput[Empty]:
    """Search a specific stock ticker for analysis."""
    return CommandOutput(results=Empty())
