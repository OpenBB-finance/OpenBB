"""Yahoo Finance Asset Undervalued Growth Tech Equities Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceQueryParams,
)
from openbb_yfinance.utils.references import YFPredefinedScreenerData
from pydantic import Field


class YFUndervaluedGrowthEquitiesQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Undervalued Growth Stocks Query.

    Source: https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks
    """

    limit: Optional[int] = Field(
        default=200,
        description="Limit the number of results.",
    )


class YFUndervaluedGrowthEquitiesData(YFPredefinedScreenerData):
    """Yahoo Finance Undervalued Growth Stocks Data."""


class YFUndervaluedGrowthEquitiesFetcher(
    Fetcher[
        YFUndervaluedGrowthEquitiesQueryParams, list[YFUndervaluedGrowthEquitiesData]
    ]
):
    """Yahoo Finance Undervalued Growth Stocks Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any]
    ) -> YFUndervaluedGrowthEquitiesQueryParams:
        """Transform query params."""
        return YFUndervaluedGrowthEquitiesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFUndervaluedGrowthEquitiesQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Get data from YF."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_defined_screener

        return await get_defined_screener(
            name="undervalued_growth_stocks", limit=query.limit
        )

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFUndervaluedGrowthEquitiesData]:
        """Transform data."""
        return [
            YFUndervaluedGrowthEquitiesData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: x["regularMarketChangePercent"],
                reverse=query.sort == "desc",
            )
        ]
