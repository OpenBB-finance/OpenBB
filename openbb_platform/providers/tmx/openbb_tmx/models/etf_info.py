"""TMX ETF Info fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from openbb_tmx.utils.helpers import get_all_etfs
from pydantic import Field


class TmxEtfInfoQueryParams(EtfInfoQueryParams):
    """TMX ETF Info Query Params"""


class TmxEtfInfoData(EtfInfoData):
    """TMX ETF Info Data."""

    issuer: Optional[str] = Field(
        description="The issuer of the ETF.", alias="fund_family", default=None
    )
    investment_style: Optional[str] = Field(
        description="The investment style of the ETF.", default=None
    )
    esg: Optional[bool] = Field(
        description="Whether the ETF qualifies as an ESG fund.", default=None
    )
    currency: Optional[str] = Field(description="The currency of the ETF.")
    unit_price: Optional[float] = Field(
        description="The unit price of the ETF.", default=None
    )
    close: Optional[float] = Field(description="The closing price of the ETF.")
    prev_close: Optional[float] = Field(
        description="The previous closing price of the ETF.", default=None
    )
    return_1m: Optional[float] = Field(
        description="The one-month return of the ETF.", default=None
    )
    return_3m: Optional[float] = Field(
        description="The three-month return of the ETF.", default=None
    )
    return_6m: Optional[float] = Field(
        description="The six-month return of the ETF.", default=None
    )
    return_ytd: Optional[float] = Field(
        description="The year-to-date return of the ETF.", default=None
    )
    return_1y: Optional[float] = Field(
        description="The one-year return of the ETF.", default=None
    )
    avg_volume: Optional[int] = Field(
        description="The average daily volume of the ETF.",
        alias="volume_avg_daily",
        default=None,
    )
    avg_volume_30d: Optional[int] = Field(
        description="The 30-day average volume of the ETF.",
        alias="volume_avg_30d",
        default=None,
    )
    aum: Optional[float] = Field(description="The AUM of the ETF.", default=None)
    pe_ratio: Optional[float] = Field(
        description="The price-to-earnings ratio of the ETF.", default=None
    )
    pb_ratio: Optional[float] = Field(
        description="The price-to-book ratio of the ETF.", default=None
    )
    management_fee: Optional[float] = Field(
        description="The management fee of the ETF.", default=None
    )
    mer: Optional[float] = Field(
        description="The management expense ratio of the ETF.", default=None
    )
    distribution_yield: Optional[float] = Field(
        description="The distribution yield of the ETF.", default=None
    )
    dividend_frequency: Optional[str] = Field(
        description="The dividend payment frequency of the ETF.", default=None
    )
    sectors: Optional[List[Dict]] = Field(
        description="The sector weightings of the ETF holdings.", default=None
    )
    regions: Optional[List[Dict]] = Field(
        description="The region weightings of the ETF holdings.", default=None
    )
    holdings_top10: Optional[List[Dict]] = Field(
        description="The top 10 holdings of the ETF.", default=None
    )
    website: Optional[str] = Field(description="The website of the ETF.", default=None)
    description: Optional[str] = Field(
        description="The description of the ETF.",
        alias="investment_objectives",
        default=None,
    )


class TmxEtfInfoFetcher(
    Fetcher[
        TmxEtfInfoQueryParams,
        List[TmxEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfInfoQueryParams:
        """Transform the query."""
        return TmxEtfInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )

        COLUMNS = [
            "symbol",
            "inception_date",
            "name",
            "fund_family",
            "investment_style",
            "esg",
            "currency",
            "unit_price",
            "close",
            "prev_close",
            "return_1m",
            "return_3m",
            "return_6m",
            "return_ytd",
            "return_1y",
            "volume_avg_daily",
            "volume_avg_30d",
            "aum",
            "pe_ratio",
            "pb_ratio",
            "management_fee",
            "mer",
            "distribution_yield",
            "dividend_frequency",
            "sectors",
            "regions",
            "holdings_top10",
            "website",
            "investment_objectives",
        ]

        _data = get_all_etfs()
        results = {}

        for symbol in symbols:
            if ".TO" in symbol:
                symbol = symbol.replace(".TO", "")  # noqa
            _target = _data[_data["symbol"] == symbol][COLUMNS].transpose()
            _target.columns = _target.loc["symbol"]
            if len(_target) > 0:
                target = _target.to_dict()
                results.update({symbol: target[symbol]})
        return pd.DataFrame(results).transpose().to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[TmxEtfInfoData]:
        """Return the transformed data."""
        return [TmxEtfInfoData.model_validate(d) for d in data]
