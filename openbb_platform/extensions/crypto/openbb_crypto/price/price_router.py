# pylint: disable=W0613:unused-argument
"""Crypto Price Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
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
        'obb.crypto.price.historical("BTCUSD", start_date="2024-01-01", end_date="2024-01-31")',
        'obb.crypto.price.historical("ETH-USD", provider="yfinance", interval="1mo", start_date="2024-01-01", end_date="2024-12-31")',  # noqa: E501
        'obb.crypto.price.historical("BTCUSD,ETH-USD", provider="yfinance", interval="1d", start_date="2024-01-01", end_date="2024-01-31")',  # noqa: E501
        'obb.crypto.price.historical(["BTCUSD", "ETH-USD"], start_date="2024-01-01", end_date="2024-01-31")',
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
