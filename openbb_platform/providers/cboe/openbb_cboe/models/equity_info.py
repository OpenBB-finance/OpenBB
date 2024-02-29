"""CBOE Equity Info Model."""

import concurrent.futures
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_cboe.utils.helpers import (
    get_cboe_directory,
    get_cboe_index_directory,
    get_ticker_info,
    get_ticker_iv,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field


class CboeEquityInfoQueryParams(EquityInfoQueryParams):
    """CBOE Equity Info Query.

    Source: https://www.cboe.com/
    """


class CboeEquityInfoData(EquityInfoData):
    """CBOE Equity Info Data."""

    type: Optional[str] = Field(default=None, description="Type of asset.")
    exchange_id: Optional[int] = Field(
        default=None, description="The Exchange ID number."
    )
    tick: Optional[str] = Field(
        default=None, description="Whether the last sale was an up or down tick."
    )
    bid: Optional[float] = Field(default=None, description="Current bid price.")
    bid_size: Optional[float] = Field(default=None, description="Bid lot size.")
    ask: Optional[float] = Field(default=None, description="Current ask price.")
    ask_size: Optional[float] = Field(default=None, description="Ask lot size.")
    volume: Optional[float] = Field(
        default=None, description="Stock volume for the current trading day."
    )
    iv30: Optional[float] = Field(
        default=None, description="The 30-day implied volatility of the stock."
    )
    iv30_change: Optional[float] = Field(
        default=None, description="Change in 30-day implied volatility of the stock."
    )
    last_trade_timestamp: Optional[datetime] = Field(
        default=None, description="Last trade timestamp for the stock."
    )
    iv30_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of implied volatility."
    )
    hv30_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of realized volatility."
    )
    iv30_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of implied volatility."
    )
    hv30_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of realized volatility."
    )
    iv60_annual_high: Optional[float] = Field(
        default=None, description="The 60-day high of implied volatility."
    )
    hv60_annual_high: Optional[float] = Field(
        default=None, description="The 60-day high of realized volatility."
    )
    iv60_annual_low: Optional[float] = Field(
        default=None, description="The 60-day low of implied volatility."
    )
    hv60_annual_low: Optional[float] = Field(
        default=None, description="The 60-day low of realized volatility."
    )
    iv90_annual_high: Optional[float] = Field(
        default=None, description="The 90-day high of implied volatility."
    )
    hv90_annual_high: Optional[float] = Field(
        default=None, description="The 90-day high of realized volatility."
    )


class CboeEquityInfoFetcher(
    Fetcher[
        CboeEquityInfoQueryParams,
        List[CboeEquityInfoData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEquityInfoQueryParams:
        """Transform the query."""
        return CboeEquityInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeEquityInfoQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        results = []

        INDEXES = get_cboe_index_directory().index.to_list()
        SYMBOLS = get_cboe_directory()

        def get_one(symbol):
            data = pd.Series(dtype="object")
            if symbol in SYMBOLS.index or symbol in INDEXES:
                _info = pd.Series(get_ticker_info(symbol))
                _iv = pd.Series(get_ticker_iv(symbol))
                data = (
                    pd.DataFrame(pd.concat([_info, _iv]))
                    .transpose()
                    .drop(columns="seqno")
                    .iloc[0]
                )

                results.append(data.to_dict())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, query.symbol.split(","))

        return (
            pd.DataFrame.from_records(results)
            .sort_values(by="symbol")
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        query: CboeEquityInfoQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeEquityInfoData]:
        """Transform the data to the standard format."""
        return [CboeEquityInfoData.model_validate(d) for d in data]
