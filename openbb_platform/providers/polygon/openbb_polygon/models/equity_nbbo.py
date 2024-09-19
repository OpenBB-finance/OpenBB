"""Polygon Equity NBBO Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_nbbo import (
    EquityNBBOData,
    EquityNBBOQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class PolygonEquityNBBOQueryParams(EquityNBBOQueryParams):
    """Polygon Equity NBBO Query.

    Source: https://polygon.io/docs/stocks/get_v3_quotes__stockticker
    """

    __alias_dict__ = {"date": "timestamp"}

    limit: int = Field(
        default=50000,
        description=(
            QUERY_DESCRIPTIONS.get("limit", "")
            + " Up to ten million records will be returned. Pagination occurs in groups of 50,000."
            + " Remaining limit values will always return 50,000 more records unless it is the last page."
            + " High volume tickers will require multiple max requests for a single day's NBBO records."
            + " Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV."
            + " Splitting large requests into chunks is recommended for full-day requests of high-volume symbols."
        ),
    )
    date: Optional[dateType] = Field(
        default=None,
        description=(
            QUERY_DESCRIPTIONS.get("date", "")
            + " Use bracketed the timestamp parameters to specify exact time ranges."
        ),
    )
    timestamp_lt: Optional[Union[datetime, str]] = Field(
        default=None,
        description=(
            "Query by datetime, less than. Either a date with the format 'YYYY-MM-DD' or a TZ-aware timestamp string, "
            "'YYYY-MM-DDTH:M:S.000000000-04:00'. Include all nanoseconds and the 'T' between the day and hour."
        ),
    )
    timestamp_gt: Optional[Union[datetime, str]] = Field(
        default=None,
        description=(
            "Query by datetime, greater than. Either a date with the format 'YYYY-MM-DD' or a TZ-aware timestamp string, "
            "'YYYY-MM-DDTH:M:S.000000000-04:00'. Include all nanoseconds and the 'T' between the day and hour."
        ),
    )
    timestamp_lte: Optional[Union[datetime, str]] = Field(
        default=None,
        description=(
            "Query by datetime, less than or equal to. Either a date with the format 'YYYY-MM-DD' or a TZ-aware "
            "timestamp string, 'YYYY-MM-DDTH:M:S.000000000-04:00'. Include all nanoseconds and the 'T' between the "
            "day and hour."
        ),
    )
    timestamp_gte: Optional[Union[datetime, str]] = Field(
        default=None,
        description=(
            "Query by datetime, greater than or equal to. Either a date with the format 'YYYY-MM-DD' or a TZ-aware "
            "timestamp string, 'YYYY-MM-DDTH:M:S.000000000-04:00'. Include all nanoseconds and the 'T' between the "
            "day and hour."
        ),
    )

    @field_validator("limit", mode="before", check_fields=False)
    @classmethod
    def capping_limit(cls, v):
        """Caps the number of records to 10 million."""
        return 10000000 if v > 10000000 else v


class PolygonEquityNBBOData(EquityNBBOData):
    """Polygon Equity NBBO data."""

    __alias_dict__ = {
        "ask": "ask_price",
        "bid": "bid_price",
        "tape": "tape_integer",
        "sequence_num": "sequence_number",
    }

    tape: Optional[str] = Field(
        default=None,
        description="The exchange tape.",
    )
    conditions: Optional[Union[str, List[int], List[str]]] = Field(
        default=None,
        description="A list of condition codes.",
    )
    indicators: Optional[List[int]] = Field(
        default=None,
        description="A list of indicator codes.",
    )
    sequence_num: Optional[int] = Field(
        default=None,
        description=(
            "The sequence number represents the sequence in which message events happened. "
            "These are increasing and unique per ticker symbol, but will not always be sequential "
            "(e.g., 1, 2, 6, 9, 10, 11)"
        ),
    )
    participant_timestamp: Optional[datetime] = Field(
        default=None,
        description=(
            "The nanosecond accuracy Participant/Exchange Unix Timestamp. "
            "This is the timestamp of when the quote was actually generated at the exchange."
        ),
    )
    sip_timestamp: Optional[datetime] = Field(
        default=None,
        description=(
            "The nanosecond accuracy SIP Unix Timestamp. "
            "This is the timestamp of when the SIP received this quote from the exchange which produced it."
        ),
    )
    trf_timestamp: Optional[datetime] = Field(
        default=None,
        description=(
            "The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp. "
            "This is the timestamp of when the trade reporting facility received this quote."
        ),
    )

    @field_validator(
        "sip_timestamp",
        "participant_timestamp",
        "trf_timestamp",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        return (
            to_datetime(v, unit="ns", origin="unix", utc=True).tz_convert("US/Eastern")
            if v
            else None
        )


class PolygonEquityNBBOFetcher(
    Fetcher[PolygonEquityNBBOQueryParams, List[PolygonEquityNBBOData]]
):
    """Polygon Equity NBBO Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonEquityNBBOQueryParams:
        """Transform the query parameters."""
        return PolygonEquityNBBOQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonEquityNBBOQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Polygon endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_polygon.utils.helpers import get_data_one, map_tape

        api_key = credentials.get("polygon_api_key") if credentials else ""
        data: List[Dict] = []
        base_url = "https://api.polygon.io/v3"

        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "limit"]
        )
        query_str = (
            f"{query_str}&limit={query.limit}"
            if query.limit <= 50000
            else f"{query_str}&limit=50000"
        )
        query_str = query_str.replace("_", ".")

        url = f"{base_url}/quotes/{query.symbol}?{query_str}&apiKey={api_key}"
        response = await get_data_one(url, **kwargs)
        next_url = response.get("next_url", None)
        data.extend(response["results"])
        records = len(data)

        while records < query.limit and next_url:
            url = f"{next_url}&apiKey={api_key}"
            response = await get_data_one(url, **kwargs)
            next_url = response.get("next_url", None)
            data.extend(response["results"])
            records += len(data)

        exchanges_url = f"{base_url}/reference/exchanges?asset_class=stocks&locale=us&apiKey={api_key}"
        exchanges = await get_data_one(exchanges_url, **kwargs)
        exchanges = exchanges["results"]
        exchange_id_map = {e["id"]: e for e in exchanges}

        data = [
            {
                **d,
                "ask_exchange": exchange_id_map.get(d["ask_exchange"], {}).get(
                    "name", ""
                ),
                "bid_exchange": exchange_id_map.get(d["bid_exchange"], {}).get(
                    "name", ""
                ),
                "tape": map_tape(d.get("tape", "")),
            }
            for d in data
        ]

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: PolygonEquityNBBOQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonEquityNBBOData]:
        """Transform the data."""
        return [PolygonEquityNBBOData.model_validate(d) for d in data]
