"""CryptoCompare CryptoSearch Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_search import (
    CryptoSearchData,
    CryptoSearchQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_cryptocompare.utils.helpers import build_search_request_url


class CryptoCompareCryptoSearchQueryParams(CryptoSearchQueryParams):
    """CryptoCompare Crypto Search Query Parameters.

    Source: https://min-api.cryptocompare.com/documentation
    """


class CryptoCompareCryptoSearchData(CryptoSearchData):
    """CryptoCompare Crypto Search Data."""

    market_cap_rank: int | None = None


class CryptoCompareCryptoSearchFetcher(
    Fetcher[
        CryptoCompareCryptoSearchQueryParams,
        list[CryptoCompareCryptoSearchData],
    ]
):
    """CryptoCompare Crypto Search Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CryptoCompareCryptoSearchQueryParams:
        """Transform the query parameters."""
        return CryptoCompareCryptoSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CryptoCompareCryptoSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fetch the full cryptocurrency list from CryptoCompare."""
        url = build_search_request_url()

        api_key = credentials.get("api_key") if credentials else None
        if api_key:
            url += f"?api_key={api_key}"

        return await amake_request(url, timeout=30)

    @staticmethod
    def transform_data(
        query: CryptoCompareCryptoSearchQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[CryptoCompareCryptoSearchData]:
        """Transform the API response into a list of CryptoSearchData."""
        if data.get("Err"):
            raise RuntimeError(f"CryptoCompare API error: {data['Err'].get('message', str(data['Err']))}")

        coins = data.get("Data", {})
        query_text = (query.query or "").lower()
        results: list[CryptoCompareCryptoSearchData] = []

        for sym, info in coins.items():
            name = info.get("coin_name", "") or ""
            symbol = info.get("symbol", "")

            if query_text and query_text not in symbol.lower() and query_text not in name.lower():
                continue

            results.append(
                CryptoCompareCryptoSearchData(
                    symbol=symbol,
                    name=name,
                    market_cap_rank=info.get("rank"),
                )
            )

        return results
