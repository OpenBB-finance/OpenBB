"""TMX Index Info Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_info import (
    IndexInfoData,
    IndexInfoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

RATIOS = ("peRatio", "pbRatio", "priceToSales", "pcfRatio", "divYield")


class TmxIndexInfoQueryParams(IndexInfoQueryParams):
    """TMX Index Info Query Params."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )


class TmxIndexInfoData(IndexInfoData):
    """TMX Index Info Data."""

    __alias_dict__ = {
        "last_updated": "updated",
        "market_value": "total",
        "average_constituent_market_value": "average",
        "median_constituent_market_value": "median",
        "top_10_market_value": "sumtop10",
        "largest_constituent_market_value": "largest",
        "smallest_constituent_market_value": "smallest",
        "largest_constituent_weight": "largestweight",
        "smallest_constituent_weight": "smallestweight",
        "month_to_date": "monthtodate",
        "quarter_to_date": "quartertodate",
        "year_to_date": "yeartodate",
        "previous_day": "previousday",
        "pe_ratio": "peRatio",
        "pb_ratio": "pbRatio",
        "price_to_sales": "priceToSales",
        "price_to_cash_flow": "pcfRatio",
        "dividend_yield": "divYield",
    }

    last_updated: str | None = Field(
        default=None,
        description="The timestamp of the last update to the index file.",
    )
    market_value: float | None = Field(
        default=None,
        description="The total quoted market value of the index.",
    )
    average_constituent_market_value: float | None = Field(
        default=None,
        description="The average quoted market value of a constituent.",
    )
    median_constituent_market_value: float | None = Field(
        default=None,
        description="The median quoted market value of a constituent.",
    )
    top_10_market_value: float | None = Field(
        default=None,
        description="The combined quoted market value of the ten largest constituents.",
    )
    largest_constituent_market_value: float | None = Field(
        default=None,
        description="The quoted market value of the largest constituent.",
    )
    smallest_constituent_market_value: float | None = Field(
        default=None,
        description="The quoted market value of the smallest constituent.",
    )
    largest_constituent_weight: float | None = Field(
        default=None,
        description="The weight of the largest constituent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    smallest_constituent_weight: float | None = Field(
        default=None,
        description="The weight of the smallest constituent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    previous_day: float | None = Field(
        default=None,
        description="The price return over the previous session.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_to_date: float | None = Field(
        default=None,
        description="The month-to-date price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    quarter_to_date: float | None = Field(
        default=None,
        description="The quarter-to-date price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_to_date: float | None = Field(
        default=None,
        description="The year-to-date price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    pe_ratio: float | None = Field(
        default=None,
        description="The price-to-earnings ratio of the index.",
    )
    pb_ratio: float | None = Field(
        default=None,
        description="The price-to-book ratio of the index.",
    )
    price_to_sales: float | None = Field(
        default=None,
        description="The price-to-sales ratio of the index.",
    )
    price_to_cash_flow: float | None = Field(
        default=None,
        description="The price-to-cash-flow ratio of the index.",
    )
    dividend_yield: float | None = Field(
        default=None,
        description="The dividend yield of the index.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator(
        "largest_constituent_weight",
        "smallest_constituent_weight",
        "previous_day",
        "month_to_date",
        "quarter_to_date",
        "year_to_date",
        "dividend_yield",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxIndexInfoFetcher(Fetcher[TmxIndexInfoQueryParams, list[TmxIndexInfoData]]):
    """TMX Index Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxIndexInfoQueryParams:
        """Transform the query."""
        return TmxIndexInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Read the index file and the published key data.

        Raises
        ------
        OpenBBError
            If the symbol is not one of the published indices.
        """
        import asyncio

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import get_data_from_url

        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"

        async def key_data() -> dict:
            try:
                response = await amake_gql_request(
                    "getIndexKeyData",
                    gql.INDEX_KEY_DATA,
                    {"symbol": query.symbol},
                    use_cache=query.use_cache,
                )
            except Exception:  # noqa: BLE001
                return {}

            return (response or {}).get("getIndexKeyData") or {}

        published, ratios = await asyncio.gather(
            get_data_from_url(url, use_cache=query.use_cache), key_data()
        )
        indices = (published or {}).get("indices") or {}

        if not indices:
            raise EmptyDataError

        if query.symbol not in indices:
            raise OpenBBError(f"Index {query.symbol} was not found. Check the symbol.")

        return {"index": indices[query.symbol], "key_data": ratios}

    @staticmethod
    def transform_data(
        query: TmxIndexInfoQueryParams, data: dict, **kwargs: Any
    ) -> list[TmxIndexInfoData]:
        """Flatten the file entry, its performance, and its market value."""
        import re
        from html import unescape

        index = data["index"]
        description = unescape(re.sub(r"<[^>]+>", " ", index.get("overview_en") or ""))
        record = {
            "symbol": query.symbol,
            "name": index.get("name_en"),
            "description": re.sub(r"\s+", " ", description).strip() or None,
            "factsheet": index.get("factsheet"),
            "methodology": index.get("methodology"),
            "num_constituents": index.get("nb_constituents"),
            "updated": index.get("updated"),
            **(index.get("quotedmarketvalue") or {}),
            **(index.get("performance") or {}),
            **{k: v for k, v in data["key_data"].items() if k in RATIOS},
        }

        return [TmxIndexInfoData.model_validate(record)]
