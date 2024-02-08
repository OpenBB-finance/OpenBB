"""TMX Equity Gainers Model."""

# pylint: disable=unused-argument
import json
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field, field_validator, model_validator

STOCK_LISTS_DICT = {
    "dividend": "TOP_DIVIDEND",
    "energy": "TOP_ENERGY",
    "healthcare": "TOP_HEALTHCARE",
    "industrials": "TOP_INDUSTRIALS",
    "price_performer": "TOP_PRICE_PERFORMER",
    "rising_stars": "RISING_STARS",
    "real_estate": "TOP_REAL_ESTATE",
    "tech": "TOP_TECH",
    "utilities": "TOP_UTILITIES",
    "52w_high": "TOP_WEEK_52_HIGH",
    "volume": "TOP_VOLUME",
}

STOCK_LISTS = Literal[
    "dividend",
    "energy",
    "healthcare",
    "industrials",
    "price_performer",
    "rising_stars",
    "real_estate",
    "tech",
    "utilities",
    "52w_high",
    "volume",
]


class TmxGainersQueryParams(EquityPerformanceQueryParams):
    """TMX Gainers Query Params."""

    category: STOCK_LISTS = Field(
        default="price_performer",
        description="The category of list to retrieve. Defaults to `price_performer`.",
    )


class TmxGainersData(EquityPerformanceData):
    """TMX Gainers Data."""

    __alias_dict__ = {
        "name": "longName",
        "change": "priceChange",
        "percent_change": "percentChange",
        "thirty_day_price_change": "30 Day Price Change",
        "dividend_yield": "Dividend Yield",
        "year_high": "52 Week High",
        "avg_volume_10d": "10 Day Avg. Volume",
        "ninety_day_price_change": "90 Day Price Change",
    }
    rank: int = Field(description="The rank of the stock in the list.")

    @field_validator("percent_change", mode="after", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else 0

    @model_validator(mode="before")
    @classmethod
    def check_metric(cls, values):
        for k, v in values.items():
            if v is None or v == "-":
                values[k] = 0
            if k in ["Dividend Yield"]:
                values[k] = float(v) / 100 if v else None
        return values


class TmxGainersFetcher(
    Fetcher[
        TmxGainersQueryParams,
        List[TmxGainersData],
    ]
):
    """TMX Gainers Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxGainersQueryParams:
        """Transform the query."""
        return TmxGainersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxGainersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[TmxGainersData]:
        """Return the raw data from the TMX endpoint."""

        user_agent = get_random_agent()
        payload = gql.get_stock_list_payload.copy()
        payload["variables"]["stockListId"] = STOCK_LISTS_DICT[query.category]

        url = "https://app-money.tmx.com/graphql"
        response = await get_data_from_gql(
            method="POST",
            url=url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": "https://money.tmx.com",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "*/*",
            },
            timeout=5,
        )
        if "errors" in response:
            raise EmptyDataError()
        results = response["data"]["stockList"].get("listItems")
        metric = response["data"]["stockList"].get("metricTitle")
        for i in range(len(results)):  # pylint: disable=C0200
            if "metric" in results[i]:
                results[i][metric] = results[i]["metric"]
                del results[i]["metric"]

        return results

    @staticmethod
    def transform_data(
        query: TmxGainersQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxGainersData]:
        """Transform the data to the model."""
        return [TmxGainersData.model_validate(d) for d in data]
