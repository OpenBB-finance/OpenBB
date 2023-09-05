"""TMX ETF Holdings fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.helpers import get_all_etfs


class TmxEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """TMX ETF Holdings query.

    Source: https://www.tmx.com/
    """


class TmxEtfHoldingsData(EtfHoldingsData):
    """TMX ETF Holdings Data."""

    symbol: Optional[str | None] = Field(description="The ticker symbol of the asset.")
    name: Optional[str | None] = Field(description="The name of the asset.")
    weight: Optional[float | None] = Field(
        description="The weight of the asset in the portfolio."
    )
    shares: Optional[int | str | None] = Field(
        description="The value of the assets under management.",
        alias="number_of_shares",
    )
    market_value: Optional[float | None] = Field(
        description="The market value of the holding."
    )
    currency: Optional[str | None] = Field(description="The currency of the holding.")
    share_percentage: Optional[float | None] = Field(
        description="The share percentage of the holding."
    )
    share_change: Optional[float | str | None] = Field(
        description="The change in shares of the holding.",
    )
    country: Optional[str | None] = Field(description="The country of the holding.")
    exchange: Optional[str | None] = Field(
        description="The exchange code of the holding."
    )
    type_id: Optional[str | None] = Field(
        description="The holding type ID of the asset."
    )
    fund_id: Optional[str | None] = Field(description="The fund ID of the asset.")


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
        results = {}
        etf = pd.DataFrame()
        etfs = get_all_etfs()
        etf = etfs[etfs["symbol"] == query.symbol.upper()]

        if len(etf) == 1:
            top_holdings = pd.DataFrame(etf["holdings_top_10"].iloc[0])
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
            results = top_holdings.to_dict("records")

        return results

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxEtfHoldingsData]:
        """Transform the data to the standard format."""
        return [TmxEtfHoldingsData.parse_obj(d) for d in data]
