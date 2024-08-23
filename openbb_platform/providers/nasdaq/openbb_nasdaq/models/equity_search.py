"""Nasdaq Equity Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class NasdaqEquitySearchQueryParams(EquitySearchQueryParams):
    """Nasdaq Equity Search Query.

    Source: https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt
    """

    is_etf: Union[bool, None] = Field(
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
    """Nasdaq Equity Search Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqEquitySearchQueryParams:
        """Transform the query parameters."""
        return NasdaqEquitySearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Extract data from Nasdaq."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"
        response = make_request(url)
        if response.status_code != 200:
            raise OpenBBError(
                f"Failed to fetch data from Nasdaq: {response.status_code}"
            )
        return response.text

    @staticmethod
    def transform_data(
        query: NasdaqEquitySearchQueryParams,
        data: str,
        **kwargs: Any,
    ) -> List[NasdaqEquitySearchData]:
        """Transform the data and filter the results."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from pandas import read_csv  # noqa

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
