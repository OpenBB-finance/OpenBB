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
        params: dict[str, Any],
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
        from openbb_yfinance.utils.helpers import get_custom_screener

        body = {
            "offset": 0,
            "size": 250,
            "sortField": "eodvolume",
            "sortType": "desc",
            "quoteType": "equity",
            "query": {
                "operator": "and",
                "operands": [
                    {"operator": "gt", "operands": ["intradaymarketcap", 500000000]},
                    {
                        "operator": "or",
                        "operands": [
                            {"operator": "eq", "operands": ["exchange", "NMS"]},
                            {"operator": "eq", "operands": ["exchange", "NYQ"]},
                        ],
                    },
                    {
                        "operator": "btwn",
                        "operands": ["peratio.lasttwelvemonths", 0, 20],
                    },
                    {"operator": "lt", "operands": ["pegratio_5y", 1]},
                    {"operator": "gte", "operands": ["epsgrowth.lasttwelvemonths", 25]},
                ],
            },
            "userId": "",
            "userIdType": "guid",
        }

        return await get_custom_screener(body=body, limit=query.limit)

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
