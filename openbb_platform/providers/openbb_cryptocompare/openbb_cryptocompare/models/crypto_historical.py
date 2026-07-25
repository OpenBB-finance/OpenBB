"""CryptoCompare CryptoHistorical Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_cryptocompare.utils.helpers import build_historical_request_url


class CryptoCompareCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """CryptoCompare Crypto Historical Query Parameters.

    Source: https://min-api.cryptocompare.com/documentation
    """

    currency: str = "USD"
    aggregate: int = 1
    limit: int = 100


class CryptoCompareCryptoHistoricalData(CryptoHistoricalData):
    """CryptoCompare Crypto Historical Data."""


class CryptoCompareCryptoHistoricalFetcher(
    Fetcher[
        CryptoCompareCryptoHistoricalQueryParams,
        list[CryptoCompareCryptoHistoricalData],
    ]
):
    """CryptoCompare Crypto Historical Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CryptoCompareCryptoHistoricalQueryParams:
        """Transform the query parameters."""
        return CryptoCompareCryptoHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CryptoCompareCryptoHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch historical crypto data from CryptoCompare."""
        symbol = query.symbol.replace(" ", "")
        currency = query.currency or "USD"
        limit = query.limit or 100
        aggregate = query.aggregate or 1

        url = build_historical_request_url(
            symbol=symbol, currency=currency, limit=limit, aggregate=aggregate
        )

        api_key = credentials.get("api_key") if credentials else None
        if api_key:
            url += f"&api_key={api_key}"

        return await amake_request(url, timeout=30)

    @staticmethod
    def transform_data(
        query: CryptoCompareCryptoHistoricalQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[CryptoCompareCryptoHistoricalData]:
        """Transform the API response into a list of CryptoHistoricalData."""
        if data.get("Err"):
            raise RuntimeError(f"CryptoCompare API error: {data['Err'].get('message', str(data['Err']))}")

        result_data = (
            data.get("Data", {}).get("Data", [])
            if isinstance(data.get("Data"), dict)
            else data.get("Data", [])
        )
        results: list[CryptoCompareCryptoHistoricalData] = []

        for entry in result_data:
            timestamp = entry.get("time")
            if isinstance(timestamp, (int, float)):
                date_val = datetime.fromtimestamp(timestamp)
            else:
                date_val = None

            results.append(
                CryptoCompareCryptoHistoricalData(
                    date=date_val,
                    open=entry.get("open"),
                    high=entry.get("high"),
                    low=entry.get("low"),
                    close=entry.get("close"),
                    volume=entry.get("volumeto"),
                )
            )

        return results
