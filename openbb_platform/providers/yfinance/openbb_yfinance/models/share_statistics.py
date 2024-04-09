"""YFinance Share Statistics Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from pydantic import Field, field_validator
from yfinance import Ticker

_warn = warnings.warn


class YFinanceShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """YFinance Share Statistics Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinanceShareStatisticsData(ShareStatisticsData):
    """YFinance Share Statistics Data."""

    __alias_dict__ = {
        "outstanding_shares": "sharesOutstanding",
        "float_shares": "floatShares",
        "date": "dateShortInterest",
    }

    implied_shares_outstanding: Optional[int] = Field(
        default=None,
        description="Implied Shares Outstanding of common equity,"
        + " assuming the conversion of all convertible subsidiary equity into common.",
        alias="impliedSharesOutstanding",
    )
    short_interest: Optional[int] = Field(
        default=None,
        description="Number of shares that are reported short.",
        alias="sharesShort",
    )
    short_percent_of_float: Optional[float] = Field(
        default=None,
        description="Percentage of shares that are reported short, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="shortPercentOfFloat",
    )
    days_to_cover: Optional[float] = Field(
        default=None,
        description="Number of days to repurchase the shares as a ratio of average daily volume",
        alias="shortRatio",
    )
    short_interest_prev_month: Optional[int] = Field(
        default=None,
        description="Number of shares that were reported short in the previous month.",
        alias="sharesShortPriorMonth",
    )
    short_interest_prev_date: Optional[dateType] = Field(
        default=None,
        description="Date of the previous month's report.",
        alias="sharesShortPreviousMonthDate",
    )
    insider_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of shares held by insiders, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="heldPercentInsiders",
    )
    institution_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of shares held by institutions, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="heldPercentInstitutions",
    )
    institution_float_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of float held by institutions, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="institutionsFloatPercentHeld",
    )
    institutions_count: Optional[int] = Field(
        default=None,
        description="Number of institutions holding shares.",
        alias="institutionsCount",
    )

    @field_validator(
        "date", "short_interest_prev_date", mode="before", check_fields=False
    )
    @classmethod
    def validate_first_trade_date(cls, v):
        """Convert  dates from UTC timestamp."""
        return datetime.utcfromtimestamp(v).date() if v else None


class YFinanceShareStatisticsFetcher(
    Fetcher[YFinanceShareStatisticsQueryParams, List[YFinanceShareStatisticsData]]
):
    """YFinance Share Statistics Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceShareStatisticsQueryParams:
        """Transform the query."""
        return YFinanceShareStatisticsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceShareStatisticsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "sharesOutstanding",
            "floatShares",
            "impliedSharesOutstanding",
            "sharesShort",
            "sharesShortPriorMonth",
            "sharesShortPreviousMonthDate",
            "shortRatio",
            "shortPercentOfFloat",
            "dateShortInterest",
            "heldPercentInsiders",
            "heldPercentInstitutions",
            "institutionsFloatPercentHeld",
            "institutionsCount",
        ]

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result = {}
            ticker = {}
            try:
                _ticker = Ticker(symbol)
                ticker = _ticker.get_info()
                major_holders = _ticker.get_major_holders(as_dict=True).get("Value")
                if major_holders:
                    ticker.update(major_holders)  # type: ignore
            except Exception as e:
                _warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("sharesOutstanding") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceShareStatisticsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceShareStatisticsData]:
        """Transform the data."""
        return [YFinanceShareStatisticsData.model_validate(d) for d in data]
