"""TMX ETF Holdings fetcher."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_tmx.utils.helpers import get_all_etfs
from pydantic import Field


class TmxEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """TMX ETF Holdings query.

    Source: https://www.tmx.com/
    """


class TmxEtfHoldingsData(EtfHoldingsData):
    """TMX ETF Holdings Data."""

    symbol: Optional[str] = Field(
        description="The ticker symbol of the asset.", default=None
    )
    name: Optional[str] = Field(description="The name of the asset.", default=None)
    weight: Optional[float] = Field(
        description="The weight of the asset in the portfolio.", default=None
    )
    shares: Optional[Union[int, str]] = Field(
        description="The value of the assets under management.",
        alias="number_of_shares",
        default=None,
    )
    market_value: Optional[Union[float, str]] = Field(
        description="The market value of the holding.", default=None
    )
    currency: Optional[str] = Field(description="The currency of the holding.")
    share_percentage: Optional[float] = Field(
        description="The share percentage of the holding.", default=None
    )
    share_change: Optional[Union[float, str]] = Field(
        description="The change in shares of the holding.", default=None
    )
    country: Optional[str] = Field(
        description="The country of the holding.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange code of the holding.", default=None
    )
    type_id: Optional[str] = Field(
        description="The holding type ID of the asset.", default=None
    )
    fund_id: Optional[str] = Field(
        description="The fund ID of the asset.", default=None
    )


class TmxEtfHoldingsFetcher(
    Fetcher[
        TmxEtfHoldingsQueryParams,
        List[TmxEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfHoldingsQueryParams:
        """Transform the query."""
        return TmxEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        query.symbol = query.symbol.upper()
        if ".TO" in query.symbol:
            query.symbol = query.symbol.replace(".TO", "")
        results = []
        etf = pd.DataFrame()
        etfs = get_all_etfs()
        etf = etfs[etfs["symbol"] == query.symbol]

        if len(etf) == 1:
            top_holdings = pd.DataFrame(etf["holdings_top10"].iloc[0])
            _columns = {
                "numberofshares": "number_of_shares",
                "symbol": "symbol",
                "country": "country",
                "fundid": "fund_id",
                "excode": "exchange",
                "securityname": "name",
                "currency": "currency",
                "marketvalue": "market_value",
                "detailholdingtypeid": "type_id",
                "weighting": "weight",
                "sharepercentage": "share_percentage",
                "sharechange": "share_change",
                "shareChange": "share_change",
            }
            top_holdings.rename(columns=_columns, inplace=True)
            top_holdings["market_value"] = top_holdings["market_value"]
            top_holdings["share_change"] = top_holdings["share_change"]
            results = top_holdings.replace("NA", "").to_dict("records")

        return results

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxEtfHoldingsData]:
        """Transform the data to the standard format."""
        return [TmxEtfHoldingsData.model_validate(d) for d in data]
