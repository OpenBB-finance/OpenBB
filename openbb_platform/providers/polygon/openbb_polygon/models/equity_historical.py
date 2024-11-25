"""Polygon Equity Historical Price Model."""

# pylint: disable=unused-argument,protected-access

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import (
    Field,
    PositiveInt,
    PrivateAttr,
    model_validator,
)


class PolygonEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Polygon Equity Historical Price Query.

    Source: https://polygon.io/docs/stocks/getting-started
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    interval: str = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", "")
        + " The numeric portion of the interval can be any positive integer."
        + " The letter portion can be one of the following: s, m, h, d, W, M, Q, Y",
    )
    adjustment: Literal["splits_only", "unadjusted"] = Field(
        default="splits_only",
        description="The adjustment factor to apply. Default is splits only.",
    )
    extended_hours: bool = Field(
        default=False,
        description="Include Pre and Post market data.",
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
    def get_api_interval_params(cls, values: "PolygonEquityHistoricalQueryParams"):
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

        values._multiplier = int(values.interval[:-1])
        values._timespan = intervals[values.interval[-1]]

        return values


class PolygonEquityHistoricalData(EquityHistoricalData):
    """Polygon Equity Historical Price Data."""

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


class PolygonEquityHistoricalFetcher(
    Fetcher[
        PolygonEquityHistoricalQueryParams,
        List[PolygonEquityHistoricalData],
    ]
):
    """Polygon Equity Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonEquityHistoricalQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return PolygonEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(  # pylint: disable=protected-access
        query: PolygonEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Polygon endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import (  # noqa
            ClientResponse,
            ClientSession,
            amake_requests,
            safe_fromtimestamp,
        )
        from pytz import timezone

        api_key = credentials.get("polygon_api_key") if credentials else ""
        adjustment = query.adjustment == "splits_only"
        urls = [
            (
                "https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{query._multiplier}/{query._timespan}/"
                f"{query.start_date}/{query.end_date}?adjusted={adjustment}"
                f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
            )
            for symbol in query.symbol.split(",")
        ]

        async def callback(
            response: ClientResponse, session: ClientSession
        ) -> List[Dict]:
            data = await response.json()

            symbol = response.url.parts[4]
            next_url = data.get("next_url", None)  # type: ignore
            results: list = data.get("results", [])  # type: ignore

            while next_url:
                url = f"{next_url}&apiKey={api_key}"
                data = await session.get_json(url)
                results.extend(data.get("results", []))  # type: ignore
                next_url = data.get("next_url", None)  # type: ignore

            for r in results:
                v = r["t"] / 1000  # milliseconds to seconds
                r["t"] = safe_fromtimestamp(v, tz=timezone("America/New_York"))  # type: ignore[arg-type]
                if query._timespan not in ["second", "minute", "hour"]:
                    r["t"] = r["t"].date().strftime("%Y-%m-%d")
                else:
                    r["t"] = r["t"].strftime("%Y-%m-%dT%H:%M:%S%z")
                if "," in query.symbol:
                    r["symbol"] = symbol

            if results == []:
                warn(f"Symbol Error: No data found for {symbol}")

            return results

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: PolygonEquityHistoricalQueryParams,
        data: List[dict],
        **kwargs: Any,
    ) -> List[PolygonEquityHistoricalData]:
        """Transform the data from the Polygon endpoint."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        if not data:
            raise EmptyDataError()
        if query.extended_hours is True or query._timespan not in [
            "second",
            "minute",
            "hour",
        ]:
            return [
                PolygonEquityHistoricalData.model_validate(d)
                for d in sorted(data, key=lambda x: x["t"], reverse=False)
            ]

        return [
            PolygonEquityHistoricalData.model_validate(d)
            for d in sorted(data, key=lambda x: x["t"], reverse=False)
            if to_datetime(d["t"]).time()
            >= datetime.strptime("09:30:00", "%H:%M:%S").time()
            and to_datetime(d["t"]).time()
            <= datetime.strptime("16:00:00", "%H:%M:%S").time()
        ]
