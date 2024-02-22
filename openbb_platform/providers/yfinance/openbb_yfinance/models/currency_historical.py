"""Yahoo Finance Currency Price Model."""

# ruff: noqa: SIM105
# pylint: disable=unused-argument

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INTERVALS, PERIODS
from pandas import to_datetime
from pydantic import Field


class YFinanceCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Yahoo Finance Currency Price Query.

    Source: https://finance.yahoo.com/currencies/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class YFinanceCurrencyHistoricalData(CurrencyHistoricalData):
    """Yahoo Finance Currency Price Data."""


class YFinanceCurrencyHistoricalFetcher(
    Fetcher[
        YFinanceCurrencyHistoricalQueryParams,
        List[YFinanceCurrencyHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFinanceCurrencyHistoricalQueryParams:
        """Transform the query."""

        transformed_params = params
        symbols = params["symbol"].split(",")
        new_symbols = [
            f"{s.upper()}=X" if "=X" not in s.upper() else s.upper() for s in symbols
        ]
        transformed_params["symbol"] = ",".join(new_symbols)

        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: YFinanceCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        data = yf_download(
            query.symbol,
            start=query.start_date,
            end=query.end_date,
            interval=query.interval,
            period=query.period,
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
        if query.interval in ["1d", "1W", "1M", "3M"]:
            data["date"] = data["date"].dt.strftime("%Y-%m-%d")

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceCurrencyHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCurrencyHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceCurrencyHistoricalData.model_validate(d) for d in data]
