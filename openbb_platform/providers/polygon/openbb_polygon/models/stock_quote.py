"""Polygon Stock Quotes Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_polygon.utils.helpers import get_data_one, map_exchanges, map_tape
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_quote import StockQuoteQueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_provider.utils.helpers import get_querystring
from pandas import to_datetime
from pydantic import Field, field_validator


class PolygonStockQuoteQueryParams(StockQuoteQueryParams):
    """Polygon Stock Quote query params."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " If a list is supplied, only the first symbol will be processed."
    )
    limit: Optional[int] = Field(
        default=25,
        description=(
            QUERY_DESCRIPTIONS.get("interval", "")
            + " Up to ten million records will be returned. Pagination occurs in groups of 50,000."
            + " Remaining limit values will always return 50,000 more records unless it is the last page."
            + " High volume tickers will require multiple max requests for a single day's NBBO records."
            + " Expect stocks, like SPY, to approach 1GB in size, per day, as a raw CSV."
            + " Splitting large requests into chunks is recommended for full-day requests of high-volume symbols."
        ),
    )
    timestamp: Optional[Union[datetime, str]] = Field(
        default=None,
        description="""
            Query by datetime. Either a date with the format YYYY-MM-DD or a TZ-aware timestamp string,
            YYYY-MM-DDTH:M:S.000000000-04:00". Include all nanoseconds and the 'T' between the day and hour.
        """,
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


class PolygonStockQuoteData(Data):
    """Polygon Stock Quote data."""

    ask_exchange: Optional[Union[int, str]] = Field(
        default=None,
        description="The exchange ID for the ask. https://polygon.io/docs/stocks/get_v3_reference_exchanges",
        alias="ask_exchange",
    )
    ask: Optional[float] = Field(
        default=None, description="The last ask price.", alias="ask_price"
    )
    ask_size: Optional[int] = Field(
        default=None,
        description="""
        The ask size. This represents the number of round lot orders at the given ask price.
        The normal round lot size is 100 shares.
        An ask size of 2 means there are 200 shares available to purchase at the given ask price.
        """,
        alias="ask_size",
    )
    bid_size: Optional[int] = Field(
        default=None, description="The bid size in round lots.", alias="bid_size"
    )
    bid: Optional[float] = Field(
        default=None, description="The last bid price.", alias="bid_price"
    )
    bid_exchange: Optional[Union[int, str]] = Field(
        default=None,
        description="The exchange ID for the bid. https://polygon.io/docs/stocks/get_v3_reference_exchanges",
        alias="bid_exchange",
    )
    tape: Optional[Union[int, str]] = Field(
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
    participant_timestamp: Optional[Union[int, datetime]] = Field(
        default=None,
        description="""
            The nanosecond accuracy Participant/Exchange Unix Timestamp.
            This is the timestamp of when the quote was actually generated at the exchange.
        """,
    )
    sip_timestamp: Optional[Union[int, datetime]] = Field(
        default=None,
        description="""
            The nanosecond accuracy SIP Unix Timestamp.
            This is the timestamp of when the SIP received this quote from the exchange which produced it.
        """,
    )
    trf_timestamp: Optional[Union[int, datetime]] = Field(
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
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        return (
            to_datetime(v, unit="ns", origin="unix", utc=True).tz_convert("US/Eastern")
            if v
            else None
        )


class PolygonStockQuoteFetcher(
    Fetcher[PolygonStockQuoteQueryParams, List[PolygonStockQuoteData]]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonStockQuoteQueryParams:
        """Transform the query parameters."""
        return PolygonStockQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonStockQuoteQueryParams,
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
        max = 10000000
        if query.timestamp or query.limit >= 50000:
            max = query.limit if query.limit != 25 and query.limit < max else max
            query.limit = 50000
        results = []
        base_url = f"https://api.polygon.io/v3/quotes/{symbols[0]}"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol"]
        ).replace("_", ".")
        url = f"{base_url}?{query_str}&apiKey={api_key}"
        data = get_data_one(url, **kwargs)
        results = data["results"]
        results = map_exchanges(results)
        results = map_tape(results)
        records += len(results)
        if records == 50000 and "next_url" in data:
            while records < max and data["next_url"]:
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
    ) -> List[PolygonStockQuoteData]:
        """Transform the data."""
        return [PolygonStockQuoteData.model_validate(d) for d in data]
