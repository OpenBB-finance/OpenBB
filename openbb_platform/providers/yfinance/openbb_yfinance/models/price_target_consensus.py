"""YFinance Price Target Consensus Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from pydantic import Field
from yfinance import Ticker

_warn = warnings.warn


class YFinancePriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """YFinance Price Target Consensus Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinancePriceTargetConsensusData(PriceTargetConsensusData):
    """YFinance Price Target Consensus Data."""

    __alias_dict__ = {
        "target_high": "targetHighPrice",
        "target_low": "targetLowPrice",
        "target_consensus": "targetMeanPrice",
        "target_median": "targetMedianPrice",
        "recommendation": "recommendationKey",
        "recommendation_mean": "recommendationMean",
        "number_of_analysts": "numberOfAnalystOpinions",
        "current_price": "currentPrice",
    }

    recommendation: Optional[str] = Field(
        default=None,
        description="Recommendation - buy, sell, etc.",
    )
    recommendation_mean: Optional[float] = Field(
        default=None,
        description="Mean recommendation score where 1 is strong buy and 5 is strong sell.",
    )
    number_of_analysts: Optional[int] = Field(
        default=None, description="Number of analysts providing opinions."
    )
    current_price: Optional[float] = Field(
        default=None,
        description="Current price of the stock.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency the stock is priced in.",
    )


class YFinancePriceTargetConsensusFetcher(
    Fetcher[
        YFinancePriceTargetConsensusQueryParams, List[YFinancePriceTargetConsensusData]
    ]
):
    """YFinance Price Target Consensus Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFinancePriceTargetConsensusQueryParams:
        """Transform the query."""
        return YFinancePriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinancePriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "currentPrice",
            "currency",
            "targetHighPrice",
            "targetLowPrice",
            "targetMeanPrice",
            "targetMedianPrice",
            "recommendationMean",
            "recommendationKey",
            "numberOfAnalystOpinions",
        ]

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result = {}
            ticker = {}
            try:
                ticker = Ticker(symbol).get_info()
            except Exception as e:
                _warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("numberOfAnalystOpinions") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinancePriceTargetConsensusQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinancePriceTargetConsensusData]:
        """Transform the data."""
        return [YFinancePriceTargetConsensusData.model_validate(d) for d in data]
