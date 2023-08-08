"""Polygon available pairs fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_pairs import (
    ForexPairsData,
    ForexPairsQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PositiveInt, validator

from openbb_polygon.utils.helpers import get_data


class PolygonForexPairsQueryParams(ForexPairsQueryParams):
    """Polygon available pairs Query.

    Source: https://polygon.io/docs/forex/get_v3_reference_tickers
    """

    symbol: Optional[str] = Field(description="Symbol of the pair to search.")
    date: Optional[dateType] = Field(
        default=datetime.now().date(), description=QUERY_DESCRIPTIONS.get("date", "")
    )
    search: Optional[str] = Field(
        default="",
        description="Search for terms within the ticker and/or company name.",
    )
    active: Optional[Literal[True, False]] = Field(
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


class PolygonForexPairsData(ForexPairsData):
    """Polygon available pairs Data."""

    market: str = Field(description="The name of the trading market. Always 'fx'.")
    locale: str = Field(description="The locale of the currency pair.")
    currency_symbol: str = Field(description="The symbol of the quote currency.")
    currency_name: str = Field(description="The name of the quote currency.")
    base_currency_symbol: str = Field(description="The symbol of the base currency.")
    base_currency_name: str = Field(description="The name of the base currency.")
    last_updated_utc: datetime = Field(description="The last updated timestamp in UTC.")
    delisted_utc: Optional[datetime] = Field(
        description="The delisted timestamp in UTC."
    )

    @validator("last_updated_utc", pre=True, check_fields=False)
    def last_updated_utc_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")

    @validator("delisted_utc", pre=True, check_fields=False)
    def delisted_utc_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")


class PolygonForexPairsFetcher(
    Fetcher[
        PolygonForexPairsQueryParams,
        List[PolygonForexPairsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonForexPairsQueryParams:
        return PolygonForexPairsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonForexPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[PolygonForexPairsData]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        tickers = f"ticker=C:{query.symbol}" if query.symbol else ""
        request_url = (
            f"https://api.polygon.io/v3/reference/"
            f"tickers?{tickers}&market=fx&date={query.date}&"
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
                all_data.extend(data["results"])
            elif data["status"] == "ERROR":
                raise UserWarning(data["error"])

            if "next_url" in data:
                request_url = f"{data['next_url']}&apiKey={api_key}"

        return all_data

    @staticmethod
    def transform_data(
        data: List[PolygonForexPairsData],
    ) -> List[PolygonForexPairsData]:
        return data
