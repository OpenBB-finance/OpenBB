"""YFinance ETF Info Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field, field_validator
from yfinance import Ticker

_warn = warnings.warn


class YFinanceEtfInfoQueryParams(EtfInfoQueryParams):
    """YFinance ETF Info Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinanceEtfInfoData(EtfInfoData):
    """YFinance ETF Info Data."""

    __alias_dict__ = {
        "name": "longName",
        "inception_date": "fundInceptionDate",
        "description": "longBusinessSummary",
    }

    fund_type: Optional[str] = Field(
        default=None,
        description="The legal type of fund.",
        alias="legalType",
    )
    fund_family: Optional[str] = Field(
        default=None,
        description="The fund family.",
        alias="fundFamily",
    )
    category: Optional[str] = Field(
        default=None,
        description="The fund category.",
    )
    exchange: Optional[str] = Field(
        default=None,
        description="The exchange the fund is listed on.",
    )
    exchange_timezone: Optional[str] = Field(
        default=None,
        description="The timezone of the exchange.",
        alias="timeZoneFullName",
    )
    currency: Optional[str] = Field(
        default=None,
        description="The currency in which the fund is listed.",
    )
    nav_price: Optional[float] = Field(
        default=None,
        description="The net asset value per unit of the fund.",
        alias="navPrice",
    )
    total_assets: Optional[int] = Field(
        default=None,
        description="The total value of assets held by the fund.",
        alias="totalAssets",
    )
    trailing_pe: Optional[float] = Field(
        default=None,
        description="The trailing twelve month P/E ratio of the fund's assets.",
        alias="trailingPE",
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="The dividend yield of the fund, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="yield",
    )
    dividend_rate_ttm: Optional[float] = Field(
        default=None,
        description="The trailing twelve month annual dividend rate of the fund, in currency units.",
        alias="trailingAnnualDividendRate",
    )
    dividend_yield_ttm: Optional[float] = Field(
        default=None,
        description="The trailing twelve month annual dividend yield of the fund, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="trailingAnnualDividendYield",
    )
    year_high: Optional[float] = Field(
        default=None,
        description="The fifty-two week high price.",
        alias="fiftyTwoWeekHigh",
    )
    year_low: Optional[float] = Field(
        default=None,
        description="The fifty-two week low price.",
        alias="fiftyTwoWeekLow",
    )
    ma_50d: Optional[float] = Field(
        default=None,
        description="50-day moving average price.",
        alias="fiftyDayAverage",
    )
    ma_200d: Optional[float] = Field(
        default=None,
        description="200-day moving average price.",
        alias="twoHundredDayAverage",
    )
    return_ytd: Optional[float] = Field(
        default=None,
        description="The year-to-date return of the fund, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="ytdReturn",
    )
    return_3y_avg: Optional[float] = Field(
        default=None,
        description="The three year average return of the fund, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="threeYearAverageReturn",
    )
    return_5y_avg: Optional[float] = Field(
        default=None,
        description="The five year average return of the fund, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="fiveYearAverageReturn",
    )
    beta_3y_avg: Optional[float] = Field(
        default=None,
        description="The three year average beta of the fund.",
        alias="beta3Year",
    )
    volume_avg: Optional[float] = Field(
        default=None,
        description="The average daily trading volume of the fund.",
        alias="averageVolume",
    )
    volume_avg_10d: Optional[float] = Field(
        default=None,
        description="The average daily trading volume of the fund over the past ten days.",
        alias="averageDailyVolume10Day",
    )
    bid: Optional[float] = Field(
        default=None,
        description="The current bid price.",
    )
    bid_size: Optional[float] = Field(
        default=None,
        description="The current bid size.",
        alias="bidSize",
    )
    ask: Optional[float] = Field(
        default=None,
        description="The current ask price.",
    )
    ask_size: Optional[float] = Field(
        default=None,
        description="The current ask size.",
        alias="askSize",
    )
    open: Optional[float] = Field(
        default=None,
        description="The open price of the most recent trading session.",
    )
    high: Optional[float] = Field(
        default=None,
        description="The highest price of the most recent trading session.",
        alias="dayHigh",
    )
    low: Optional[float] = Field(
        default=None,
        description="The lowest price of the most recent trading session.",
        alias="dayLow",
    )
    volume: Optional[int] = Field(
        default=None,
        description="The trading volume of the most recent trading session.",
    )
    prev_close: Optional[float] = Field(
        default=None,
        description="The previous closing price.",
        alias="previousClose",
    )

    @field_validator("inception_date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Validate first stock price date."""
        return datetime.utcfromtimestamp(v).date().strftime("%Y-%m-%d") if v else None


class YFinanceEtfInfoFetcher(
    Fetcher[YFinanceEtfInfoQueryParams, List[YFinanceEtfInfoData]]
):
    """YFinance ETF Info fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEtfInfoQueryParams:
        """Transform the query."""
        return YFinanceEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "quoteType",
            "legalType",
            "longName",
            "fundFamily",
            "category",
            "exchange",
            "timeZoneFullName",
            "fundInceptionDate",
            "currency",
            "navPrice",
            "totalAssets",
            "trailingPE",
            "yield",
            "trailingAnnualDividendRate",
            "trailingAnnualDividendYield",
            "bid",
            "bidSize",
            "ask",
            "askSize",
            "open",
            "dayHigh",
            "dayLow",
            "previousClose",
            "volume",
            "averageVolume",
            "averageDailyVolume10Day",
            "fiftyTwoWeekHigh",
            "fiftyTwoWeekLow",
            "fiftyDayAverage",
            "twoHundredDayAverage",
            "ytdReturn",
            "threeYearAverageReturn",
            "fiveYearAverageReturn",
            "beta3Year",
            "longBusinessSummary",
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
                quote_type = ticker.pop("quoteType", "")
                if quote_type == "ETF":
                    for field in fields:
                        if field in ticker:
                            result[field] = ticker.get(field, None)
                if quote_type != "ETF":
                    _warn(f"{symbol} is not an ETF.")
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceEtfInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEtfInfoData]:
        """Transform the data."""
        return [YFinanceEtfInfoData.model_validate(d) for d in data]
