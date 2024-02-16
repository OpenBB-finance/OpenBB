"""Finviz Price Performance Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from finvizfinance.screener import performance
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FinvizPricePerformanceQueryParams(RecentPerformanceQueryParams):
    """
    Finviz Price Performance Query.

    Source: https://finviz.com/screener.ashx
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FinvizPricePerformanceData(RecentPerformanceData):
    """Finviz Price Performance Data."""

    __alias_dict__ = {
        "symbol": "Ticker",
        "one_week": "Perf Week",
        "one_month": "Perf Month",
        "three_month": "Perf Quart",
        "six_month": "Perf Half",
        "one_year": "Perf Year",
        "ytd": "Perf YTD",
        "volatility_week": "Volatility W",
        "volatility_month": "Volatility M",
        "price": "Price",
        "one_day": "Change",
        "volume": "Volume",
        "average_volume": "Avg Volume",
        "relative_volume": "Rel Volume",
        "analyst_score": "Recom",
    }

    volatility_week: Optional[float] = Field(
        default=None,
        description="One-week realized volatility, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "fontend_multiply": 100},
    )
    volatility_month: Optional[float] = Field(
        default=None,
        description="One-month realized volatility, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "fontend_multiply": 100},
    )
    price: Optional[float] = Field(
        default=None,
        description="Last Price.",
    )
    volume: Optional[float] = Field(
        default=None,
        description="Current volume.",
    )
    average_volume: Optional[float] = Field(
        default=None,
        description="Average daily volume.",
    )
    relative_volume: Optional[float] = Field(
        default=None,
        description="Relative volume as a ratio of current volume to average volume.",
    )
    analyst_recommendation: Optional[float] = Field(
        default=None,
        description="The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell.",
    )
    symbol: Optional[str] = Field(
        default=None,
        description="The ticker symbol.",
    )


class FinvizPricePerformanceFetcher(
    Fetcher[FinvizPricePerformanceQueryParams, List[FinvizPricePerformanceData]]
):
    """Finviz Price Performance Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizPricePerformanceQueryParams:
        """Transform the query params."""
        return FinvizPricePerformanceQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizPricePerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Finviz."""

        screen = performance.Performance()
        screen.set_filter(ticker=query.symbol)
        try:
            screen_df = screen.screener_view(verbose=0)
            if screen_df is None:
                raise EmptyDataError()
            screen_df.columns = screen_df.columns.str.strip()  # type: ignore
            screen_df = screen_df.fillna("N/A").replace("N/A", None)  # type: ignore
        except Exception as e:
            raise e from e
        return screen_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: FinvizPricePerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizPricePerformanceData]:
        """Transform the raw data."""
        return [FinvizPricePerformanceData.model_validate(d) for d in data]
