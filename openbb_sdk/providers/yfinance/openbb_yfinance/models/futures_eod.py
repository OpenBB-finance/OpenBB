"""yfinance Futures End of Day fetcher."""


from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_eod import (
    FuturesEODData,
    FuturesEODQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator
from yfinance import Ticker

from openbb_yfinance.utils.helpers import get_futures_data
from openbb_yfinance.utils.references import INTERVALS, PERIODS, MONTHS


class YFinanceFuturesEODQueryParams(FuturesEODQueryParams):
    """YFinance Futures End of Day Query.

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


class YFinanceFuturesEODData(FuturesEODData):
    """YFinance Futures End of Day Data."""

    class Config:
        fields = {
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")


class YFinanceFuturesEODFetcher(
    Fetcher[
        YFinanceFuturesEODQueryParams,
        List[YFinanceFuturesEODData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceFuturesEODQueryParams:
        if params.get("period") is None:
            now = datetime.now().date()
            transformed_params = params

            if params.get("start_date") is None:
                transformed_params["start_date"] = now - relativedelta(years=1)

            if params.get("end_date") is None:
                transformed_params["end_date"] = now
            return YFinanceFuturesEODQueryParams(**transformed_params)

        return YFinanceFuturesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceFuturesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceFuturesEODData]:
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

        data = data.reset_index()
        data["Date"] = (
            data["Date"].dt.tz_localize(None).dt.strftime("%Y-%m-%dT%H:%M:%S")
        )
        data = data.to_dict("records")

        return data

    @staticmethod
    def transform_data(
        data: List[YFinanceFuturesEODData],
    ) -> List[YFinanceFuturesEODData]:
        return [YFinanceFuturesEODData.parse_obj(d) for d in data]
