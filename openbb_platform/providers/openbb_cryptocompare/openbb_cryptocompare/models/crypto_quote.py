"""CryptoCompare CryptoQuote Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_quote import (
    CryptoQuoteData,
    CryptoQuoteQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_cryptocompare.utils.helpers import build_price_request_url
from pydantic import field_validator


class CryptoCompareCryptoQuoteQueryParams(CryptoQuoteQueryParams):
    """CryptoCompare Crypto Quote Query Parameters.

    Source: https://min-api.cryptocompare.com/documentation
    """

    currency: str = "USD"


class CryptoCompareCryptoQuoteData(CryptoQuoteData):
    """CryptoCompare Crypto Quote Data."""

    # Override the standard model validator to prevent double-normalization.
    # CryptoCompare already returns decimal-form percentages from the fetcher.
    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Return the value as-is (already normalized in fetcher)."""
        return v


class CryptoCompareCryptoQuoteFetcher(
    Fetcher[
        CryptoCompareCryptoQuoteQueryParams,
        list[CryptoCompareCryptoQuoteData],
    ]
):
    """CryptoCompare Crypto Quote Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CryptoCompareCryptoQuoteQueryParams:
        """Transform the query parameters."""
        return CryptoCompareCryptoQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CryptoCompareCryptoQuoteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch real-time crypto quote data from CryptoCompare."""
        symbols = query.symbol.replace(" ", "")
        currency = query.currency or "USD"
        url = build_price_request_url(symbols=symbols, currency=currency)

        api_key = credentials.get("api_key") if credentials else None
        if api_key:
            url += f"&api_key={api_key}"

        return await amake_request(url, timeout=30)

    @staticmethod
    def transform_data(
        query: CryptoCompareCryptoQuoteQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[CryptoCompareCryptoQuoteData]:
        """Transform the API response into a list of CryptoQuoteData."""
        if data.get("Err"):
            raise RuntimeError(
                f"CryptoCompare API error: {data['Err'].get('message', str(data['Err']))}"
            )

        raw = data.get("RAW", {})
        currency = query.currency or "USD"
        results: list[CryptoCompareCryptoQuoteData] = []

        for symbol, currencies in raw.items():
            coin_data = currencies.get(currency.upper())
            price = coin_data.get("PRICE") if coin_data else None
            if price is None:
                continue

            last_timestamp = coin_data.get("LASTUPDATE")
            if isinstance(last_timestamp, (int, float)):
                last_timestamp = datetime.fromtimestamp(last_timestamp)

            # CryptoCompare returns CHANGEPCT24HOUR as a percentage value
            # (e.g., 0.5 = 0.5% change). Normalize to decimal (0.005 = 0.5%).
            change_pct = coin_data.get("CHANGEPCT24HOUR")
            if change_pct is not None:
                change_pct = change_pct / 100

            results.append(
                CryptoCompareCryptoQuoteData(
                    symbol=symbol,
                    price=price,
                    currency=currency.upper(),
                    change=coin_data.get("CHANGE24HOUR"),
                    change_percent=change_pct,
                    volume_24h=coin_data.get("VOLUME24HOUR"),
                    high_24h=coin_data.get("HIGH24HOUR"),
                    low_24h=coin_data.get("LOW24HOUR"),
                    market_cap=coin_data.get("MKTCAP"),
                    supply_circulating=coin_data.get("SUPPLY"),
                    supply_total=coin_data.get("TOTALSUPPLY"),
                    last_timestamp=last_timestamp,
                    open=coin_data.get("OPEN24HOUR"),
                    high=coin_data.get("HIGH24HOUR"),
                    low=coin_data.get("LOW24HOUR"),
                    volume=coin_data.get("VOLUME24HOURTO"),
                )
            )

        return results
