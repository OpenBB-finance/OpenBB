"""Nasdaq Market Status Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

SESSION_FIELDS = {
    "pre_market_open": "preMarketOpeningTime",
    "pre_market_close": "preMarketClosingTime",
    "market_open": "marketOpeningTime",
    "market_close": "marketClosingTime",
    "after_hours_open": "afterHoursMarketOpeningTime",
    "after_hours_close": "afterHoursMarketClosingTime",
}


class NasdaqMarketStatusQueryParams(QueryParams):
    """Nasdaq Market Status Query.

    Source: https://www.nasdaq.com/market-activity
    """


class NasdaqMarketStatusData(Data):
    """Nasdaq Market Status Data."""

    country: str | None = Field(default=None, description="The market's country.")
    status: str | None = Field(
        default=None, description="The session status - i.e., 'Open' or 'Closed'."
    )
    indicator: str | None = Field(
        default=None, description="The status message displayed by Nasdaq."
    )
    countdown: str | None = Field(
        default=None, description="Time remaining until the next session change."
    )
    is_business_day: bool | None = Field(
        default=None, description="Whether the current day is a trading day."
    )
    previous_trade_date: dateType | None = Field(
        default=None, description="The previous trading day."
    )
    next_trade_date: dateType | None = Field(
        default=None, description="The next trading day."
    )
    pre_market_open: datetime | None = Field(
        default=None, description="The pre-market session open, in US/Eastern time."
    )
    pre_market_close: datetime | None = Field(
        default=None, description="The pre-market session close, in US/Eastern time."
    )
    market_open: datetime | None = Field(
        default=None, description="The regular session open, in US/Eastern time."
    )
    market_close: datetime | None = Field(
        default=None, description="The regular session close, in US/Eastern time."
    )
    after_hours_open: datetime | None = Field(
        default=None, description="The after-hours session open, in US/Eastern time."
    )
    after_hours_close: datetime | None = Field(
        default=None, description="The after-hours session close, in US/Eastern time."
    )


class NasdaqMarketStatusFetcher(
    Fetcher[
        NasdaqMarketStatusQueryParams,
        list[NasdaqMarketStatusData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqMarketStatusQueryParams:
        """Transform the query."""
        return NasdaqMarketStatusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqMarketStatusQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        return await get_nasdaq_data("market-info") or {}

    @staticmethod
    def transform_data(
        query: NasdaqMarketStatusQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqMarketStatusData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no market status.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_date

        if not data:
            raise EmptyDataError("No market status was returned.")

        record: dict[str, Any] = {
            "country": data.get("country"),
            "status": data.get("mrktStatus"),
            "indicator": data.get("marketIndicator"),
            "countdown": data.get("mrktCountDown"),
            "is_business_day": data.get("isBusinessDay"),
            "previous_trade_date": to_date(data.get("previousTradeDate")),
            "next_trade_date": to_date(data.get("nextTradeDate")),
        }

        for field, label in SESSION_FIELDS.items():
            record[field] = parse_eastern(data.get(label))

        return [NasdaqMarketStatusData.model_validate(record)]


def parse_eastern(value: Any) -> datetime | None:
    """Parse a Nasdaq session timestamp.

    Parameters
    ----------
    value : Any
        A timestamp such as 'Jul 27, 2026 04:00 AM ET'.

    Returns
    -------
    datetime or None
        The naive US/Eastern timestamp, or None when unparseable.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.strptime(
            value.strip().removesuffix("ET").strip(), "%b %d, %Y %I:%M %p"
        )
    except ValueError:
        return None
