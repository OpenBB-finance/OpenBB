"""ChartLibrary Pattern Similarity Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.chart_pattern_similarity import (
    ChartPatternSimilarityData,
    ChartPatternSimilarityQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field, PositiveInt, field_validator

CHARTLIBRARY_SEARCH_URL = "https://chartlibrary.io/api/v1/search/text"
SUPPORTED_TIMEFRAMES = ("auto", "rth", "premarket", "rth_3d", "rth_5d", "rth_10d")


class ChartLibraryPatternSimilarityQueryParams(ChartPatternSimilarityQueryParams):
    """ChartLibrary Pattern Similarity Query."""

    __json_schema_extra__ = {"timeframe": {"choices": list(SUPPORTED_TIMEFRAMES)}}

    limit: PositiveInt | None = Field(
        default=None,
        le=50,
        description="Maximum number of similar historical patterns to return.",
    )

    @field_validator("timeframe", mode="before", check_fields=False)
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Validate ChartLibrary search timeframe values."""
        timeframe = str(v).lower()
        if timeframe not in SUPPORTED_TIMEFRAMES:
            supported = ", ".join(SUPPORTED_TIMEFRAMES)
            raise ValueError(f"ChartLibrary timeframe must be one of: {supported}.")
        return timeframe


class ChartLibraryPatternSimilarityData(ChartPatternSimilarityData):
    """ChartLibrary Pattern Similarity Data."""


def _first_available(data: dict, *keys: str) -> Any:
    """Return the first available value from a set of possible provider keys."""
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def _error_message(data: Any, status_code: int) -> str:
    """Return a provider error message from a response payload."""
    if isinstance(data, dict):
        for key in ("message", "detail", "error"):
            if data.get(key):
                return str(data[key])
    return f"ChartLibrary request failed with status {status_code}."


def _extract_results(response: dict | list[dict]) -> list[dict]:
    """Extract search results from supported ChartLibrary response shapes."""
    if isinstance(response, list):
        return response

    if isinstance(response, dict):
        results = response.get("results")
        if results is None:
            results = response.get("matches")
        if isinstance(results, list):
            return results

    return []


class ChartLibraryPatternSimilarityFetcher(
    Fetcher[
        ChartLibraryPatternSimilarityQueryParams,
        list[ChartLibraryPatternSimilarityData],
    ]
):
    """Transform, extract, and transform ChartLibrary pattern similarity data."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> ChartLibraryPatternSimilarityQueryParams:
        """Transform the query params."""
        return ChartLibraryPatternSimilarityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ChartLibraryPatternSimilarityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return raw data from the ChartLibrary search endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        api_key = credentials.get("chartlibrary_api_key") if credentials else ""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "query": f"{query.symbol} {query.date.isoformat()}",
            "timeframe": query.timeframe,
            "top_n": query.limit or 10,
        }

        async def response_callback(response, _):
            """Handle ChartLibrary API responses."""
            data = await response.json()

            if response.status >= 400:
                message = _error_message(data, response.status)
                if response.status in [401, 403] or "api key" in message.lower():
                    raise UnauthorizedError(
                        f"Unauthorized ChartLibrary request -> {message}"
                    )
                raise OpenBBError(message)

            return data

        response = await amake_request(
            CHARTLIBRARY_SEARCH_URL,
            method="POST",
            headers=headers,
            json=payload,
            response_callback=response_callback,
            **kwargs,
        )

        results = _extract_results(response)

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: ChartLibraryPatternSimilarityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ChartLibraryPatternSimilarityData]:
        """Return transformed ChartLibrary pattern similarity data."""
        results: list[ChartLibraryPatternSimilarityData] = []

        for index, item in enumerate(data, start=1):
            record = item.copy()
            record["symbol"] = _first_available(record, "symbol", "ticker")
            record["date"] = _first_available(record, "date", "match_date")
            record["rank"] = (
                _first_available(
                    record,
                    "rank",
                    "similarity_rank",
                    "match_rank",
                )
                or index
            )
            record["distance"] = _first_available(
                record,
                "distance",
                "distance_score",
                "embedding_distance",
                "similarity",
            )
            record["similarity_score"] = _first_available(
                record,
                "similarity_score",
                "score",
                "match_score",
            )
            record["timeframe"] = record.get("timeframe") or query.timeframe
            record["forward_return_1d"] = _first_available(
                record,
                "forward_return_1d",
                "return_1d",
                "fwd_return_1d",
            )
            record["forward_return_3d"] = _first_available(
                record,
                "forward_return_3d",
                "return_3d",
                "fwd_return_3d",
            )
            record["forward_return_5d"] = _first_available(
                record,
                "forward_return_5d",
                "return_5d",
                "fwd_return_5d",
            )
            record["forward_return_10d"] = _first_available(
                record,
                "forward_return_10d",
                "return_10d",
                "fwd_return_10d",
            )

            results.append(ChartLibraryPatternSimilarityData.model_validate(record))

        return results
