"""YFinance Share Statistics Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
    timezone,
)
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from pydantic import Field, field_validator


class YFinanceShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """YFinance Share Statistics Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class YFinanceShareStatisticsData(ShareStatisticsData):
    """YFinance Share Statistics Data."""

    __alias_dict__ = {
        "outstanding_shares": "sharesOutstanding",
        "float_shares": "floatShares",
        "date": "dateShortInterest",
        "implied_shares_outstanding": "impliedSharesOutstanding",
        "short_interest": "sharesShort",
        "short_percent_of_float": "shortPercentOfFloat",
        "days_to_cover": "shortRatio",
        "short_interest_prev_month": "sharesShortPriorMonth",
        "short_interest_prev_date": "sharesShortPreviousMonthDate",
        "insider_ownership": "heldPercentInsiders",
        "institution_ownership": "heldPercentInstitutions",
        "institution_float_ownership": "institutionsFloatPercentHeld",
        "institutions_count": "institutionsCount",
    }

    implied_shares_outstanding: Optional[int] = Field(
        default=None,
        description="Implied Shares Outstanding of common equity,"
        + " assuming the conversion of all convertible subsidiary equity into common.",
    )
    short_interest: Optional[int] = Field(
        default=None,
        description="Number of shares that are reported short.",
    )
    short_percent_of_float: Optional[float] = Field(
        default=None,
        description="Percentage of shares that are reported short, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    days_to_cover: Optional[float] = Field(
        default=None,
        description="Number of days to repurchase the shares as a ratio of average daily volume",
    )
    short_interest_prev_month: Optional[int] = Field(
        default=None,
        description="Number of shares that were reported short in the previous month.",
    )
    short_interest_prev_date: Optional[dateType] = Field(
        default=None,
        description="Date of the previous month's report.",
    )
    insider_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of shares held by insiders, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    institution_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of shares held by institutions, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    institution_float_ownership: Optional[float] = Field(
        default=None,
        description="Percentage of float held by institutions, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    institutions_count: Optional[int] = Field(
        default=None,
        description="Number of institutions holding shares.",
    )

    @field_validator(
        "date", "short_interest_prev_date", mode="before", check_fields=False
    )
    @classmethod
    def validate_first_trade_date(cls, v):
        """Convert dates from UTC timestamp."""
        return datetime.fromtimestamp(v, timezone.utc).date() if v else None


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
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from yfinance import Ticker

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
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())
        messages: list = []

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result: dict = {}
            ticker: dict = {}
            try:
                _ticker = Ticker(
                    symbol,
                    session=session,
                )
                ticker = _ticker.get_info()
                major_holders = _ticker.get_major_holders(as_dict=True).get("Value")
                if major_holders:
                    ticker.update(major_holders)  # type: ignore
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("sharesOutstanding") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for the given symbol(s).")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceShareStatisticsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceShareStatisticsData]:
        """Transform the data."""
        return [YFinanceShareStatisticsData.model_validate(d) for d in data]
