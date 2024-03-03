# pylint: disable=W0613:unused-argument
"""Crypto Price Router."""

from openbb_core.app.model import CommandContext, Example, OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/price")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="CryptoHistorical",
    examples=[
        Example(parameters={"symbol": "BTCUSD"}),
        Example(
            parameters={
                "symbol": "BTCUSD",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        ),
        Example(
            parameters={
                "symbol": "BTCUSD,ETHUSD",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        ),
        Example(
            parameters={
                "symbol": "ETH-USD",
                "provider": "yfinance",
                "interval": "1mo",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get historical price data for cryptocurrency pair(s) within a provider."""
    return await OBBject.from_query(Query(**locals()))
