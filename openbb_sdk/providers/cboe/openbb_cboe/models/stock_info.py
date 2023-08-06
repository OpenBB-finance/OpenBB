"""CBOE Stock Info fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_info import StockInfoData, StockInfoQueryParams
from pydantic import Field, validator

from openbb_cboe.utils.helpers import get_info


class CboeStockInfoQueryParams(StockInfoQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """

class CboeStockInfoData(StockInfoData):
    """CBOE Company Search Data."""

    type: Optional[str] = Field(description="The type of asset.")
    tick: Optional[str] = Field(description="Whether the last sale was an up or down tick.")
    bid: Optional[float] = Field(description="The current bid price.")
    bid_size: Optional[float] = Field(description="The bid lot size.")
    ask: Optional[float] = Field(description="The current ask price.")
    ask_size: Optional[float] = Field(description="The ask lot size.")
    volume: Optional[float] = Field(description="The stock volume for the current trading day.")
    iv_thirty: Optional[float] = Field(description="The 30-day implied volatility of the stock.")
    iv_thirty_change: Optional[float] = Field(description="The change in 30-day implied volatility of the stock.")
    last_trade_timestamp: Optional[datetime] = Field(description="The last trade timestamp for the stock.")
    iv_thirty_one_year_high: Optional[float] = Field(description="The 1-year high of implied volatility.")
    hv_thirty_one_year_high: Optional[float] = Field(description="The 1-year high of realized volatility.")
    iv_thirty_one_year_low: Optional[float] = Field(description="The 1-year low of implied volatility.")
    hv_thirty_one_year_low: Optional[float] = Field(description="The 1-year low of realized volatility.")
    iv_sixty_one_year_high: Optional[float] = Field(description="The 60-day high of implied volatility.")
    hv_sixty_one_year_high: Optional[float] = Field(description="The 60-day high of realized volatility.")
    iv_sixty_one_year_low: Optional[float] = Field(description="The 60-day low of implied volatility.")
    hv_sixty_one_year_low: Optional[float] = Field(description="The 60-day low of realized volatility.")
    iv_ninety_one_year_high: Optional[float] = Field(description="The 90-day high of implied volatility.")
    hv_ninety_one_year_high: Optional[float] = Field(description="The 90-day high of realized volatility.")

    @validator("symbol", pre=True, check_fields=False)
    def name_validate(cls, v):  # pylint: disable=E0213
        return v.upper()


class CboeStockInfoFetcher(
    Fetcher[
        StockInfoQueryParams,
        List[StockInfoData],
        CboeStockInfoQueryParams,
        List[CboeStockInfoData],
    ]
):

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockInfoQueryParams:
        return CboeStockInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeStockInfoQueryParams,
        credentials: Optional[Dict[str,str]],
    ) -> List[CboeStockInfoData]:
        data = get_info(query.symbol).to_dict()
        return CboeStockInfoData.parse_obj(data)

    @staticmethod
    def transform_data(data: List[CboeStockInfoData]) -> List[StockInfoData]:
        return StockInfoData.parse_obj(data.dict())
