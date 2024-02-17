"""TMX Index Snapshots Model"""

# pylint: disable=unused-argument
import json
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_snapshots import (
    IndexSnapshotsData,
    IndexSnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import (
    NASDAQ_GIDS,
    get_data_from_gql,
    get_data_from_url,
    get_random_agent,
    tmx_indices_backend,
)
from pydantic import Field, field_validator


class TmxIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """TMX Index Snapshots Query Params."""

    region: Literal[None, "ca", "us"] = Field(default="ca")
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
    year_high: Optional[float] = Field(
        default=None, description="The 52-week high of the index."
    )
    year_low: Optional[float] = Field(
        default=None, description="The 52-week low of the index."
    )
    return_mtd: Optional[float] = Field(
        default=None,
        description="The month-to-date return of the index, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_qtd: Optional[float] = Field(
        default=None,
        description="The quarter-to-date return of the index, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_ytd: Optional[float] = Field(
        default=None,
        description="The year-to-date return of the index, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    total_market_value: Optional[float] = Field(
        default=None,
        description="The total quoted market value of the index.",
    )
    number_of_constituents: Optional[int] = Field(
        default=None,
        description="The number of constituents in the index.",
    )
    constituent_average_market_value: Optional[float] = Field(
        default=None,
        description="The average quoted market value of the index constituents.",
    )
    constituent_median_market_value: Optional[float] = Field(
        default=None,
        description="The median quoted market value of the index constituents.",
    )
    constituent_top10_market_value: Optional[float] = Field(
        default=None,
        description="The sum of the top 10 quoted market values of the index constituents.",
    )
    constituent_largest_market_value: Optional[float] = Field(
        default=None,
        description="The largest quoted market value of the index constituents.",
    )
    constituent_largest_weight: Optional[float] = Field(
        default=None,
        description="The largest weight of the index constituents, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    constituent_smallest_market_value: Optional[float] = Field(
        default=None,
        description="The smallest quoted market value of the index constituents.",
    )
    constituent_smallest_weight: Optional[float] = Field(
        default=None,
        description="The smallest weight of the index constituents, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
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
        List[TmxIndexSnapshotsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxIndexSnapshotsQueryParams:
        """Transform the query."""
        return TmxIndexSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"
        user_agent = get_random_agent()
        results = []
        if query.region == "ca":
            data = await get_data_from_url(
                url,
                use_cache=query.use_cache,
                backend=tmx_indices_backend,
            )
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

            # Get current levels for each index.

            payload = gql.get_quote_for_symbols_payload.copy()
            payload["variables"]["symbols"] = symbols

            url = "https://app-money.tmx.com/graphql"
            response = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": "https://money.tmx.com/en/quote/^TSX",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=5,
            )
            if response.get("data") and response["data"].get("getQuoteForSymbols"):
                quote_data = response["data"]["getQuoteForSymbols"]
                for d in data:
                    if "longname" in d:
                        d.pop("longname")
                    if "percentChange" in d:
                        d.pop("percentChange")
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
            payload = gql.get_quote_for_symbols_payload.copy()
            payload["variables"]["symbols"] = symbols

            url = "https://app-money.tmx.com/graphql"
            response = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": "https://money.tmx.com/en/quote/^TSX",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=5,
            )
            if response.get("data") and response["data"].get("getQuoteForSymbols"):
                results = response["data"]["getQuoteForSymbols"]
            for item in results:
                item["change_percent"] = item.pop("percentChange")

        return results

    @staticmethod
    def transform_data(
        query: TmxIndexSnapshotsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxIndexSnapshotsData]:
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
