"""CoinGecko Crypto Historical Model."""

from typing import Any
from datetime import datetime

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)


class CoinGeckoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """CoinGecko Crypto Historical Query Params."""


class CoinGeckoCryptoHistoricalData(CryptoHistoricalData):
    """CoinGecko Crypto Historical Data."""


class CoinGeckoCryptoHistoricalFetcher(
    Fetcher[
        CoinGeckoCryptoHistoricalQueryParams,
        list[CoinGeckoCryptoHistoricalData],
    ]
):
    """Fetch Crypto Historical Data from CoinGecko."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CoinGeckoCryptoHistoricalQueryParams:
        """Transform Query Settings."""
        return CoinGeckoCryptoHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CoinGeckoCryptoHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Extract Data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        # By default CoinGecko api uses lowercase ID
        symbol_id = str(query.symbol).lower()
        url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart"
        
        days = "max"
        if query.start_date:
            now = datetime.now().date()
            if query.end_date:
                now = query.end_date
            delta = now - query.start_date
            days_int = delta.days
            if days_int > 0:
                days = str(days_int)
                
        req_params = {
            "vs_currency": "usd",
            "days": days,
        }

        # amake_request will automatically parse JSON into a dict
        res = await amake_request(url, method="GET", params=req_params, timeout=15)
        if isinstance(res, list):
            res = res[0]
        return res

    @staticmethod
    def transform_data(
        query: CoinGeckoCryptoHistoricalQueryParams, data: dict[str, Any], **kwargs: Any
    ) -> list[CoinGeckoCryptoHistoricalData]:
        """Transform Data."""
        results = []
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        
        volume_map = {item[0]: item[1] for item in volumes}
        
        for item in prices:
            ts = item[0]
            price = item[1]
            vol = volume_map.get(ts)
            
            result = CoinGeckoCryptoHistoricalData(
                date=datetime.fromtimestamp(ts / 1000.0),
                open=price,
                high=price,
                low=price,
                close=price,
                volume=vol,
            )
            results.append(result)
            
        return results
