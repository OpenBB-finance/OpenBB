"""Yahoo Finance Futures Historical Price Model."""
# ruff: noqa: SIM105


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,
    FuturesHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import get_futures_data
from openbb_yfinance.utils.references import INTERVALS, MONTHS, PERIODS
from pandas import Timestamp, to_datetime
from pydantic import Field, field_validator
from yfinance import Ticker


class YFinanceFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """Yahoo Finance Futures historical Price Query.

    Source: https://finance.yahoo.com/crypto/
    """

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(
        default=False, description="Include Pre and Post market data."
    )
    adjust: bool = Field(default=True, description="Adjust all the data automatically.")
    back_adjust: bool = Field(
        default=False, description="Back-adjusted data to mimic true historical prices."
    )


class YFinanceFuturesHistoricalData(FuturesHistoricalData):
    """Yahoo Finance Futures Historical Price Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, Timestamp):
            return v.to_pydatetime()
        return v


class YFinanceFuturesHistoricalFetcher(
    Fetcher[
        YFinanceFuturesHistoricalQueryParams,
        List[YFinanceFuturesHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceFuturesHistoricalQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        if params.get("period") is None:
            transformed_params = params

            now = datetime.now().date()
            if params.get("start_date") is None:
                transformed_params["start_date"] = now - relativedelta(years=1)

            if params.get("end_date") is None:
                transformed_params["end_date"] = now

        else:
            transformed_params = params

        return YFinanceFuturesHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: YFinanceFuturesHistoricalQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Yahoo Finance endpoint."""
        symbol = ""

        if query.expiration:
            expiry_date = datetime.strptime(query.expiration, "%Y-%m")
            futures_data = get_futures_data()
            exchange = futures_data[futures_data["Ticker"] == query.symbol][
                "Exchange"
            ].values[0]
            symbol = f"{query.symbol}{MONTHS[expiry_date.month]}{str(expiry_date.year)[-2:]}.{exchange}"

        query_symbol = symbol if symbol else f"{query.symbol}=F"

        if query.period:
            data = Ticker(query_symbol).history(
                interval=query.interval,
                period=query.period,
                prepost=query.prepost,
                auto_adjust=query.adjust,
                back_adjust=query.back_adjust,
                actions=False,
                raise_errors=True,
            )
        else:
            data = Ticker(query_symbol).history(
                interval=query.interval,
                start=query.start_date,
                end=query.end_date,
                prepost=query.prepost,
                auto_adjust=query.adjust,
                back_adjust=query.back_adjust,
                actions=False,
                raise_errors=True,
            )

        if data.empty:
            raise EmptyDataError()

        query.end_date = (
            datetime.now().date() if query.end_date is None else query.end_date
        )
        days = (
            1
            if query.interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
            else 0
        )
        if query.start_date:
            data.index = to_datetime(data.index).tz_convert(None)

            start_date_dt = datetime.combine(query.start_date, datetime.min.time())
            end_date_dt = datetime.combine(query.end_date, datetime.min.time())

            data = data[
                (data.index >= start_date_dt + timedelta(days=days))
                & (data.index <= end_date_dt)
            ]

        data = data.reset_index().rename(
            columns={"index": "Date", "Datetime": "Date"}, errors="ignore"
        )
        data.columns = data.columns.str.lower()
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceFuturesHistoricalQueryParams,  # pylint: disable=unused-argument
        data: dict,
        **kwargs: Any,
    ) -> List[YFinanceFuturesHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceFuturesHistoricalData.model_validate(d) for d in data]
