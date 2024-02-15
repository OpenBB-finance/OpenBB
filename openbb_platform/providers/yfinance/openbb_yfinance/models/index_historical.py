"""Yahoo Finance Index Historical Model."""

# ruff: noqa: SIM105

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INDICES, INTERVALS, PERIODS
from pandas import to_datetime
from pydantic import Field


class YFinanceIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """YFinance Index Historical Query.

    Source: https://finance.yahoo.com/world-indices
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(default=True, description="Include Pre and Post market data.")
    rounding: bool = Field(default=True, description="Round prices to two decimals?")


class YFinanceIndexHistoricalData(IndexHistoricalData):
    """YFinance Index Historical Data."""


class YFinanceIndexHistoricalFetcher(
    Fetcher[
        YFinanceIndexHistoricalQueryParams,
        List[YFinanceIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceIndexHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        tickers = params.get("symbol").lower().split(",")

        new_tickers = []
        for ticker in tickers:
            _ticker = ""
            indices = pd.DataFrame(INDICES).transpose().reset_index()
            indices.columns = ["code", "name", "symbol"]

            if ticker in indices["code"].values:
                _ticker = indices[indices["code"] == ticker]["symbol"].values[0]

            if ticker.title() in indices["name"].values:
                _ticker = indices[indices["name"] == ticker.title()]["symbol"].values[0]

            if "^" + ticker.upper() in indices["symbol"].values:
                _ticker = "^" + ticker.upper()

            if ticker.upper() in indices["symbol"].values:
                _ticker = ticker.upper()

            if _ticker != "":
                new_tickers.append(_ticker)

        transformed_params["symbol"] = ",".join(new_tickers)

        return YFinanceIndexHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIndexHistoricalQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query.period,
            prepost=query.prepost,
            rounding=query.rounding,
        )

        if data.empty:
            raise EmptyDataError()

        days = (
            1
            if query.interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
            else 0
        )

        if query.start_date:
            if "date" in data.columns:
                data.set_index("date", inplace=True)
                data.index = to_datetime(data.index)

            data = data[
                (data.index >= to_datetime(query.start_date))
                & (data.index <= to_datetime(query.end_date + timedelta(days=days)))
            ]

        data.reset_index(inplace=True)
        data.rename(columns={"index": "date"}, inplace=True)

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceIndexHistoricalQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> List[YFinanceIndexHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceIndexHistoricalData.model_validate(d) for d in data]
