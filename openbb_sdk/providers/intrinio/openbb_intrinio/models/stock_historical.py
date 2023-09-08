"""Intrinio Stocks end of day fetcher."""

from datetime import datetime, time
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_historical import (
    StockHistoricalData,
    StockHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt, validator

from openbb_intrinio.utils.helpers import get_data_one
from openbb_intrinio.utils.references import INTERVALS, TIMEZONES


class IntrinioStockHistoricalQueryParams(StockHistoricalQueryParams):
    """Intrinio Stock end of day Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_interval_prices_v2
    """

    symbol: str = Field(
        description="A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)."
    )
    timezone: Optional[TIMEZONES] = Field(
        default="UTC", description="Returns trading times in this timezone."
    )
    source: Optional[Literal["realtime", "delayed", "nasdaq_basic"]] = Field(
        default="realtime", description="The source of the data."
    )
    start_time: Optional[time] = Field(
        description="Return intervals starting at the specified time on the `start_date` formatted as 'hh:mm:ss'."
    )
    end_time: Optional[time] = Field(
        description="Return intervals stopping at the specified time on the `end_date` formatted as 'hh:mm:ss'."
    )
    interval_size: Optional[INTERVALS] = Field(
        default="60m", description=QUERY_DESCRIPTIONS.get("frequency", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=300,
        description=f"{QUERY_DESCRIPTIONS.get('limit', '')}",
    )
    next_page: Optional[str] = Field(
        description="Token to get the next page of data from a previous API call."
    )
    all_pages: Optional[bool] = Field(
        default=False,
        description="Returns all pages of data from the API call at once.",
    )

    @validator("limit", pre=True)
    def limit_check(cls, v):  # pylint: disable=E0213
        """Set the limit bound to 300."""
        return min(v, 300)


class IntrinioStockHistoricalData(StockHistoricalData):
    """Intrinio Stock end of day Data."""

    class Config:
        fields = {
            "date": "time",
        }

    close_time: Optional[datetime] = Field(
        description="The timestamp that represents the end of the interval span."
    )
    interval: Optional[str] = Field(description="The data time frequency.")
    average: Optional[float] = Field(
        description="Average trade price of an individual stock during the interval."
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        alias="change",
    )

    @validator("time", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return (
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            if v.endswith(("Z", "+00:00"))
            else datetime.fromisoformat(v)
        )

    @validator("close_time", pre=True, check_fields=False)
    def close_time_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return (
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            if v.endswith(("Z", "+00:00"))
            else datetime.fromisoformat(v)
        )


class IntrinioStockHistoricalFetcher(
    Fetcher[
        IntrinioStockHistoricalQueryParams,
        List[IntrinioStockHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioStockHistoricalQueryParams:
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

        return IntrinioStockHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: IntrinioStockHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.dict(by_alias=True), ["symbol", "all_pages"])
        query_str = query_str.replace("limit", "page_size")
        url = (
            f"{base_url}/securities/{query.symbol}/prices/intervals"
            f"?{query_str}&api_key={api_key}"
        )

        data = get_data_one(url, **kwargs)

        if query.all_pages:
            all_data = data["intervals"]
            next_page = data["next_page"]

            while next_page:
                query_str = get_querystring(
                    query.dict(by_alias=True), ["symbol", "next_page", "all_pages"]
                )
                query_str = query_str.replace("limit", "page_size")
                url = (
                    f"{base_url}/securities/{query.symbol}/prices/intervals"
                    f"?{query_str}&next_page={next_page}&api_key={api_key}"
                )

                data = get_data_one(url, **kwargs)
                all_data.extend(data.get("intervals", []))

                next_page = data.get("next_page", None)

            return all_data

        return data.get("intervals", [])

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioStockHistoricalData]:
        """Return the transformed data."""

        return [IntrinioStockHistoricalData(**d) for d in data]
