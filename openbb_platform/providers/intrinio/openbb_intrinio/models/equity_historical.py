"""Intrinio Equity Historical Price Model."""

# pylint: disable = unused-argument

from datetime import datetime, time
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_request,
    get_querystring,
)
from pydantic import Field, PrivateAttr, model_validator


class IntrinioEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Intrinio Equity Historical Price Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_interval_prices_v2
    """

    __json_schema_extra__ = {
        "interval": {
            "choices": [
                "1m",
                "5m",
                "10m",
                "15m",
                "30m",
                "60m",
                "1h",
                "1d",
                "1W",
                "1M",
                "1Q",
                "1Y",
            ],
        },
    }

    symbol: str = Field(
        description="A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)."
    )
    interval: Literal[
        "1m", "5m", "10m", "15m", "30m", "60m", "1h", "1d", "1W", "1M", "1Q", "1Y"
    ] = Field(default="1d", description=QUERY_DESCRIPTIONS.get("interval", ""))
    start_time: Optional[time] = Field(
        default=None,
        description="Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'.",
    )
    end_time: Optional[time] = Field(
        default=None,
        description="Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'.",
    )
    timezone: Optional[str] = Field(
        default="America/New_York",
        description="Timezone of the data, in the IANA format (Continent/City).",
    )
    source: Literal["realtime", "delayed", "nasdaq_basic"] = Field(
        default="realtime", description="The source of the data."
    )
    _interval_size: Literal["1m", "5m", "10m", "15m", "30m", "60m", "1h"] = PrivateAttr(
        default=None
    )
    _frequency: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] = (
        PrivateAttr(default=None)
    )

    # pylint: disable=protected-access
    @model_validator(mode="after")
    @classmethod
    def set_time_params(cls, values: "IntrinioEquityHistoricalQueryParams"):
        """Set the default start & end date and time params for Intrinio API."""
        frequency_dict = {
            "1d": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "1Q": "quarterly",
            "1Y": "yearly",
        }

        if values.interval in ["1m", "5m", "10m", "15m", "30m", "60m", "1h"]:
            values._interval_size = values.interval  # type: ignore
        elif values.interval in ["1d", "1W", "1M", "1Q", "1Y"]:
            values._frequency = frequency_dict[values.interval]  # type: ignore

        return values


class IntrinioEquityHistoricalData(EquityHistoricalData):
    """Intrinio Equity Historical Price Data."""

    __alias_dict__ = {
        "date": "time",
        "change_percent": "percent_change",
        "interval": "frequency",
        "intra_period": "intraperiod",
    }

    average: Optional[float] = Field(
        default=None,
        description="Average trade price of an individual equity during the interval.",
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price of the symbol from the previous day.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Percent change in the price of the symbol from the previous day.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    adj_open: Optional[float] = Field(
        default=None,
        description="The adjusted open price.",
    )
    adj_high: Optional[float] = Field(
        default=None,
        description="The adjusted high price.",
    )
    adj_low: Optional[float] = Field(
        default=None,
        description="The adjusted low price.",
    )
    adj_close: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("adj_close", ""),
    )
    adj_volume: Optional[float] = Field(
        default=None,
        description="The adjusted volume.",
    )
    fifty_two_week_high: Optional[float] = Field(
        default=None,
        description="52 week high price for the symbol.",
    )
    fifty_two_week_low: Optional[float] = Field(
        default=None,
        description="52 week low price for the symbol.",
    )
    factor: Optional[float] = Field(
        default=None,
        description="factor by which to multiply equity prices before this "
        "date, in order to calculate historically-adjusted equity prices.",
    )
    split_ratio: Optional[float] = Field(
        default=None,
        description="Ratio of the equity split, if a split occurred.",
    )
    dividend: Optional[float] = Field(
        default=None,
        description="Dividend amount, if a dividend was paid.",
    )
    close_time: Optional[datetime] = Field(
        default=None,
        description="The timestamp that represents the end of the interval span.",
    )
    interval: Optional[str] = Field(
        default=None,
        description="The data time frequency.",
    )
    intra_period: Optional[bool] = Field(
        default=None,
        description="If true, the equity price represents an unfinished period "
        "(be it day, week, quarter, month, or year), meaning that the close "
        "price is the latest price available, not the official close price "
        "for the period",
    )


class IntrinioEquityHistoricalFetcher(
    Fetcher[
        IntrinioEquityHistoricalQueryParams,
        List[IntrinioEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        if params.get("start_time") is None:
            transformed_params["start_time"] = time(0, 0, 0)

        if params.get("end_time") is None:
            transformed_params["end_time"] = time(23, 59, 59)

        return IntrinioEquityHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    async def aextract_data(
        query: IntrinioEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = f"https://api-v2.intrinio.com/securities/{query.symbol}/prices"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "interval"]
        )

        if query._interval_size:
            base_url += f"/intervals?interval_size={query._interval_size}"
            data_key = "intervals"
        elif query._frequency:
            base_url += f"?frequency={query._frequency}"
            data_key = "stock_prices"

        async def callback(response: ClientResponse, session: ClientSession) -> list:
            """Return the response."""
            init_response = await response.json()
            if "error" in init_response:
                raise OpenBBError(
                    f"Intrinio Error Message -> {init_response['error']}: {init_response.get('message')}"  # type: ignore
                )

            all_data: list = init_response.get(data_key, [])  # type: ignore

            next_page = init_response.get("next_page", None)  # type: ignore
            while next_page:
                url = response.url.update_query(next_page=next_page).human_repr()
                response_data = await session.get_json(url)

                all_data.extend(response_data.get(data_key, []))  # type: ignore
                next_page = response_data.get("next_page", None)  # type: ignore

            return all_data

        url = f"{base_url}&{query_str}&api_key={api_key}"

        return await amake_request(url, response_callback=callback, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: IntrinioEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioEquityHistoricalData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        date_col = (
            "time"
            if query.interval in ["1m", "5m", "10m", "15m", "30m", "60m", "1h"]
            else "date"
        )
        return [
            IntrinioEquityHistoricalData.model_validate(d)
            for d in sorted(data, key=lambda x: x[date_col], reverse=False)
        ]
