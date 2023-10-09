"""Polygon stocks end of day fetcher."""


from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import repeat
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_polygon.utils.helpers import get_data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_historical import (
    StockHistoricalData,
    StockHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import (
    Field,
    PositiveInt,
    PrivateAttr,
    model_validator,
)


class PolygonStockHistoricalQueryParams(StockHistoricalQueryParams):
    """Polygon stocks end of day Query.

    Source: https://polygon.io/docs/stocks/getting-started
    """

    interval: str = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    sort: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order of the data."
    )
    limit: PositiveInt = Field(
        default=49999, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    adjusted: bool = Field(
        default=True,
        description="Output time series is adjusted by historical split and dividend events.",
    )
    _multiplier: PositiveInt = PrivateAttr(default=None)
    _timespan: str = PrivateAttr(default=None)

    @model_validator(mode="after")
    @classmethod
    def get_api_interval_params(cls, values: "PolygonStockHistoricalQueryParams"):
        """Get the multiplier and timespan parameters for the Polygon API."""

        intervals = {
            "s": "second",
            "m": "minute",
            "h": "hour",
            "d": "day",
            "W": "week",
            "M": "month",
            "Q": "quarter",
            "Y": "year",
        }

        values._multiplier = int(values.interval[:-1])
        values._timespan = intervals[values.interval[-1]]

        return values


class PolygonStockHistoricalData(StockHistoricalData):
    """Polygon stocks end of day Data."""

    __alias_dict__ = {
        "date": "t",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
        "vwap": "vw",
    }

    transactions: Optional[PositiveInt] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
        alias="n",
    )


class PolygonStockHistoricalFetcher(
    Fetcher[
        PolygonStockHistoricalQueryParams,
        List[PolygonStockHistoricalData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonStockHistoricalQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return PolygonStockHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: PolygonStockHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        data: List = []

        def multiple_symbols(
            symbol: str, data: List[PolygonStockHistoricalData]
        ) -> None:
            results: List = []

            url = (
                "https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{query._multiplier}/{query._timespan}/"
                f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
                f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
            )

            response = get_data(url, **kwargs)

            next_url = response.get("next_url", None)
            results = response.get("results", [])

            while next_url:
                url = f"{next_url}&apiKey={api_key}"
                response = get_data(url, **kwargs)
                results.extend(response.get("results", []))
                next_url = response.get("next_url", None)

            for r in results:
                r["t"] = datetime.fromtimestamp(r["t"] / 1000)
                if query._timespan not in ["second", "minute", "hour"]:
                    r["t"] = r["t"].date()
                if "," in query.symbol:
                    r["symbol"] = symbol

            data.extend(results)

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[PolygonStockHistoricalData]:
        return [PolygonStockHistoricalData.model_validate(d) for d in data]
