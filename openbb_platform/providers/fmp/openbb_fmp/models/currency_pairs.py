"""FMP Currency Available Pairs Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FMPCurrencyPairsQueryParams(CurrencyPairsQueryParams):
    """FMP Currency Available Pairs Query.

    Source: http://site.financialmodelingprep.com/developer/docs/stock-ticker-symbol-lookup-api/?direct=true
    """


class FMPCurrencyPairsData(CurrencyPairsData):
    """FMP Currency Available Pairs Data."""

    symbol: str = Field(description="Symbol of the currency pair.")
    currency: str = Field(description="Base currency of the currency pair.")
    stock_exchange: Optional[str] = Field(
        default=None, description="Stock exchange of the currency pair."
    )
    exchange_short_name: Optional[str] = Field(
        default=None,
        description="Short name of the stock exchange of the currency pair.",
    )


class FMPCurrencyPairsFetcher(
    Fetcher[
        FMPCurrencyPairsQueryParams,
        List[FMPCurrencyPairsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCurrencyPairsQueryParams:
        """Transform the query params."""
        return FMPCurrencyPairsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCurrencyPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCurrencyPairsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCurrencyPairsData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame(data)
        if query.query:
            df = df[
                df["name"].str.contains(query.query, case=False)
                | df["symbol"].str.contains(query.query, case=False)
                | df["currency"].str.contains(query.query, case=False)
                | df["stockExchange"].str.contains(query.query, case=False)
                | df["exchangeShortName"].str.contains(query.query, case=False)
            ]
        if len(df) == 0:
            raise EmptyDataError(
                f"No results were found with the query supplied. -> {query.query}"
                + " Hint: Names and descriptions are not searchable from FMP, try 3-letter symbols."
            )
        return [FMPCurrencyPairsData.model_validate(d) for d in df.to_dict("records")]
