"""Yahoo Finance Asset Performance Active Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceQueryParams,
)
from openbb_yfinance.utils.references import YFPredefinedScreenerData
from pydantic import Field


class YFActiveQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Most Active Query.

    Source: https://finance.yahoo.com/screener/predefined/most_actives
    """

    limit: Optional[int] = Field(
        default=200,
        description="Limit the number of results.",
    )


class YFActiveData(YFPredefinedScreenerData):
    """Yahoo Finance Most Active Data."""


class YFActiveFetcher(Fetcher[YFActiveQueryParams, list[YFActiveData]]):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFActiveQueryParams:
        """Transform query params."""
        return YFActiveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFActiveQueryParams,
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
                    {"operator": "gt", "operands": ["intradaymarketcap", 2000000000]},
                    {
                        "operator": "or",
                        "operands": [
                            {"operator": "eq", "operands": ["exchange", "NMS"]},
                            {"operator": "eq", "operands": ["exchange", "NYQ"]},
                        ],
                    },
                    {"operator": "gt", "operands": ["davolume", 1000000]},
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
    ) -> list[YFActiveData]:
        """Transform data."""
        return [
            YFActiveData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: x["regularMarketVolume"],
                reverse=query.sort == "desc",
            )
        ]
