"""FMP Currency Available Pairs Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FMPCurrencyPairsQueryParams(CurrencyPairsQueryParams):
    """FMP Currency Available Pairs Query.

    Source: https://site.financialmodelingprep.com/developer/docs#forex
    """


class FMPCurrencyPairsData(CurrencyPairsData):
    """FMP Currency Available Pairs Data."""

    symbol: str = Field(description="Symbol of the currency pair.")
    from_currency: str = Field(description="Base currency of the currency pair.")
    to_currency: str = Field(description="Quote currency of the currency pair.")
    from_name: str = Field(description="Name of the base currency.")
    to_name: str = Field(description="Name of the quote currency.")


class FMPCurrencyPairsFetcher(
    Fetcher[
        FMPCurrencyPairsQueryParams,
        list[FMPCurrencyPairsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCurrencyPairsQueryParams:
        """Transform the query params."""
        return FMPCurrencyPairsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCurrencyPairsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = f"https://financialmodelingprep.com/stable/forex-list?apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCurrencyPairsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCurrencyPairsData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")

        df = DataFrame(data)

        if query.query:
            df = df[
                df["symbol"].str.contains(query.query, case=False)
                | df["fromCurrency"].str.contains(query.query, case=False)
                | df["toCurrency"].str.contains(query.query, case=False)
                | df["fromName"].str.contains(query.query, case=False)
                | df["toName"].str.contains(query.query, case=False)
            ]

        if len(df) == 0:
            raise EmptyDataError(
                f"No results were found with the query supplied. -> {query.query}"
            )
        return [FMPCurrencyPairsData.model_validate(d) for d in df.to_dict("records")]
