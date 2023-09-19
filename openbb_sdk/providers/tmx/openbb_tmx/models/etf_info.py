"""TMX ETF Info fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.helpers import get_all_etfs


class TmxEtfInfoQueryParams(EtfInfoQueryParams):
    """TMX ETF Info Query Params"""


class TmxEtfInfoData(EtfInfoData):
    """TMX ETF Info Data."""

    issuer: Optional[str] = Field(
        description="The issuer of the ETF.", alias="fund_family"
    )
    investment_style: Optional[str] = Field(
        description="The investment style of the ETF.",
    )
    esg: Optional[str] = Field(
        description="Whether the ETF qualifies as an ESG fund.",
    )
    currency: Optional[str] = Field(description="The currency of the ETF.")
    unit_price: Optional[float] = Field(
        description="The unit price of the ETF.",
    )
    close: Optional[float] = Field(description="The closing price of the ETF.")
    prev_close: Optional[float] = Field(
        description="The previous closing price of the ETF."
    )
    return_1m: Optional[float] = Field(description="The one-month return of the ETF.")
    return_3m: Optional[float] = Field(description="The three-month return of the ETF.")
    return_6m: Optional[float] = Field(description="The six-month return of the ETF.")
    return_ytd: Optional[float] = Field(
        description="The year-to-date return of the ETF."
    )
    return_1y: Optional[float] = Field(description="The one-year return of the ETF.")
    avg_volume: Optional[int] = Field(
        description="The average daily volume of the ETF.", alias="volume_avg_daily"
    )
    avg_volume_30d: Optional[int] = Field(
        description="The 30-day average volume of the ETF.", alias="volume_avg_30d"
    )
    aum: Optional[float] = Field(description="The AUM of the ETF.")
    pe_ratio: Optional[float] = Field(
        description="The price-to-earnings ratio of the ETF."
    )
    pb_ratio: Optional[float] = Field(description="The price-to-book ratio of the ETF.")
    management_fee: Optional[float] = Field(
        description="The management fee of the ETF."
    )
    mer: Optional[float] = Field(description="The management expense ratio of the ETF.")
    distribution_yield: Optional[float] = Field(
        description="The distribution yield of the ETF."
    )
    dividend_frequency: Optional[str] = Field(
        description="The dividend payment frequency of the ETF."
    )
    sectors: Optional[List[Dict]] = Field(
        description="The sector weightings of the ETF holdings."
    )
    regions: Optional[List[Dict]] = Field(
        description="The region weightings of the ETF holdings."
    )
    holdings_top10: Optional[List[Dict]] = Field(
        description="The top 10 holdings of the ETF."
    )
    website: Optional[str] = Field(description="The website of the ETF.")
    description: Optional[str] = Field(
        description="The description of the ETF.", alias="investment_objectives"
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
    def transform_data(data: List[Dict]) -> List[TmxEtfInfoData]:
        """Return the transformed data."""
        return [TmxEtfInfoData(**d) for d in data]
