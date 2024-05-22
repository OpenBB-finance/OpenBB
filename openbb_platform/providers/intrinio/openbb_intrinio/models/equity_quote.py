"""Intrinio Equity Quote Model."""

# pylint: disable=unused-argument
import re
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)
from openbb_intrinio.utils.references import SOURCES, VENUES, IntrinioSecurity
from pydantic import Field, field_validator

_warn = warnings.warn


class IntrinioEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Intrinio Equity Quote Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_realtime_price_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    symbol: str = Field(
        description="A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)."
    )
    source: SOURCES = Field(default="iex", description="Source of the data.")


class IntrinioEquityQuoteData(EquityQuoteData):
    """Intrinio Equity Quote Data."""

    __alias_dict__ = {
        "exchange": "listing_venue",
        "market_center": "market_center_code",
        "bid": "bid_price",
        "ask": "ask_price",
        "open": "open_price",
        "close": "close_price",
        "low": "low_price",
        "high": "high_price",
        "last_timestamp": "last_time",
        "volume": "market_volume",
    }
    is_darkpool: Optional[bool] = Field(
        default=None, description="Whether or not the current trade is from a darkpool."
    )
    source: Optional[str] = Field(
        default=None, description="Source of the Intrinio data."
    )
    updated_on: datetime = Field(
        description="Date and Time when the data was last updated."
    )
    security: Optional[IntrinioSecurity] = Field(
        default=None, description="Security details related to the quote."
    )

    @field_validator("last_time", "updated_on", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return (
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            if v.endswith(("Z", "+00:00"))
            else datetime.fromisoformat(v)
        )

    @field_validator("sales_conditions", mode="before", check_fields=False)
    @classmethod
    def validate_sales_conditions(cls, v):
        """Validate sales conditions and remove empty strings."""
        if v:
            control_char_re = re.compile(r"[\x00-\x1f\x7f-\x9f]")
            v = control_char_re.sub("", v).strip()
            v = None if v == "" else v
        return v if v else None

    @field_validator("exchange", "market_center", mode="before", check_fields=False)
    @classmethod
    def validate_listing_venue(cls, v):
        """Validate listing venue and remove empty strings."""
        if v:
            return VENUES.get(v, v)
        return None


class IntrinioEquityQuoteFetcher(
    Fetcher[
        IntrinioEquityQuoteQueryParams,
        List[IntrinioEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquityQuoteQueryParams:
        """Transform the query params."""
        return IntrinioEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"

        async def callback(response: ClientResponse, _: Any) -> dict:
            """Return the response."""
            if response.status != 200:
                return {}

            response_data = await response.json()
            response_data["symbol"] = response_data["security"].get("ticker", None)  # type: ignore
            if "messages" in response_data and response_data.get("messages"):  # type: ignore
                _message = list(response_data.pop("messages"))  # type: ignore
                _warn(str(",".join(_message)))
            return response_data  # type: ignore

        urls = [
            f"{base_url}/securities/{s.strip()}/prices/realtime?source={query.source}&api_key={api_key}"
            for s in query.symbol.split(",")
        ]
        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioEquityQuoteQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioEquityQuoteData]:
        """Return the transformed data."""
        return [IntrinioEquityQuoteData.model_validate(d) for d in data]
