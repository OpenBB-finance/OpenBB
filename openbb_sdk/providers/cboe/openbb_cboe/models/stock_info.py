"""CBOE Stock Info fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_info import (
    StockInfoData,
    StockInfoQueryParams,
)
from pydantic import Field

from openbb_cboe.utils.helpers import get_info


class CboeStockInfoQueryParams(StockInfoQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """


class CboeStockInfoData(StockInfoData):
    """CBOE Company Search Data."""

    type: Optional[str] = Field(description="Type of asset.")
    tick: Optional[str] = Field(
        description="Whether the last sale was an up or down tick."
    )
    bid: Optional[float] = Field(description="Current bid price.")
    bid_size: Optional[float] = Field(description="Bid lot size.")
    ask: Optional[float] = Field(description="Current ask price.")
    ask_size: Optional[float] = Field(description="Ask lot size.")
    volume: Optional[float] = Field(
        description="Stock volume for the current trading day."
    )
    iv_thirty: Optional[float] = Field(
        description="The 30-day implied volatility of the stock."
    )
    iv_thirty_change: Optional[float] = Field(
        description="Change in 30-day implied volatility of the stock."
    )
    last_trade_timestamp: Optional[datetime] = Field(
        description="Last trade timestamp for the stock."
    )
    iv_thirty_one_year_high: Optional[float] = Field(
        description="The 1-year high of implied volatility."
    )
    hv_thirty_one_year_high: Optional[float] = Field(
        description="The 1-year high of realized volatility."
    )
    iv_thirty_one_year_low: Optional[float] = Field(
        description="The 1-year low of implied volatility."
    )
    hv_thirty_one_year_low: Optional[float] = Field(
        description="The 1-year low of realized volatility."
    )
    iv_sixty_one_year_high: Optional[float] = Field(
        description="The 60-day high of implied volatility."
    )
    hv_sixty_one_year_high: Optional[float] = Field(
        description="The 60-day high of realized volatility."
    )
    iv_sixty_one_year_low: Optional[float] = Field(
        description="The 60-day low of implied volatility."
    )
    hv_sixty_one_year_low: Optional[float] = Field(
        description="The 60-day low of realized volatility."
    )
    iv_ninety_one_year_high: Optional[float] = Field(
        description="The 90-day high of implied volatility."
    )
    hv_ninety_one_year_high: Optional[float] = Field(
        description="The 90-day high of realized volatility."
    )


class CboeStockInfoFetcher(
    Fetcher[
        CboeStockInfoQueryParams,
        List[CboeStockInfoData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockInfoQueryParams:
        """Transform the query"""
        return CboeStockInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeStockInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the CBOE endpoint"""
        return get_info(query.symbol).to_dict()

    @staticmethod
    def transform_data(data: dict) -> List[CboeStockInfoData]:
        """Transform the data to the standard format"""
        return [CboeStockInfoData.parse_obj(data)]
