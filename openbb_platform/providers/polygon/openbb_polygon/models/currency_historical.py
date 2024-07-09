"""Polygon Currency Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import (
    Field,
    PositiveInt,
    PrivateAttr,
    model_validator,
)


class PolygonCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Polygon Currency Historical Price Query.

    Source: https://polygon.io/docs/forex/get_v2_aggs_ticker__forexticker__range__multiplier___timespan___from___to
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    interval: str = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", "")
        + " The numeric portion of the interval can be any positive integer."
        + " The letter portion can be one of the following: s, m, h, d, W, M, Q, Y",
    )
    sort: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort order of the data."
        + " This impacts the results in combination with the 'limit' parameter."
        + " The results are always returned in ascending order by date.",
    )
    limit: PositiveInt = Field(
        default=49999, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    _multiplier: PositiveInt = PrivateAttr(default=None)
    _timespan: str = PrivateAttr(default=None)

    @model_validator(mode="after")
    @classmethod
    def get_api_interval_params(cls, values: "PolygonCurrencyHistoricalQueryParams"):
        """Get the multiplier and timespan parameters for the Polygon API."""
        intervals = {
            "s": "second",
            "m": "minute",
            "h": "hour",
            "d": "day",
            "W": "week",
            "M": "month",
            "Q": "quarter",
            "Y": "year",
        }

        values._multiplier = int(  # pylint: disable=protected-access
            values.interval[:-1]
        )
        values._timespan = intervals[  # pylint: disable=protected-access
            values.interval[-1]
        ]

        return values


class PolygonCurrencyHistoricalData(CurrencyHistoricalData):
    """Polygon Currency Historical Price Data."""

    __alias_dict__ = {
        "date": "t",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
        "vwap": "vw",
        "transactions": "n",
    }

    transactions: Optional[PositiveInt] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
    )


class PolygonCurrencyHistoricalFetcher(
    Fetcher[
        PolygonCurrencyHistoricalQueryParams,
        List[PolygonCurrencyHistoricalData],
    ]
):
    """Polygon Currency Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCurrencyHistoricalQueryParams:
        """Transform the query."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return PolygonCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: PolygonCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the polygon endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import (
            amake_requests,
            safe_fromtimestamp,
        )
        from pytz import timezone

        api_key = credentials.get("polygon_api_key") if credentials else ""

        urls = [
            (  # pylint: disable=protected-access
                "https://api.polygon.io/v2/aggs/ticker/"
                f"C:{symbol.upper()}/range/{query._multiplier}/{query._timespan}/"
                f"{query.start_date}/{query.end_date}?"
                f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
            )
            for symbol in query.symbol.split(",")
        ]
        results: List = []

        async def callback(response, session):
            """Return the data from the response."""
            data = await response.json()

            symbol = response.url.parts[4]
            next_url = data.get("next_url", None)  # type: ignore
            results.extend(data.get("results", []))  # type: ignore
            while next_url:
                url = f"{next_url}&apiKey={api_key}"
                data = await session.get_json(url)
                results.extend(data.get("results", []))  # type: ignore
                next_url = data.get("next_url", None)  # type: ignore

            for r in results:
                v = r.get("t") / 1000  # milliseconds to seconds
                r["t"] = safe_fromtimestamp(v, tz=timezone.utc)  # type: ignore
                if query._timespan not in [  # pylint: disable=protected-access
                    "second",
                    "minute",
                    "hour",
                ]:
                    r["t"] = r["t"].date().strftime("%Y-%m-%d")
                else:
                    r["t"] = r["t"].strftime("%Y-%m-%dT%H:%M:%S%z")
                if "," in query.symbol:
                    r["symbol"] = symbol

            if not results:
                warn(f"Symbol Error: No data found for {symbol.replace('C:', '')}")

        await amake_requests(urls=urls, response_callback=callback, **kwargs)

        return results

    @staticmethod
    def transform_data(
        query: PolygonCurrencyHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[PolygonCurrencyHistoricalData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError()
        return [PolygonCurrencyHistoricalData.model_validate(d) for d in data]
