"""Yahoo Finance Market Indices Model."""
# ruff: noqa: SIM105


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_indices import (
    MarketIndicesData,
    MarketIndicesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INDICES, INTERVALS, PERIODS
from pandas import to_datetime
from pydantic import Field


class YFinanceMarketIndicesQueryParams(MarketIndicesQueryParams):
    """YFinance Market Indices Query.

    Source: https://finance.yahoo.com/world-indices
    """

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(default=True, description="Include Pre and Post market data.")
    rounding: bool = Field(default=True, description="Round prices to two decimals?")


class YFinanceMarketIndicesData(MarketIndicesData):
    """YFinance Market Indices Data."""


class YFinanceMarketIndicesFetcher(
    Fetcher[
        YFinanceMarketIndicesQueryParams,
        List[YFinanceMarketIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceMarketIndicesQueryParams:
        """Transform the query."""
        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceMarketIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceMarketIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        symbol = query.symbol.lower()
        indices = pd.DataFrame(INDICES).transpose().reset_index()
        indices.columns = ["code", "name", "symbol"]

        if symbol in indices["code"].to_list():
            symbol = indices[indices["code"] == symbol]["symbol"].values[0]

        if symbol.title() in indices["name"].to_list():
            symbol = indices[indices["name"] == symbol.title()]["symbol"].values[0]

        if "^" + symbol.upper() in indices["symbol"].to_list():
            symbol = "^" + symbol.upper()

        data = yf_download(
            symbol=symbol,
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

            start_date_dt = datetime.combine(query.start_date, datetime.min.time())
            end_date_dt = datetime.combine(query.end_date, datetime.min.time())

            data = data[
                (data.index >= start_date_dt + timedelta(days=days))
                & (data.index <= end_date_dt)
            ]

        data.reset_index(inplace=True)
        data.rename(columns={"index": "date"}, inplace=True)

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceMarketIndicesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> List[YFinanceMarketIndicesData]:
        """Transform the data to the standard format."""
        return [YFinanceMarketIndicesData.model_validate(d) for d in data]
