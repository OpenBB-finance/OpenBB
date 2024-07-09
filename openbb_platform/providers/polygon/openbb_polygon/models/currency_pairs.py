"""Polygon Currency Available Pairs Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class PolygonCurrencyPairsQueryParams(CurrencyPairsQueryParams):
    """Polygon Currency Available Pairs Query.

    Source: https://polygon.io/docs/forex/get_v3_reference_tickers
    """


class PolygonCurrencyPairsData(CurrencyPairsData):
    """Polygon Currency Available Pairs Data."""

    __alias_dict__ = {
        "last_updated": "last_updated_utc",
        "delisted": "delisted_utc",
        "name": "currency_name",
        "symbol": "ticker",
    }
    currency_symbol: Optional[str] = Field(
        default=None, description="The symbol of the quote currency."
    )
    base_currency_symbol: Optional[str] = Field(
        default=None, description="The symbol of the base currency."
    )
    base_currency_name: Optional[str] = Field(
        default=None, description="Name of the base currency."
    )
    market: str = Field(description="Name of the trading market. Always 'fx'.")
    locale: str = Field(description="Locale of the currency pair.")
    last_updated: Optional[dateType] = Field(
        default=None, description="The date the reference data was last updated."
    )
    delisted: Optional[dateType] = Field(
        default=None, description="The date the item was delisted."
    )

    @field_validator("last_updated", "delisted", mode="before", check_fields=False)
    @classmethod
    def last_updated_utc_validate(cls, v):  # pylint: disable=E0213
        """Return the parsed last updated timestamp in UTC."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ").date() if v else None


class PolygonCurrencyPairsFetcher(
    Fetcher[
        PolygonCurrencyPairsQueryParams,
        List[PolygonCurrencyPairsData],
    ]
):
    """Polygon Currency Pairs Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCurrencyPairsQueryParams:
        """Transform the query parameters."""
        return PolygonCurrencyPairsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonCurrencyPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Polygon API."""
        # pylint: disable=import-outside-toplevel
        from openbb_polygon.utils.helpers import get_data

        api_key = credentials.get("polygon_api_key") if credentials else ""
        request_url = (
            f"https://api.polygon.io/v3/reference/"
            f"tickers?&market=fx&limit=1000"
            f"&apiKey={api_key}"
        )
        data = {"next_url": request_url}
        all_data: List[Dict] = []
        while "next_url" in data:
            data = await get_data(request_url, **kwargs)
            if isinstance(data, list):
                raise ValueError("Expected a dict, got a list")
            if len(data["results"]) == 0:
                raise OpenBBError(
                    "No results found. Please change your query parameters."
                )
            if data["status"] == "OK":
                results = data.get("results")
                if not isinstance(results, list):
                    raise ValueError(
                        "Expected 'results' to be a list, got something else."
                    )
                all_data.extend(results)
            elif data["status"] == "ERROR":
                raise UserWarning(data["error"])
            if "next_url" in data:
                request_url = f"{data['next_url']}&apiKey={api_key}"
        return all_data

    @staticmethod
    def transform_data(
        query: PolygonCurrencyPairsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonCurrencyPairsData]:
        """Filter data by search query and validate the model."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame(data)
        df["ticker"] = df["ticker"].str.replace("C:", "")
        if query.query:
            df = df[
                df["name"].str.contains(query.query, case=False)
                | df["base_currency_name"].str.contains(query.query, case=False)
                | df["currency_name"].str.contains(query.query, case=False)
                | df["base_currency_symbol"].str.contains(query.query, case=False)
                | df["currency_symbol"].str.contains(query.query, case=False)
                | df["ticker"].str.contains(query.query, case=False)
            ]
        if len(df) == 0:
            raise EmptyDataError(
                f"No results were found with the query supplied. -> {query.query}"
            )
        return [
            PolygonCurrencyPairsData.model_validate(d) for d in df.to_dict("records")
        ]
