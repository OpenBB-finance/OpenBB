"""Polygon Equity Historical Price Model."""

# pylint: disable=unused-argument

import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
)
from pydantic import (
    Field,
    PositiveInt,
    PrivateAttr,
    model_validator,
)
from pytz import timezone

_warn = warnings.warn


class PolygonEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Polygon Equity Historical Price Query.

    Source: https://polygon.io/docs/stocks/getting-started
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: str = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    sort: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order of the data."
    )
    limit: PositiveInt = Field(
        default=49999, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    adjusted: bool = Field(
        default=True,
        description="Output time series is adjusted by historical split and dividend events.",
    )
    _multiplier: PositiveInt = PrivateAttr(default=None)
    _timespan: str = PrivateAttr(default=None)

    # pylint: disable=protected-access
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
    }

    transactions: Optional[PositiveInt] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
        alias="n",
    )


class PolygonEquityHistoricalFetcher(
    Fetcher[
        PolygonEquityHistoricalQueryParams,
        List[PolygonEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Polygon endpoints."""

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
        api_key = credentials.get("polygon_api_key") if credentials else ""

        urls = [
            (
                "https://api.polygon.io/v2/aggs/ticker/"
                f"{symbol.upper()}/range/{query._multiplier}/{query._timespan}/"
                f"{query.start_date}/{query.end_date}?adjusted={query.adjusted}"
                f"&sort={query.sort}&limit={query.limit}&apiKey={api_key}"
            )
            for symbol in query.symbol.split(",")
        ]

        async def callback(
            response: ClientResponse, session: ClientSession
        ) -> List[Dict]:
            data = await response.json()

            symbol = response.url.parts[4]
            next_url = data.get("next_url", None)
            results: list = data.get("results", [])

            while next_url:
                url = f"{next_url}&apiKey={api_key}"
                data = await session.get_json(url)
                results.extend(data.get("results", []))
                next_url = data.get("next_url", None)

            for r in results:
                r["t"] = datetime.fromtimestamp(
                    r["t"] / 1000, tz=timezone("America/New_York")
                )
                if query._timespan not in ["second", "minute", "hour"]:
                    r["t"] = r["t"].date()
                else:
                    r["t"] = r["t"].strftime("%Y-%m-%dT%H:%M:%S")
                if "," in query.symbol:
                    r["symbol"] = symbol

            if results == []:
                _warn(f"Symbol Error: No data found for {symbol}")

            return results

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: PolygonEquityHistoricalQueryParams,
        data: List[dict],
        **kwargs: Any,
    ) -> List[PolygonEquityHistoricalData]:
        """Transform the data from the Polygon endpoint."""
        if not data:
            raise EmptyDataError()
        return [PolygonEquityHistoricalData.model_validate(d) for d in data]
