"""Yahoo Finance Top Gainers Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceQueryParams,
)
from openbb_yfinance.utils.references import YFPredefinedScreenerData
from pydantic import Field


class YFGainersQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Gainers Query.

    Source: https://finance.yahoo.com/screener/predefined/day_gainers
    """

    limit: Optional[int] = Field(
        default=200,
        description="Limit the number of results.",
    )


class YFGainersData(YFPredefinedScreenerData):
    """Yahoo Finance Gainers Data."""


class YFGainersFetcher(Fetcher[YFGainersQueryParams, list[YFGainersData]]):
    """Yahoo Finance Gainers Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFGainersQueryParams:
        """Transform query params."""
        return YFGainersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFGainersQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Get data from YF."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_defined_screener

        return await get_defined_screener(name="day_gainers", limit=query.limit)

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFGainersData]:
        """Transform data."""
        return [
            YFGainersData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: x["regularMarketChangePercent"],
                reverse=query.sort == "desc",
            )
        ]
