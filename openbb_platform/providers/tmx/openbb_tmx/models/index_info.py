"""TMX Index Info Model"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.index_info import (
    IndexInfoData,
    IndexInfoQueryParams,
)
from openbb_tmx.utils.helpers import get_all_index_data, get_index_data
from pydantic import Field


class TmxIndexInfoQueryParams(IndexInfoQueryParams):
    """TMX Index Info Query Params."""


class TmxIndexInfoData(IndexInfoData):
    """TMX Index Info Data."""

    __alias_dict__ = {
        "name": "name_en",
        "description": "overview_en",
        "num_constituents": "numConstituents",
    }

    return_day: Optional[float] = Field(
        description="The one-day return.", default=None, alias="prevDayPriceReturn"
    )
    return_month: Optional[float] = Field(
        description="The one-month return.", default=None, alias="prevMonthPriceReturn"
    )
    return_quarter: Optional[float] = Field(
        description="The one-quarter return.",
        default=None,
        alias="prevQuarterPriceReturn",
    )
    return_ytd: Optional[float] = Field(
        description="The year-to-date return.", default=None, alias="ytdPriceReturn"
    )
    pe_ratio: Optional[float] = Field(
        description="The price-to-earnings ratio.", default=None, alias="peRatio"
    )
    pb_ratio: Optional[float] = Field(
        description="The price-to-book ratio.", default=None, alias="pbRatio"
    )
    price_to_sales: Optional[float] = Field(
        description="The price-to-sales ratio.", default=None, alias="priceToSales"
    )
    div_yield: Optional[float] = Field(
        description="The dividend yield.", default=None, alias="divYield"
    )
    price_to_cashflow: Optional[float] = Field(
        description="The price-to-cashflow ratio.", default=None, alias="pcfRatio"
    )
    market_cap: Optional[float] = Field(
        description="The total market cap of the index.",
        default=None,
        alias="adjMarketCap",
    )
    constituent_top10_market_cap: Optional[float] = Field(
        description="The market cap of the top 10 constituents.",
        default=None,
        alias="top10HoldingsAdjMarketCap",
    )
    constituent_avg_market_cap: Optional[float] = Field(
        description="The average market cap of an index constituent.",
        default=None,
        alias="avgConstituentMarketCap",
    )
    constituent_largest_market_cap: Optional[float] = Field(
        description="The largest constituent's market cap.",
        default=None,
        alias="marketCapLargest",
    )
    constituent_largest_weight: Optional[float] = Field(
        description="The largest constituent's weight.",
        default=None,
        alias="percentWeightLargestConstituent",
    )
    constituent_smallest_market_cap: Optional[float] = Field(
        description="The smallest constituent's market cap.",
        default=None,
        alias="marketCapSmallest",
    )
    constituent_smallest_weight: Optional[float] = Field(
        description="The smallest constituent's weight.",
        default=None,
        alias="percentWeightSmallestConstituent",
    )
    constituent_median_market_cap: Optional[float] = Field(
        description="The median market cap of index constituents.",
        default=None,
        alias="marketCapMedian",
    )
    updated: Optional[datetime] = Field(
        description="The timestamp of when the data was updated.", default=None
    )


class TmxIndexInfoFetcher(Fetcher[TmxIndexInfoQueryParams, List[TmxIndexInfoData]]):
    """TMX Index Info Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxIndexInfoQueryParams:
        """Transform the query."""

        params["symbol"] = (
            params["symbol"]
            .upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        if "^" not in params["symbol"]:
            params["symbol"] = f"^{params['symbol']}"

        return TmxIndexInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxIndexInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the data from the TMX endpoint."""

        data = {}
        all_data = {}
        _all_data = get_all_index_data()
        if (
            _all_data != {}
            and "indices" in _all_data
            and query.symbol in _all_data["indices"]
        ):
            all_data = _all_data["indices"][query.symbol]

        _data = get_index_data(query.symbol)
        if _data != {} and "data" in _data and "keyData" in _data["data"]:
            data = _data["data"]["keyData"]

        items = [
            "methodology",
            "factsheet",
            "name_en",
            "overview_en",
            "quotedmarketvalue",
            "updated",
        ]
        for item in items:
            if item in all_data:
                if item == "quotedmarketvalue":
                    weights = ["largest", "smallest", "smallestweight", "median"]
                    for weight in weights:
                        if weight in all_data["quotedmarketvalue"]:
                            data.update(
                                {
                                    "marketCapLargest": all_data["quotedmarketvalue"][
                                        "largest"
                                    ],
                                    "marketCapSmallest": all_data["quotedmarketvalue"][
                                        "smallest"
                                    ],
                                    "percentWeightSmallestConstituent": all_data[
                                        "quotedmarketvalue"
                                    ]["smallestweight"],
                                    "marketCapMedian": all_data["quotedmarketvalue"][
                                        "median"
                                    ],
                                }
                            )
                else:
                    data.update({item: all_data[item]})

        if "overview_en" in data:
            data["overview_en"] = (
                data["overview_en"]
                .replace("<p>", "")
                .replace("</p>", "")
                .replace("amp;", "")
                .replace("\r\n", "")
            )

        if data != {}:
            data.update({"symbol": query.symbol})

        return data

    @staticmethod
    def transform_data(data: Dict) -> List[TmxIndexInfoData]:
        """Transform the data."""
        return [TmxIndexInfoData.model_validate(data)]
