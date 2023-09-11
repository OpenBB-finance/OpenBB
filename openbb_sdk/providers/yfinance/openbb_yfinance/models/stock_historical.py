"""yfinance Stock End of Day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_historical import (
    StockHistoricalData,
    StockHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pandas import to_datetime
from pydantic import Field, validator

from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INTERVALS, PERIODS


class YFinanceStockHistoricalQueryParams(StockHistoricalQueryParams):
    """YFinance Stock End of Day Query.

    Source: https://finance.yahoo.com/
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(
        default=False, description="Include Pre and Post market data."
    )
    actions: bool = Field(default=True, description="Include actions.")
    auto_adjust: bool = Field(
        default=False, description="Adjust all OHLC data automatically."
    )
    back_adjust: bool = Field(
        default=False, description="Attempt to adjust all the data automatically."
    )
    progress: bool = Field(default=False, description="Show progress bar.")
    ignore_tz: bool = Field(
        default=True,
        description="When combining from different timezones, ignore that part of datetime.",
    )
    rounding: bool = Field(default=True, description="Round to two decimal places?")
    repair: bool = Field(
        default=False,
        description="Detect currency unit 100x mixups and attempt repair.",
    )
    keepna: bool = Field(default=False, description="Keep NaN rows returned by Yahoo?")
    group_by: Literal["ticker", "column"] = Field(
        default="column", description="Group by ticker or column."
    )


class YFinanceStockHistoricalData(StockHistoricalData):
    """YFinance Stock End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d").date()


class YFinanceStockHistoricalFetcher(
    Fetcher[
        YFinanceStockHistoricalQueryParams,
        List[YFinanceStockHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceStockHistoricalQueryParams:
        """Transform the query."""

        return YFinanceStockHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceStockHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the yfinance endpoint."""

        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query.period,
            prepost=query.prepost,
            actions=query.actions,
            auto_adjust=query.auto_adjust,
            back_adjust=query.back_adjust,
            progress=query.progress,
            ignore_tz=query.ignore_tz,
            keepna=query.keepna,
            repair=query.repair,
            rounding=query.rounding,
            group_by=query.group_by,
        )

        query.end_date = (
            datetime.now().date() if query.end_date is None else query.end_date
        )
        days = (
            1
            if query.interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
            else 0
        )
        if query.start_date is not None:
            data["date"] = to_datetime(data["date"])
            data.set_index("date", inplace=True)
            data = data.loc[query.start_date : (query.end_date + timedelta(days=days))]

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[YFinanceStockHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceStockHistoricalData.parse_obj(d) for d in data]
