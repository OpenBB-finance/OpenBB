"""Intrinio ETF Performance Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_intrinio.utils.references import ETF_PERFORMANCE_MAP
from pydantic import Field


class IntrinioEtfPricePerformanceQueryParams(RecentPerformanceQueryParams):
    """
    Intrinio ETF Performance Query Params.

    Source: https://docs.intrinio.com/documentation/web_api/get_etf_stats_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_etf_analytics_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    return_type: Literal["trailing", "calendar"] = Field(
        default="trailing",
        description="The type of returns to return, a trailing or calendar window.",
    )
    adjustment: Literal["splits_only", "splits_and_dividends"] = Field(
        default="splits_and_dividends",
        description="The adjustment factor, 'splits_only' will return pure price performance.",
    )


class IntrinioEtfPricePerformanceData(RecentPerformanceData):
    """Intrinio ETF Performance Data."""

    __alias_dict__ = {
        "updated": "date",
        "year_high": "fifty_two_week_high",
        "year_low": "fifty_two_week_low",
        "volume": "volume_traded",
        "volume_avg_30": "average_daily_volume_one_month",
        "volume_avg_90": "average_daily_volume_three_month",
        "volume_avg_180": "average_daily_volume_six_month",
    }

    max_annualized: Optional[float] = Field(
        default=None,
        description="Annualized rate of return from inception.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volatility_one_year: Optional[float] = Field(
        default=None,
        description="Trailing one-year annualized volatility.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volatility_three_year: Optional[float] = Field(
        default=None,
        description="Trailing three-year annualized volatility.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volatility_five_year: Optional[float] = Field(
        default=None,
        description="Trailing five-year annualized volatility.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[int] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    volume_avg_30: Optional[float] = Field(
        default=None,
        description="The one-month average daily volume.",
    )
    volume_avg_90: Optional[float] = Field(
        default=None,
        description="The three-month average daily volume.",
    )
    volume_avg_180: Optional[float] = Field(
        default=None,
        description="The six-month average daily volume.",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Beta compared to the S&P 500.",
    )
    nav: Optional[float] = Field(
        default=None,
        description="Net asset value per share.",
    )
    year_high: Optional[float] = Field(
        default=None,
        description="The 52-week high price.",
    )
    year_low: Optional[float] = Field(
        default=None,
        description="The 52-week low price.",
    )

    market_cap: Optional[float] = Field(
        default=None,
        description="The market capitalization.",
    )
    shares_outstanding: Optional[int] = Field(
        default=None,
        description="The number of shares outstanding.",
    )
    updated: Optional[dateType] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )


class IntrinioEtfPricePerformanceFetcher(
    Fetcher[
        IntrinioEtfPricePerformanceQueryParams, List[IntrinioEtfPricePerformanceData]
    ]
):
    """Intrinio ETF Performance Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioEtfPricePerformanceQueryParams:
        """Transform query."""
        return IntrinioEtfPricePerformanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEtfPricePerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com/etfs/"
        symbols = query.symbol.split(",")
        symbols = [
            symbol + ":US" if ":" not in symbol else symbol for symbol in symbols
        ]

        adjustment = (
            "split_only"
            if query.adjustment == "splits_and_dividends"
            else "split_and_dividend"
        )

        return_type = "trailing" if query.return_type == "calendar" else "calendar"

        results = []

        async def get_one(symbol: str, **kwargs):
            """Get data for one symbol."""

            url = f"{base_url}{symbol}/stats?api_key={api_key}"
            result = await amake_request(url, **kwargs)

            if "message" in result and result["message"] != []:  # type: ignore
                warn(f"Symbol Error: {symbol} - {result['message']}")  # type: ignore
                return
            _ = result.pop("message", None)  # type: ignore
            _ = result.pop("messages", None)  # type: ignore

            data = {}
            etf = result.pop("etf", {})  # type: ignore
            data["symbol"] = etf.get("ticker")
            # These items will be kept regardless of the adjustment and return_type.
            keep = ["volatility", "month", "year_to_date"]
            for k, v in result.copy().items():  # type: ignore
                if not any(substring in k for substring in keep):
                    _ = result.pop(k, None) if adjustment in k else None  # type: ignore
                    _ = result.pop(k, None) if return_type in k else None  # type: ignore
                if k in result:
                    data[ETF_PERFORMANCE_MAP.get(k, k)] = v
            # Get an additional set of data to combine with the first set.
            analytics_url = (
                f"https://api-v2.intrinio.com/etfs/{symbol}/analytics?api_key={api_key}"
            )
            if data:
                analytics = await amake_request(analytics_url, **kwargs)
                if "messages" in analytics and analytics["messages"] != []:  # type: ignore
                    warn(
                        f"Symbol Error: {analytics['messages']}"  # type: ignore
                        + f"for {etf.get('ticker')}"  # type: ignore
                    )
                    return
                # Remove the duplicate data from the analytics response.
                _ = analytics.pop("messages", None)  # type: ignore
                _ = analytics.pop("etf", None)  # type: ignore
                _ = analytics.pop("date", None)  # type: ignore

                data.update(analytics)  # type: ignore

            results.append(data)

        tasks = [get_one(symbol, **kwargs) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError("No data was returned.")

        # Undo any formatting changes made to the symbols before sorting.
        symbols = query.symbol.replace(":US", "").split(",")

        return sorted(
            results,
            key=(lambda item: (symbols.index(item.get("symbol", len(symbols))))),
        )

    @staticmethod
    def transform_data(
        query: IntrinioEtfPricePerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioEtfPricePerformanceData]:
        """Transform data."""
        return [IntrinioEtfPricePerformanceData.model_validate(d) for d in data]
