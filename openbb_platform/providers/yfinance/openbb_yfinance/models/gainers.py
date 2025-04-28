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
        from openbb_yfinance.utils.helpers import get_custom_screener

        body = {
            "offset": 0,
            "size": 250,
            "sortField": "percentchange",
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
                    {"operator": "gt", "operands": ["percentchange", 3]},
                    {"operator": "gt", "operands": ["intradayprice", 5]},
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
