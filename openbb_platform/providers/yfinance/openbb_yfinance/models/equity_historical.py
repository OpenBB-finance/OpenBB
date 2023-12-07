"""Yahoo Finance Equity Historical Price Model."""
# ruff: noqa: SIM105

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import PERIODS
from pandas import Timestamp, to_datetime
from pydantic import Field, PrivateAttr, field_validator


class YFinanceEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Yahoo Finance Equity Historical Price Query.

    Source: https://finance.yahoo.com/
    """

    interval: Optional[
        Literal[
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1W",
            "1M",
            "3M",
        ]
    ] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )
    prepost: bool = Field(
        default=False, description="Include Pre and Post market data."
    )
    include: bool = Field(
        default=True, description="Include Dividends and Stock Splits in results."
    )
    adjusted: bool = Field(
        default=False,
        description="Adjust all OHLC data automatically.",
    )
    ignore_tz: bool = Field(
        default=True,
        description="When combining from different timezones, ignore that part of datetime.",
    )
    _progress: bool = PrivateAttr(default=False)
    _keepna: bool = PrivateAttr(default=False)
    _period: Optional[PERIODS] = PrivateAttr(default="max")
    _rounding: bool = PrivateAttr(default=True)
    _repair: bool = PrivateAttr(default=False)
    _group_by: Literal["ticker", "column"] = PrivateAttr(default="ticker")


class YFinanceEquityHistoricalData(EquityHistoricalData):
    """Yahoo Finance Equity Historical Price Data."""

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if isinstance(v, Timestamp):
            return v.to_pydatetime()
        return v


class YFinanceEquityHistoricalFetcher(
    Fetcher[
        YFinanceEquityHistoricalQueryParams,
        List[YFinanceEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEquityHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceEquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceEquityHistoricalQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        if query.interval == "1W":
            query.interval = "1wk"
        elif query.interval == "1M":
            query.interval = "1mo"
        elif query.interval == "3M":
            query.interval = "3mo"

        # pylint: disable=protected-access
        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query._period,
            prepost=query.prepost,
            actions=query.include,
            progress=query._progress,
            ignore_tz=query.ignore_tz,
            keepna=query._keepna,
            repair=query._repair,
            rounding=query._rounding,
            group_by=query._group_by,
            adjusted=query.adjusted,
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
        query: YFinanceEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEquityHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceEquityHistoricalData.model_validate(d) for d in data]
