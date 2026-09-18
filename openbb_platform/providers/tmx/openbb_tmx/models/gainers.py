"""TMX Equity Gainers Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator

from openbb_tmx.utils.choices import literal_choices

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
    "cdr": "CIBC_CDR_SL",
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
    "cdr",
]


class TmxGainersQueryParams(EquityPerformanceQueryParams):
    """TMX Gainers Query Params."""

    __json_schema_extra__ = {
        "category": {
            "multiple_items_allowed": False,
            "choices": list(STOCK_LISTS_DICT),
            "x-widget_config": {
                "options": literal_choices(
                    tuple(STOCK_LISTS_DICT),
                    **{"cdr": "CDR", "52w_high": "52-Week High"},
                )
            },
        },
    }

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
    thirty_day_price_change: float | None = Field(
        default=None,
        description="30 Day Price Change.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ninety_day_price_change: float | None = Field(
        default=None,
        description="90 Day Price Change.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    dividend_yield: float | None = Field(
        default=None,
        description="Dividend Yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_volume_10d: float | None = Field(
        default=None,
        description="10 Day Avg. Volume.",
    )
    rank: int = Field(description="The rank of the stock in the list.")

    @field_validator("percent_change", mode="after", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else 0

    @model_validator(mode="before")
    @classmethod
    def check_metric(cls, values):
        """Check for missing metrics."""
        for k, v in values.items():
            if v is None or v == "-":
                values[k] = 0
            if k in ["Dividend Yield"]:
                values[k] = float(v) / 100 if v else None
        return values


class TmxGainersFetcher(
    Fetcher[
        TmxGainersQueryParams,
        list[TmxGainersData],
    ]
):
    """TMX Gainers Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxGainersQueryParams:
        """Transform the query."""
        return TmxGainersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxGainersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[TmxGainersData]:
        """Return the raw data from the TMX endpoint."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        response = await amake_gql_request(
            "getStockListSymbolsWithQuote",
            gql.STOCK_LIST,
            {
                "stockListId": STOCK_LISTS_DICT[query.category],
                "locale": "en",
            },
        )
        stock_list = (response or {}).get("stockList")

        if not stock_list:
            raise EmptyDataError()

        results = stock_list.get("listItems")
        metric = stock_list.get("metricTitle")
        for i in range(len(results)):  # pylint: disable=C0200
            if "metric" in results[i]:
                results[i][metric] = results[i]["metric"]
                del results[i]["metric"]

        return results

    @staticmethod
    def transform_data(
        query: TmxGainersQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxGainersData]:
        """Transform the data to the model."""
        return [TmxGainersData.model_validate(d) for d in data]
