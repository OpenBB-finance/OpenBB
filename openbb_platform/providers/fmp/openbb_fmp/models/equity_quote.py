"""FMP Equity Quote Model."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests
from openbb_fmp.utils.helpers import get_querystring
from pydantic import Field, field_validator


class FMPEquityQuoteQueryParams(EquityQuoteQueryParams):
    """FMP Equity Quote Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FMPEquityQuoteData(EquityQuoteData):
    """FMP Equity Quote Data."""

    __alias_dict__ = {
        "price_avg50": "priceAvg50",
        "price_avg200": "priceAvg200",
        "last_timestamp": "timestamp",
        "high": "dayHigh",
        "low": "dayLow",
        "last_price": "price",
        "change_percent": "changesPercentage",
        "prev_close": "previousClose",
    }
    price_avg50: Optional[float] = Field(
        default=None, description="50 day moving average price."
    )
    price_avg200: Optional[float] = Field(
        default=None, description="200 day moving average price."
    )
    avg_volume: Optional[ForceInt] = Field(
        default=None,
        description="Average volume over the last 10 trading days.",
    )
    market_cap: Optional[float] = Field(
        default=None, description="Market cap of the company."
    )
    shares_outstanding: Optional[ForceInt] = Field(
        default=None, description="Number of shares outstanding."
    )
    eps: Optional[float] = Field(default=None, description="Earnings per share.")
    pe: Optional[float] = Field(default=None, description="Price earnings ratio.")
    earnings_announcement: Optional[Union[datetime, str]] = Field(
        default=None, description="Upcoming earnings announcement date."
    )

    @field_validator("last_timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_last_timestamp(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        v = int(v) if isinstance(v, str) else v
        return datetime.utcfromtimestamp(int(v)).replace(tzinfo=timezone.utc)

    @field_validator("earnings_announcement", mode="before", check_fields=False)
    @classmethod
    def timestamp_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime string as a datetime object."""
        if v:
            dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f%z")
            dt = dt.replace(microsecond=0)
            timestamp = dt.timestamp()
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return None

    @field_validator("change_percent", mode="after", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):  # pylint: disable=E0213
        """Return the percent value as a normalized value."""
        return float(v) / 100 if v else None


class FMPEquityQuoteFetcher(
    Fetcher[
        FMPEquityQuoteQueryParams,
        List[FMPEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityQuoteQueryParams:
        """Transform the query params."""
        return FMPEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol"])

        symbols = query.symbol.split(",")
        symbols_split = [
            ",".join(symbols[i : i + 10]) for i in range(0, len(symbols), 10)
        ]

        urls = [
            f"{base_url}/quote/{symbol}?{query_str}&apikey={api_key}"
            for symbol in symbols_split
        ]

        return await amake_requests(urls, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityQuoteQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityQuoteData]:
        """Return the transformed data."""
        return [FMPEquityQuoteData.model_validate(d) for d in data]
