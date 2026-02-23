"""CoinGecko crypto historical price model."""

# pylint: disable=unused-argument

from datetime import datetime, timezone
from typing import Any, Literal
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class CoinGeckoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """CoinGecko crypto historical query params."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {"choices": ["1h", "1d"]},
    }

    interval: Literal["1h", "1d"] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )


class CoinGeckoCryptoHistoricalData(CryptoHistoricalData):
    """CoinGecko crypto historical data model."""

    symbol: str | None = Field(
        default=None,
        description="Normalized crypto pair symbol.",
    )
    coin_id: str | None = Field(
        default=None,
        description="CoinGecko unique coin id.",
    )


class CoinGeckoCryptoHistoricalFetcher(
    Fetcher[
        CoinGeckoCryptoHistoricalQueryParams,
        list[CoinGeckoCryptoHistoricalData],
    ]
):
    """Transform, extract and transform CoinGecko crypto historical data."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CoinGeckoCryptoHistoricalQueryParams:
        """Set default date range and validate params."""
        transformed_params = params
        today = datetime.now(tz=timezone.utc).date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = today - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = today

        return CoinGeckoCryptoHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: CoinGeckoCryptoHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract raw CoinGecko data using `/coins/markets` and OHLCV endpoints."""
        # pylint: disable=import-outside-toplevel
        from openbb_coingecko.utils.helpers import (
            get_ohlcv_series,
            resolve_coin_ids,
            split_crypto_symbol,
        )

        if query.start_date is None or query.end_date is None:
            raise OpenBBError("start_date and end_date are required")

        api_key = credentials.get("coingecko_api_key") if credentials else ""
        symbols = [
            symbol.strip() for symbol in query.symbol.split(",") if symbol.strip()
        ]

        if not symbols:
            raise EmptyDataError("At least one symbol is required.")

        split_pairs = [split_crypto_symbol(symbol) for symbol in symbols]
        quote_currencies = {quote.upper() for _, quote in split_pairs}

        if len(quote_currencies) != 1:
            raise OpenBBError(
                "CoinGecko fetcher supports one quote currency per request. "
                "Use symbols with a shared quote, e.g. BTCUSD,ETHUSD."
            )

        vs_currency = quote_currencies.pop().lower()
        bases = [base.upper() for base, _ in split_pairs]
        symbol_to_id = await resolve_coin_ids(bases, vs_currency, api_key, **kwargs)

        results: list[dict] = []
        for symbol, (base, quote) in zip(symbols, split_pairs):
            coin_id = symbol_to_id.get(base.upper())
            if not coin_id:
                warn(f"No CoinGecko coin id found for {symbol}")
                continue

            ohlcv = await get_ohlcv_series(
                coin_id=coin_id,
                vs_currency=vs_currency,
                start_date=query.start_date,
                end_date=query.end_date,
                interval=query.interval,
                api_key=api_key,
                **kwargs,
            )

            if not ohlcv:
                warn(f"No OHLCV data found for {symbol}")
                continue

            results.append(
                {
                    "symbol": f"{base.upper()}{quote.upper()}",
                    "coin_id": coin_id,
                    "ohlcv": ohlcv,
                }
            )

        if not results:
            raise EmptyDataError(
                "No CoinGecko OHLCV data found for the requested symbols."
            )

        return results

    @staticmethod
    def transform_data(
        query: CoinGeckoCryptoHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CoinGeckoCryptoHistoricalData]:
        """Transform raw OHLCV arrays into the OpenBB standard model."""
        results: list[CoinGeckoCryptoHistoricalData] = []

        for item in data:
            symbol = item.get("symbol")
            coin_id = item.get("coin_id")
            rows = item.get("ohlcv", [])

            if not isinstance(rows, list):
                continue

            for row in rows:
                if not isinstance(row, list) or len(row) < 5:
                    continue

                raw_timestamp = int(row[0])
                timestamp = (
                    raw_timestamp / 1000
                    if raw_timestamp > 1_000_000_000_000
                    else raw_timestamp
                )
                parsed_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)

                normalized_row = {
                    "date": (
                        parsed_datetime.date()
                        if query.interval == "1d"
                        else parsed_datetime
                    ),
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4],
                    "volume": row[5] if len(row) > 5 else None,
                    "symbol": symbol,
                    "coin_id": coin_id,
                }
                results.append(
                    CoinGeckoCryptoHistoricalData.model_validate(normalized_row)
                )

        return sorted(
            results,
            key=lambda entry: (
                entry.date,
                entry.symbol if entry.symbol is not None else "",
            ),
        )
