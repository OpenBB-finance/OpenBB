"""FMP Equity Quote Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many, get_querystring
from pydantic import Field, field_validator


class FMPEquityQuoteQueryParams(EquityQuoteQueryParams):
    """FMP Equity Quote Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """


class FMPEquityQuoteData(EquityQuoteData):
    """FMP Equity Quote Data."""

    __alias_dict__ = {
        "price_avg50": "priceAvg50",
        "price_avg200": "priceAvg200",
        "date": "timestamp",
    }

    symbol: Optional[str] = Field(default=None, description="Symbol of the company.")
    name: Optional[str] = Field(default=None, description="Name of the company.")
    price: Optional[float] = Field(
        default=None, description="Current trading price of the equity."
    )
    changes_percentage: Optional[float] = Field(
        default=None, description="Change percentage of the equity price."
    )
    change: Optional[float] = Field(
        default=None, description="Change in the equity price."
    )
    year_high: Optional[float] = Field(
        default=None, description="Highest price of the equity in the last 52 weeks."
    )
    year_low: Optional[float] = Field(
        default=None, description="Lowest price of the equity in the last 52 weeks."
    )
    market_cap: Optional[float] = Field(
        default=None, description="Market cap of the company."
    )
    price_avg50: Optional[float] = Field(
        default=None, description="50 days average price of the equity."
    )
    price_avg200: Optional[float] = Field(
        default=None, description="200 days average price of the equity."
    )
    volume: Optional[ForceInt] = Field(
        default=None,
        description="Volume of the equity in the current trading day.",
    )
    avg_volume: Optional[ForceInt] = Field(
        default=None,
        description="Average volume of the equity in the last 10 trading days.",
    )
    exchange: Optional[str] = Field(
        default=None, description="Exchange the equity is traded on."
    )
    open: Optional[float] = Field(
        default=None,
        description="Opening price of the equity in the current trading day.",
    )
    previous_close: Optional[float] = Field(
        default=None, description="Previous closing price of the equity."
    )
    eps: Optional[float] = Field(
        default=None, description="Earnings per share of the equity."
    )
    pe: Optional[float] = Field(
        default=None, description="Price earnings ratio of the equity."
    )
    earnings_announcement: Optional[str] = Field(
        default=None, description="Earnings announcement date of the equity."
    )
    shares_outstanding: Optional[ForceInt] = Field(
        default=None, description="Number of shares outstanding of the equity."
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


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
    def extract_data(
        query: FMPEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol"])
        url = f"{base_url}/quote/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityQuoteQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityQuoteData]:
        """Return the transformed data."""
        return [FMPEquityQuoteData.model_validate(d) for d in data]
