"""YFinance Equity Profile Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, field_validator
from yfinance import Ticker

_warn = warnings.warn


class YFinanceEquityProfileQueryParams(EquityInfoQueryParams):
    """YFinance Equity Profile Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinanceEquityProfileData(EquityInfoData):
    """YFinance Equity Profile Data."""

    __alias_dict__ = {
        "name": "longName",
        "issue_type": "quoteType",
        "stock_exchange": "exchange",
        "first_stock_price_date": "firstTradeDateEpochUtc",
        "exchange_timezone": "timeZoneFullName",
        "industry_category": "industry",
        "hq_country": "country",
        "hq_address1": "address1",
        "hq_address_city": "city",
        "hq_address_postal_code": "zip",
        "hq_state": "state",
        "business_phone_no": "phone",
        "company_url": "website",
        "long_description": "longBusinessSummary",
        "employees": "fullTimeEmployees",
        "market_cap": "marketCap",
        "dividend_yield": "dividendYield",
    }

    exchange_timezone: Optional[str] = Field(
        description="The timezone of the exchange.",
        default=None,
        alias="timeZoneFullName",
    )
    issue_type: Optional[str] = Field(
        description="The issuance type of the asset.", default=None, alias="issueType"
    )
    currency: Optional[str] = Field(
        description="The currency in which the asset is traded.", default=None
    )
    market_cap: Optional[int] = Field(
        description="The market capitalization of the asset.",
        default=None,
    )
    shares_outstanding: Optional[int] = Field(
        description="The number of listed shares outstanding.",
        default=None,
        alias="sharesOutstanding",
    )
    shares_float: Optional[int] = Field(
        description="The number of shares in the public float.",
        default=None,
        alias="floatShares",
    )
    shares_implied_outstanding: Optional[int] = Field(
        description=(
            "Implied shares outstanding of common equity"
            "assuming the conversion of all convertible subsidiary equity into common."
        ),
        default=None,
        alias="impliedSharesOutstanding",
    )
    shares_short: Optional[int] = Field(
        description="The reported number of shares short.",
        default=None,
        alias="sharesShort",
    )
    dividend_yield: Optional[float] = Field(
        description="The dividend yield of the asset, as a normalized percent.",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="yield",
    )
    beta: Optional[float] = Field(
        description="The beta of the asset relative to the broad market.",
        default=None,
    )

    @field_validator("first_stock_price_date", mode="before", check_fields=False)
    @classmethod
    def validate_first_trade_date(cls, v):
        """Validate first stock price date."""
        return datetime.utcfromtimestamp(v).date() if v else None


class YFinanceEquityProfileFetcher(
    Fetcher[YFinanceEquityProfileQueryParams, List[YFinanceEquityProfileData]]
):
    """YFinance Equity Profile fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEquityProfileQueryParams:
        """Transform the query."""
        return YFinanceEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "longName",
            "exchange",
            "timeZoneFullName",
            "quoteType",
            "firstTradeDateEpochUtc",
            "currency",
            "sharesOutstanding",
            "floatShares",
            "impliedSharesOutstanding",
            "sharesShort",
            "sector",
            "industry",
            "address1",
            "city",
            "state",
            "zip",
            "country",
            "phone",
            "website",
            "fullTimeEmployees",
            "longBusinessSummary",
            "marketCap",
            "yield",
            "dividendYield",
            "beta",
        ]

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result = {}
            ticker = {}
            try:
                ticker = Ticker(symbol).get_info()
            except Exception as e:
                _warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEquityProfileData]:
        """Transform the data."""
        return [YFinanceEquityProfileData.model_validate(d) for d in data]
