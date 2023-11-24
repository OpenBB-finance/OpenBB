"""Nasdaq Equity Search Model."""

from datetime import timedelta
from io import StringIO
from typing import Any, Dict, List, Optional

import requests
import requests_cache
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pandas import read_csv
from pydantic import Field

cache_dir = get_user_cache_directory()

nasdaq_session_companies = requests_cache.CachedSession(
    f"{cache_dir}/http/nasdaq_companies", expire_after=timedelta(days=1)
)


class NasdaqEquitySearchQueryParams(EquitySearchQueryParams):
    """Nasdaq Equity Search Query.

    Source: https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt
    """

    is_etf: Optional[bool] = Field(
        default=None,
        description="If True, returns ETFs.",
    )
    use_cache: Optional[bool] = Field(
        default=True,
        description="If True, caches the symbol directory for one day.",
    )


class NasdaqEquitySearchData(EquitySearchData):
    """Nasdaq Equity Search Data."""

    __alias_dict__ = {
        "symbol": "Symbol",
        "name": "Security Name",
        "nasdaq_traded": "Nasdaq Traded",
        "exchange": "Listing Exchange",
        "market_category": "Market Category",
        "etf": "ETF",
        "round_lot_size": "Round Lot Size",
        "test_issue": "Test Issue",
        "financial_status": "Financial Status",
        "cqs_symbol": "CQS Symbol",
        "nasdaq_symbol": "NASDAQ Symbol",
        "next_shares": "NextShares",
    }

    nasdaq_traded: Optional[str] = Field(
        default=None,
        description="Is Nasdaq traded?",
    )
    exchange: Optional[str] = Field(
        default=None,
        description="Primary Exchange",
    )
    market_category: Optional[str] = Field(
        default=None,
        description="Market Category",
    )
    etf: Optional[str] = Field(
        default=None,
        description="Is ETF?",
    )
    round_lot_size: Optional[float] = Field(
        default=None,
        description="Round Lot Size",
    )
    test_issue: Optional[str] = Field(
        default=None,
        description="Is test Issue?",
    )
    financial_status: Optional[str] = Field(
        default=None,
        description="Financial Status",
    )
    cqs_symbol: Optional[str] = Field(
        default=None,
        description="CQS Symbol",
    )
    nasdaq_symbol: Optional[str] = Field(
        default=None,
        description="NASDAQ Symbol",
    )
    next_shares: Optional[str] = Field(
        default=None,
        description="Is NextShares?",
    )


class NasdaqEquitySearchFetcher(
    Fetcher[NasdaqEquitySearchQueryParams, List[NasdaqEquitySearchData]]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqEquitySearchQueryParams:
        return NasdaqEquitySearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"

        r = (
            nasdaq_session_companies.get(url, timeout=5)
            if query.use_cache is True
            else requests.get(url, timeout=5)
        )
        if r.status_code != 200:
            raise RuntimeError(f"Error with the request: {r.status_code}")

        directory = read_csv(StringIO(r.text), sep="|").iloc[:-1]

        if query.is_etf is True:
            directory = directory[directory["ETF"] == "Y"]
        if query.is_etf is False:
            directory = directory[directory["ETF"] == "N"]

        if query.query:
            directory = directory[
                directory["Symbol"].str.contains(query.query, case=False)
                | directory["Security Name"].str.contains(query.query, case=False)
                | directory["CQS Symbol"].str.contains(query.query, case=False)
                | directory["NASDAQ Symbol"].str.contains(query.query, case=False)
            ]
        directory["Market Category"] = directory["Market Category"].replace(" ", None)

        return (
            directory.astype(object)
            .fillna("-")
            .replace("-", None)
            .to_dict(orient="records")
        )

    @staticmethod
    def transform_data(
        query: NasdaqEquitySearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqEquitySearchData]:
        return [NasdaqEquitySearchData.model_validate(d) for d in data]
