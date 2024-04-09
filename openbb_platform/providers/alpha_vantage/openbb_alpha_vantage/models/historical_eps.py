"""AlphaVantage Historical EPS Model."""

# pylint: disable=unused-argument

import warnings
from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_eps import (
    HistoricalEpsData,
    HistoricalEpsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
)
from pydantic import Field, field_validator

_warn = warnings.warn


class AlphaVantageHistoricalEpsQueryParams(HistoricalEpsQueryParams):
    """
    AlphaVantage Historical EPS Query Params.

    Source: https://www.alphavantage.co/documentation/#earnings
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    period: Literal["annual", "quarter"] = Field(
        default="quarter", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[int] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class AlphaVantageHistoricalEpsData(HistoricalEpsData):
    """AlphaVantage Historical EPS Data."""

    __alias_dict__ = {
        "date": "fiscalDateEnding",
        "eps_actual": "reportedEPS",
        "eps_estimated": "estimatedEPS",
        "surprise_percent": "surprisePercentage",
        "reported_date": "reportedDate",
    }

    surprise: Optional[float] = Field(
        default=None,
        description="Surprise in EPS (Actual - Estimated).",
    )
    surprise_percent: Optional[Union[float, str]] = Field(
        default=None,
        description="EPS surprise as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    reported_date: Optional[dateType] = Field(
        default=None,
        description="Date of the earnings report.",
    )

    @field_validator(
        "eps_estimated",
        "eps_actual",
        "surprise",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_null(cls, v):
        """Clean None returned as a string."""
        return None if str(v).strip() == "None" or str(v) == "0" else v

    @field_validator("surprise_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        if isinstance(v, str) and v == "None" or str(v) == "0":
            return None
        return float(v) / 100


class AVHistoricalEpsFetcher(
    Fetcher[AlphaVantageHistoricalEpsQueryParams, List[AlphaVantageHistoricalEpsData]]
):
    """AlphaVantage Historical EPS Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AlphaVantageHistoricalEpsQueryParams:
        """Transform the query params."""
        return AlphaVantageHistoricalEpsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AlphaVantageHistoricalEpsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AlphaVantage endpoint."""

        api_key = credentials.get("alpha_vantage_api_key") if credentials else ""

        BASE_URL = "https://www.alphavantage.co/query?function=EARNINGS&"

        # We are allowing multiple symbols to be passed in the query, so we need to handle that.
        symbols = query.symbol.split(",")

        urls = [f"{BASE_URL}symbol={symbol}&apikey={api_key}" for symbol in symbols]

        results = []

        # We need to make a custom callback function for this async request.
        async def response_callback(response: ClientResponse, _: ClientSession):
            """Response callback function."""
            symbol = response.url.query.get("symbol", None)
            data = await response.json()
            target = (
                "annualEarnings" if query.period == "annual" else "quarterlyEarnings"
            )
            result = []
            # If data is returned, append it to the results list.
            if data:
                result = [
                    {
                        "symbol": symbol,
                        **d,
                    }
                    for d in data.get(target, [])  # type: ignore
                ]
                if query.limit is not None:
                    results.extend(result[: query.limit])
                else:
                    results.extend(result)

            # If no data is returned, raise a warning and move on to the next symbol.
            if not data:
                _warn(f"Symbol Error: No data found for {symbol}")

        await amake_requests(urls, response_callback, **kwargs)  # type: ignore

        return results

    @staticmethod
    def transform_data(
        query: AlphaVantageHistoricalEpsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AlphaVantageHistoricalEpsData]:
        """Transform the raw data into the standard model."""
        if not data:
            raise EmptyDataError("No data found.")
        return [AlphaVantageHistoricalEpsData.model_validate(d) for d in data]
