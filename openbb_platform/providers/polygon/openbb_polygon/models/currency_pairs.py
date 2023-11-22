"""Polygon Currency Available Pairs Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_polygon.utils.helpers import get_data
from pydantic import Field, PositiveInt, field_validator


class PolygonCurrencyPairsQueryParams(CurrencyPairsQueryParams):
    """Polygon Currency Available Pairs Query.

    Source: https://polygon.io/docs/forex/get_v3_reference_tickers
    """

    symbol: Optional[str] = Field(
        default=None, description="Symbol of the pair to search."
    )
    date: Optional[dateType] = Field(
        default=datetime.now().date(), description=QUERY_DESCRIPTIONS.get("date", "")
    )
    search: Optional[str] = Field(
        default="",
        description="Search for terms within the ticker and/or company name.",
    )
    active: Optional[bool] = Field(
        default=True,
        description="Specify if the tickers returned should be actively traded on the queried date.",
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        default="asc", description="Order data by ascending or descending."
    )
    sort: Optional[
        Literal[
            "ticker",
            "name",
            "market",
            "locale",
            "currency_symbol",
            "currency_name",
            "base_currency_symbol",
            "base_currency_name",
            "last_updated_utc",
            "delisted_utc",
        ]
    ] = Field(default="", description="Sort field used for ordering.")
    limit: Optional[PositiveInt] = Field(
        default=1000, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class PolygonCurrencyPairsData(CurrencyPairsData):
    """Polygon Currency Available Pairs Data."""

    market: str = Field(description="Name of the trading market. Always 'fx'.")
    locale: str = Field(description="Locale of the currency pair.")
    currency_symbol: Optional[str] = Field(
        default=None, description="The symbol of the quote currency."
    )
    currency_name: Optional[str] = Field(
        default=None, description="Name of the quote currency."
    )
    base_currency_symbol: Optional[str] = Field(
        default=None, description="The symbol of the base currency."
    )
    base_currency_name: Optional[str] = Field(
        default=None, description="Name of the base currency."
    )
    last_updated_utc: datetime = Field(description="The last updated timestamp in UTC.")
    delisted_utc: Optional[datetime] = Field(
        default=None, description="The delisted timestamp in UTC."
    )

    @field_validator("last_updated_utc", mode="before", check_fields=False)
    @classmethod
    def last_updated_utc_validate(cls, v):  # pylint: disable=E0213
        """Return the parsed last updated timestamp in UTC."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")

    @field_validator("delisted_utc", mode="before", check_fields=False)
    @classmethod
    def delisted_utc_validate(cls, v):  # pylint: disable=E0213
        """Return the parsed delisted timestamp in UTC."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")


class PolygonCurrencyPairsFetcher(
    Fetcher[
        PolygonCurrencyPairsQueryParams,
        List[PolygonCurrencyPairsData],
    ]
):
    """Transform the query, extract and transform the data from the Polygon endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCurrencyPairsQueryParams:
        """Transform the query parameters. Ticker is set if symbol is provided."""
        transform_params = params
        now = datetime.now().date()
        transform_params["symbol"] = (
            f"ticker=C:{params.get('symbol').upper()}" if params.get("symbol") else ""
        )
        if params.get("date") is None:
            transform_params["start_date"] = now

        return PolygonCurrencyPairsQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: PolygonCurrencyPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Extract the data from the Polygon API."""
        api_key = credentials.get("polygon_api_key") if credentials else ""

        request_url = (
            f"https://api.polygon.io/v3/reference/"
            f"tickers?{query.symbol}&market=fx&date={query.date}&"
            f"search={query.search}&active={query.active}&order={query.order}&"
            f"limit={query.limit}&sort={query.sort}&apiKey={api_key}"
        )

        data = {"next_url": request_url}
        all_data: List[Dict] = []

        while "next_url" in data:
            data = get_data(request_url, **kwargs)

            if isinstance(data, list):
                raise ValueError("Expected a dict, got a list")

            if len(data["results"]) == 0:
                raise RuntimeError(
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
        data: List[dict],
        **kwargs: Any,
    ) -> List[PolygonCurrencyPairsData]:
        """Transform the data into a list of PolygonCurrencyPairsData."""
        return [PolygonCurrencyPairsData.model_validate(d) for d in data]
