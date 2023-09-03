"""yfinance Forex End of Day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_historical import (
    ForexHistoricalData,
    ForexHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator

from openbb_yfinance.utils.references import INTERVALS, PERIODS


class YFinanceForexHistoricalQueryParams(ForexHistoricalQueryParams):
    """YFinance Forex End of Day Query.

    Source: https://finance.yahoo.com/currencies/
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class YFinanceForexHistoricalData(ForexHistoricalData):
    """YFinance Forex End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d").date()


class YFinanceForexHistoricalFetcher(
    Fetcher[
        YFinanceForexHistoricalQueryParams,
        List[YFinanceForexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceForexHistoricalQueryParams:
        """Transform the query."""

        return YFinanceForexHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceForexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the yfinance endpoint."""

        query.symbol = f"{query.symbol.upper()}=X"
        _start_date = query.start_date

        if query.interval in ["60m", "1h"]:
            query.period = (
                "2y" if query.period in ["5y", "10y", "max"] else query.period
            )
            _start_date = None

        if query.interval in ["2m", "5m", "15m", "30m", "90m"]:
            _start_date = (datetime.now().date() - timedelta(days=30)).strftime(
                "%Y-%m-%d"
            )
            query.period = "1mo"

        if query.interval == "1m":
            query.period = "5d"
            _start_date = None

        data = yf.Ticker(query.symbol).history(
            interval=query.interval,
            period=query.period,
            auto_adjust=False,
            start=_start_date,
        )

        if not data.empty:
            data = data.reset_index()
            data = data.rename(columns={"Date": "date", "Datetime": "date"})
            data["date"] = pd.to_datetime(data["date"])
            data["date"] = data["date"].dt.tz_localize(None)
            data = data[data["Open"] > 0]

            if query.start_date is not None:
                data = data[data["date"] >= pd.to_datetime(query.start_date)]
                if query.end_date is not None and pd.to_datetime(
                    query.end_date
                ) > pd.to_datetime(query.start_date):
                    data = data[
                        data["date"]
                        <= (pd.to_datetime(query.end_date) + timedelta(days=1))
                    ]

            data = data.drop(columns=["Dividends", "Stock Splits", "Adj Close"])

            data.columns = data.columns.str.lower().to_list()

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[YFinanceForexHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceForexHistoricalData.parse_obj(d) for d in data]
