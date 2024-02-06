"""Nasdaq Equity Search Model."""

import asyncio
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
        """Transform the query parameters."""
        return NasdaqEquitySearchQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    async def aextract_data(
        query: NasdaqEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Extract data from Nasdaq."""
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"

        def fetch_data():
            r = (
                nasdaq_session_companies.get(url, timeout=5)
                if query.use_cache is True
                else requests.get(url, timeout=5)
            )
            if r.status_code != 200:
                raise RuntimeError(f"Error with the request: {r.status_code}")
            return r.text

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fetch_data)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: NasdaqEquitySearchQueryParams,
        data: str,
        **kwargs: Any,
    ) -> List[NasdaqEquitySearchData]:
        """Transform the data and filter the results."""
        directory = read_csv(StringIO(data), sep="|").iloc[:-1]

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

        results = (
            directory.astype(object)
            .fillna("N/A")
            .replace("N/A", None)
            .to_dict(orient="records")
        )

        return [NasdaqEquitySearchData.model_validate(d) for d in results]
