"""Intrinio Forex available pairs fetcher."""


from typing import Any, Dict, List, Optional

from openbb_intrinio.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_pairs import (
    ForexPairsData,
    ForexPairsQueryParams,
)
from pydantic import Field


class IntrinioForexPairsQueryParams(ForexPairsQueryParams):
    """Intrinio Forex available pairs Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_forex_pairs_v2
    """


class IntrinioForexPairsData(ForexPairsData):
    """Intrinio Forex available pairs Data."""

    class Config:
        fields = {
            "name": "code",
        }

    code: str = Field(description="Code of the currency pair.")
    base_currency: str = Field(
        description="ISO 4217 currency code of the base currency."
    )
    quote_currency: str = Field(
        description="ISO 4217 currency code of the quote currency."
    )


class IntrinioForexPairsFetcher(
    Fetcher[
        IntrinioForexPairsQueryParams,
        List[IntrinioForexPairsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioForexPairsQueryParams:
        """Transform the query params."""

        return IntrinioForexPairsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioForexPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        url = f"{base_url}/forex/pairs?api_key={api_key}"

        return get_data_many(url, "pairs", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioForexPairsData]:
        """Return the transformed data."""

        return [IntrinioForexPairsData.parse_obj(d) for d in data]
