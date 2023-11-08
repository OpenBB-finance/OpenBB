"""Polygon Stock NBBO Model."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
    timezone,
)
from typing import Any, Dict, List, Optional, Union

from openbb_polygon.utils.helpers import get_data_one, map_exchanges, map_tape
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_nbbo import (
    StockNBBOData,
    StockNBBOQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, field_validator


class PolygonStockNBBOQueryParams(StockNBBOQueryParams):
    """Polygon Stock NBBO query params.

    Source: https://polygon.io/docs/stocks/get_v3_quotes__stockticker
    """

    limit: Optional[int] = Field(
        default=25,
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
        description="""
            Query by datetime, less than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
        """,
    )
    timestamp_gt: Optional[Union[datetime, str]] = Field(
        default=None,
        description="""
            Query by datetime, greater than. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
        """,
    )
    timestamp_lte: Optional[Union[datetime, str]] = Field(
        default=None,
        description="""
            Query by datetime, less than or equal to.
            Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
        """,
    )
    timestamp_gte: Optional[Union[datetime, str]] = Field(
        default=None,
        description="""
            Query by datetime, greater than or equal to.
            Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
        """,
    )


class PolygonStockNBBOData(StockNBBOData):
    """Polygon Stock NBBO data."""

    __alias_dict__ = {"ask": "ask_price", "bid": "bid_price"}

    tape: Optional[str] = Field(
        default=None, description="The exchange tape.", alias="tape_integer"
    )
    conditions: Optional[Union[str, List[int], List[str]]] = Field(
        default=None, description="A list of condition codes.", alias="conditions"
    )
    indicators: Optional[Any] = Field(
        default=None, description="A list of indicator codes.", alias="indicators"
    )
    sequence_num: Optional[int] = Field(
        default=None,
        description="""
            The sequence number represents the sequence in which message events happened.
            These are increasing and unique per ticker symbol, but will not always be sequential
            (e.g., 1, 2, 6, 9, 10, 11)
        """,
        alias="sequence_number",
    )
    participant_timestamp: Optional[datetime] = Field(
        default=None,
        description="""
            The nanosecond accuracy Participant/Exchange Unix Timestamp.
            This is the timestamp of when the quote was actually generated at the exchange.
        """,
    )
    sip_timestamp: Optional[datetime] = Field(
        default=None,
        description="""
            The nanosecond accuracy SIP Unix Timestamp.
            This is the timestamp of when the SIP received this quote from the exchange which produced it.
        """,
    )
    trf_timestamp: Optional[datetime] = Field(
        default=None,
        description="""
            The nanosecond accuracy TRF (Trade Reporting Facility) Unix Timestamp.
            This is the timestamp of when the trade reporting facility received this quote.
        """,
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

        if v:
            dlt = timedelta(hours=-5)
            tz = timezone(dlt)
            return datetime.fromtimestamp(v / 1000000000).astimezone(tz)
        return None


class PolygonStockNBBOFetcher(
    Fetcher[PolygonStockNBBOQueryParams, List[PolygonStockNBBOData]]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonStockNBBOQueryParams:
        """Transform the query parameters."""
        return PolygonStockNBBOQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonStockNBBOQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Polygon endpoint."""

        api_key = credentials.get("polygon_api_key") if credentials else ""
        # This is to ensure that a list of symbols is not processed, only the first item will be passed.
        symbols = query.symbol.split(",") if "," in query.symbol else [query.symbol]
        query.symbol = symbols[0]
        records = 0

        # Internal hard limit to prevent system overloads.
        _max_ = 10000000
        if (
            query.date
            or query.timestamp_gt
            or query.timestamp_gte
            or query.timestamp_lt
            or query.timestamp_lte
            or query.limit >= 50000
        ):
            max_ = query.limit if query.limit != 25 and query.limit < _max_ else _max_
            query.limit = 50000 if max_ >= 50000 else query.limit
        results = []
        base_url = f"https://api.polygon.io/v3/quotes/{symbols[0]}"
        query_str = (
            get_querystring(query.model_dump(by_alias=True), ["symbol"])
            .replace("_", ".")
            .replace("date", "timestamp")
        )
        url = f"{base_url}?{query_str}&apiKey={api_key}"
        data = get_data_one(url, **kwargs)
        results = data["results"]
        results = map_exchanges(results)
        results = map_tape(results)
        records += len(results)
        if (
            query.date
            or query.timestamp_gt
            or query.timestamp_gte
            and records == 50000
            and "next_url" in data
        ):
            while records < max_ and "next_url" in data and data["next_url"]:
                new_data = get_data_one(f"{data['next_url']}&apiKey={api_key}")
                records += len(new_data["results"])
                data = new_data
                new_data = map_tape(new_data["results"])
                results.extend(map_exchanges(new_data))

        return results

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonStockNBBOData]:
        """Transform the data."""
        return [PolygonStockNBBOData.model_validate(d) for d in data]
