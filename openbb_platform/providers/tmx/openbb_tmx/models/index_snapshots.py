"""TMX Index Snapshots Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_snapshots import (
    IndexSnapshotsData,
    IndexSnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tmx.utils.choices import literal_choices


class TmxIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """TMX Index Snapshots Query Params."""

    __json_schema_extra__ = {
        "region": {"x-widget_config": {"options": literal_choices(("ca", "us"))}}
    }

    region: Literal["ca", "us"] | None = Field(
        default="ca",
        description="The region the indices are published for.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )


class TmxIndexSnapshotsData(IndexSnapshotsData):
    """TMX Index Snapshots Data."""

    __alias_dict__ = {
        "name": "longname",
        "prev_close": "prevClose",
        "change": "priceChange",
        "change_percent": "previousday",
        "year_high": "weeks52high",
        "year_low": "weeks52low",
        "return_mtd": "monthtodate",
        "return_qtd": "quartertodate",
        "return_ytd": "yeartodate",
        "total_market_value": "total",
        "constituent_average_market_value": "average",
        "constituent_median_market_value": "median",
        "constituent_top10_market_value": "sumtop10",
        "constituent_largest_market_value": "largest",
        "constituent_largest_weight": "largestweight",
        "constituent_smallest_market_value": "smallest",
        "constituent_smallest_weight": "smallestweight",
    }
    year_high: float | None = Field(
        default=None, description="The 52-week high of the index."
    )
    year_low: float | None = Field(
        default=None, description="The 52-week low of the index."
    )
    return_mtd: float | None = Field(
        default=None,
        description="The month-to-date return of the index, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_qtd: float | None = Field(
        default=None,
        description="The quarter-to-date return of the index, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_ytd: float | None = Field(
        default=None,
        description="The year-to-date return of the index, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    total_market_value: float | None = Field(
        default=None,
        description="The total quoted market value of the index.",
    )
    number_of_constituents: int | None = Field(
        default=None,
        description="The number of constituents in the index.",
    )
    constituent_average_market_value: float | None = Field(
        default=None,
        description="The average quoted market value of the index constituents.",
    )
    constituent_median_market_value: float | None = Field(
        default=None,
        description="The median quoted market value of the index constituents.",
    )
    constituent_top10_market_value: float | None = Field(
        default=None,
        description="The sum of the top 10 quoted market values of the index constituents.",
    )
    constituent_largest_market_value: float | None = Field(
        default=None,
        description="The largest quoted market value of the index constituents.",
    )
    constituent_largest_weight: float | None = Field(
        default=None,
        description="The largest weight of the index constituents, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    constituent_smallest_market_value: float | None = Field(
        default=None,
        description="The smallest quoted market value of the index constituents.",
    )
    constituent_smallest_weight: float | None = Field(
        default=None,
        description="The smallest weight of the index constituents, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator(
        "return_mtd",
        "return_qtd",
        "return_ytd",
        "change_percent",
        "constituent_largest_weight",
        "constituent_smallest_weight",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return round(float(v) / 100, 6) if v else None

    @field_validator(
        "year_high",
        "year_low",
        "price",
        "prev_close",
        "change",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def round_floating(cls, v):
        """Round floating values to two decimals."""
        return round(float(v), 2) if v else None


class TmxIndexSnapshotsFetcher(
    Fetcher[
        TmxIndexSnapshotsQueryParams,
        list[TmxIndexSnapshotsData],
    ]
):
    """TMX Index Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxIndexSnapshotsQueryParams:
        """Transform the query."""
        return TmxIndexSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexSnapshotsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import NASDAQ_GIDS, get_data_from_url

        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"
        results = []

        if query.region == "ca":
            data = await get_data_from_url(url, use_cache=query.use_cache)
            if not data:
                raise EmptyDataError
            symbols = []

            for symbol in data["indices"]:
                symbols.append(symbol)
                new_data = {}
                performance = data["indices"][symbol].get("performance", {})
                market_value = data["indices"][symbol].get("quotedmarketvalue", {})
                new_data.update(
                    {
                        "symbol": symbol,
                        "name": data["indices"][symbol].get("name_en", None),
                        "currency": (
                            "USD"
                            if "(USD)" in data["indices"][symbol]["name_en"]
                            else "CAD"
                        ),
                        **performance,
                        **market_value,
                    }
                )
                results.append(new_data)

            response = await amake_gql_request(
                "getQuoteForSymbols", gql.QUOTE_FOR_SYMBOLS, {"symbols": symbols}
            )

            if response and response.get("getQuoteForSymbols"):
                quote_data = response["getQuoteForSymbols"]
                for row in results:
                    row.pop("longname", None)
                    row.pop("percentChange", None)
                merged_list = [
                    {
                        **d1,
                        **next(
                            (d2 for d2 in quote_data if d2["symbol"] == d1["symbol"]),
                            {},
                        ),
                    }
                    for d1 in results
                ]
                results = merged_list

        if query.region == "us":
            symbols = [f"{symbol}:US" for symbol in NASDAQ_GIDS]
            response = await amake_gql_request(
                "getQuoteForSymbols", gql.QUOTE_FOR_SYMBOLS, {"symbols": symbols}
            )

            if response and response.get("getQuoteForSymbols"):
                results = [
                    item
                    for item in response["getQuoteForSymbols"]
                    if item.get("price") is not None
                ]

            for item in results:
                item["change_percent"] = item.pop("percentChange", None)

        return results

    @staticmethod
    def transform_data(
        query: TmxIndexSnapshotsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxIndexSnapshotsData]:
        """Return the transformed data."""
        return [
            TmxIndexSnapshotsData.model_validate(
                {
                    "change_percent" if k == "percentChange" else k: (
                        None if v in ["", 0] else v
                    )
                    for k, v in d.items()
                }
            )
            for d in data
            if "price" in d and d["price"] is not None
        ]
