# pylint: disable=W0613:unused-argument
"""Crypto Price Router."""

from fastapi.responses import StreamingResponse
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from providers.binance.openbb_binance.models.crypto_historical import (
    BinanceCryptoHistoricalFetcher,
)

router = Router(prefix="/price")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="CryptoHistorical",
    examples=[
        APIEx(parameters={"symbol": "BTCUSD", "provider": "fmp"}),
        APIEx(
            parameters={
                "symbol": "BTCUSD",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "provider": "fmp",
            },
        ),
        APIEx(
            parameters={
                "symbol": "BTCUSD,ETHUSD",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "provider": "polygon",
            },
        ),
        APIEx(
            description="Get monthly historical prices from Yahoo Finance for Ethereum.",
            parameters={
                "symbol": "ETH-USD",
                "interval": "1m",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "provider": "yfinance",
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


@router.stream(methods=["GET"])
async def live(symbol: str = "ethbtc", lifetime: int = 10, tld: str = "us") -> OBBject:
    """Connect to Binance WebSocket Crypto Price data feed."""
    generator = BinanceCryptoHistoricalFetcher().stream_data(
        params={"symbol": symbol, "lifetime": lifetime, "tld": tld},
        credentials=None,
    )
    return OBBject(
        results=StreamingResponse(generator, media_type="application/x-ndjson"),
        provider="binance",
    )
