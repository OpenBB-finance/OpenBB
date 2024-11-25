"""Intrinio Currency Available Pairs Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class IntrinioCurrencyPairsQueryParams(CurrencyPairsQueryParams):
    """Intrinio Currency Available Pairs Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_forex_pairs_v2
    """


class IntrinioCurrencyPairsData(CurrencyPairsData):
    """Intrinio Currency Available Pairs Data."""

    __alias_dict__ = {"symbol": "code"}

    base_currency: str = Field(
        description="ISO 4217 currency code of the base currency."
    )
    quote_currency: str = Field(
        description="ISO 4217 currency code of the quote currency."
    )


class IntrinioCurrencyPairsFetcher(
    Fetcher[
        IntrinioCurrencyPairsQueryParams,
        List[IntrinioCurrencyPairsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCurrencyPairsQueryParams:
        """Transform the query params."""
        return IntrinioCurrencyPairsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCurrencyPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_intrinio.utils.helpers import get_data_many

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        url = f"{base_url}/forex/pairs?api_key={api_key}"
        return await get_data_many(url, "pairs", **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioCurrencyPairsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCurrencyPairsData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame(data)
        if query.query:
            df = df[
                df["code"].str.contains(query.query, case=False)
                | df["base_currency"].str.contains(query.query, case=False)
                | df["quote_currency"].str.contains(query.query, case=False)
            ]
        if len(df) == 0:
            raise EmptyDataError(
                f"No results were found with the query supplied. -> {query.query}"
                + " Hint: Names and descriptions are not searchable from Intrinio, try 3-letter symbols."
            )
        return [
            IntrinioCurrencyPairsData.model_validate(d)
            for d in df.to_dict(orient="records")
        ]
