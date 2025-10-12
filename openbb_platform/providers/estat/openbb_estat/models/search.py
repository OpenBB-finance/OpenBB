"""e-Stat Search Model.

ATTRIBUTION: This service uses API functions from e-Stat,
however its contents are not guaranteed by government.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.estat_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_estat.utils.helpers import handle_estat_error


class EstatSearchQueryParams(SearchQueryParams):
    """e-Stat Search Query Parameters."""

    limit: int = Field(
        default=100,
        description="Number of results to return. Default is 100. e-Stat API default is 10,000 if not specified.",
        le=100000,
        ge=1,
    )
    start_position: Optional[int] = Field(
        default=None,
        description="Starting position for pagination (starts at 1). Use this with limit to paginate through results.",
        ge=1,
    )
    updated_date: Optional[str] = Field(
        default=None,
        description="Filter by update date in YYYY-MM-DD format.",
    )


class EstatSearchData(SearchData):
    """e-Stat Search Data."""

    @field_validator("survey_date", "open_date", mode="before", check_fields=False)
    @classmethod
    def validate_dates(cls, v):
        """Validate and parse dates."""
        if not v:
            return None
        try:
            # e-Stat returns dates as YYYY-MM-DD strings
            return datetime.strptime(v, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None


class EstatSearchFetcher(Fetcher[EstatSearchQueryParams, List[EstatSearchData]]):
    """e-Stat Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EstatSearchQueryParams:
        """Transform query parameters."""
        return EstatSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EstatSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from e-Stat getStatsList API."""
        # pylint: disable=import-outside-toplevel
        import aiohttp

        api_key = credentials.get("api_key") if credentials else ""

        # Build API parameters
        params = {
            "appId": api_key,
            "lang": "E",  # Request English where available
            "limit": query.limit,
        }

        if query.query:
            params["searchWord"] = query.query

        if query.start_position:
            params["startPosition"] = query.start_position

        if query.updated_date:
            # Convert YYYY-MM-DD to YYYY-MM-DD format (e-Stat accepts this)
            params["updatedDate"] = query.updated_date

        url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(
                        f"e-Stat API request failed with status {response.status}"
                    )

                data = await response.json()

                if "GET_STATS_LIST" not in data:
                    raise EmptyDataError("No data returned from e-Stat API")

                stats_list = data["GET_STATS_LIST"]

                # Check for API errors
                if "RESULT" in stats_list:
                    result = stats_list["RESULT"]
                    status = result.get("STATUS", -1)
                    if status != 0:
                        error_msg = result.get("ERROR_MSG", "Unknown error")
                        formatted_error = handle_estat_error(status, error_msg)
                        raise EmptyDataError(formatted_error)

                # Extract dataset list
                if (
                    "DATALIST_INF" not in stats_list
                    or "LIST_INF" not in stats_list["DATALIST_INF"]
                ):
                    raise EmptyDataError("No datasets found")

                datasets = stats_list["DATALIST_INF"]["LIST_INF"]
                # Ensure we return a list even if single result
                datasets_list = datasets if isinstance(datasets, list) else [datasets]

                # Store pagination info for transform_data to use
                # Attach as a special field that won't interfere with data parsing
                pagination_info = {
                    "_pagination": {
                        "next_key": stats_list.get("NEXT_KEY"),
                        "number": stats_list.get("DATALIST_INF", {}).get("NUMBER"),
                        "result_inf": stats_list.get("DATALIST_INF", {}).get("RESULT_INF", {}),
                    }
                }
                # Attach pagination to first element if list is not empty
                if datasets_list:
                    datasets_list[0]["_pagination"] = pagination_info["_pagination"]

                return datasets_list

    @staticmethod
    def transform_data(
        query: EstatSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> AnnotatedResult[List[EstatSearchData]]:
        """Transform the data and include attribution metadata."""
        results = []
        pagination_info = None

        for item in data:
            # Extract pagination info if present (attached to first item)
            if "_pagination" in item and pagination_info is None:
                pagination_info = item.pop("_pagination")
                # Continue processing this item as a dataset

            # Flatten nested JSON structure from e-Stat API
            # API returns nested structures like {"STAT_NAME": {"@id": "...", "$": "..."}}
            flat_item = {
                "dataset_id": item.get("STAT_NAME", {}).get("@id", ""),
                "title": item.get("STAT_NAME", {}).get("$", ""),
                "stats_code": item.get("STATISTICS_NAME", {}).get("@code", ""),
                "statistics_name": item.get("STATISTICS_NAME", {}).get("$", ""),
                "gov_org": item.get("GOV_ORG", {}).get("$", ""),
                "survey_date": item.get("SURVEY_DATE"),
                "open_date": item.get("OPEN_DATE"),
                "small_area": item.get("SMALL_AREA"),
            }

            # Skip entries without dataset_id
            if flat_item["dataset_id"]:
                results.append(EstatSearchData.model_validate(flat_item))

        if not results:
            raise EmptyDataError("No valid datasets found in search results")

        # Include attribution and metadata as specified in the requirements
        metadata = {
            "attribution": "This service uses API functions from e-Stat, "
            "however its contents are not guaranteed by government.",
            "source": "https://www.e-stat.go.jp/",
            "api_version": "3.0",
            "total_results": len(results),
        }

        # Add pagination info if available
        if pagination_info:
            if pagination_info.get("next_key"):
                metadata["next_start_position"] = pagination_info["next_key"]
                metadata["has_more"] = True
            else:
                metadata["has_more"] = False

            if pagination_info.get("number"):
                metadata["total_available"] = pagination_info["number"]

        return AnnotatedResult(result=results, metadata=metadata)
