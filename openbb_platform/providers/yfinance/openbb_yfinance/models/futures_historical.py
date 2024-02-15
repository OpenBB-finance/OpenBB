"""Yahoo Finance Futures Historical Price Model."""

# pylint: disable=unused-argument
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
from openbb_yfinance.utils.helpers import get_futures_data, yf_download
from openbb_yfinance.utils.references import INTERVALS, MONTHS, PERIODS
from pandas import Timestamp, to_datetime
from pydantic import Field, field_validator


class YFinanceFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """Yahoo Finance Futures historical Price Query.

    Source: https://finance.yahoo.com/crypto/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("period", "")
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
        transformed_params = params.copy()

        symbols = params["symbol"].split(",")
        new_symbols = []
        futures_data = get_futures_data()
        for symbol in symbols:
            if params.get("expiration"):
                expiry_date = datetime.strptime(
                    transformed_params["expiration"], "%Y-%m"
                )
                if "." not in symbol:
                    exchange = futures_data[futures_data["Ticker"] == symbol][
                        "Exchange"
                    ].values[0]
                new_symbol = (
                    f"{symbol}{MONTHS[expiry_date.month]}{str(expiry_date.year)[-2:]}.{exchange}"
                    if "." not in symbol
                    else symbol
                )
                new_symbols.append(new_symbol)
            else:
                new_symbols.append(symbol)

        formatted_symbols = []
        for s in new_symbols:
            if "." not in s.upper() and "=F" not in s.upper():
                formatted_symbols.append(f"{s.upper()}=F")
            else:
                formatted_symbols.append(s.upper())

        transformed_params["symbol"] = ",".join(formatted_symbols)

        now = datetime.now()

        if params.get("start_date") is None:
            transformed_params["start_date"] = (now - relativedelta(years=1)).strftime(
                "%Y-%m-%d"
            )

        if params.get("end_date") is None:
            transformed_params["end_date"] = now.strftime("%Y-%m-%d")

        return YFinanceFuturesHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: YFinanceFuturesHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        data = yf_download(
            query.symbol,
            start=query.start_date,
            end=query.end_date,
            interval=query.interval,  # type: ignore
            prepost=True,
            auto_adjust=False,
            actions=False,
        )

        if data.empty:
            raise EmptyDataError()

        days = (
            1
            if query.interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
            else 0
        )
        if "date" in data.columns:
            data.set_index("date", inplace=True)
            data.index = to_datetime(data.index)
        if query.start_date:
            data = data[
                (data.index >= to_datetime(query.start_date))
                & (data.index <= to_datetime(query.end_date + timedelta(days=days)))
            ]

        data.reset_index(inplace=True)
        data.rename(columns={"index": "date"}, inplace=True)

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceFuturesHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceFuturesHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceFuturesHistoricalData.model_validate(d) for d in data]
