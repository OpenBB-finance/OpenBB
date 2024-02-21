"""FRED Search Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from pydantic import Field, NonNegativeInt


class FredSearchQueryParams(SearchQueryParams):
    """FRED Search Query Params."""

    __alias_dict__ = {
        "query": "search_text",
    }
    is_release: Optional[bool] = Field(
        default=False,
        description="Is release?  If True, other search filter variables are ignored."
        + " If no query text or release_id is supplied, this defaults to True.",
    )
    release_id: Optional[Union[str, int]] = Field(
        default=None,
        description="A specific release ID to target.",
    )
    limit: Optional[int] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " (1-1000)",
    )
    offset: Optional[NonNegativeInt] = Field(
        default=0,
        description="Offset the results in conjunction with limit.",
    )
    filter_variable: Literal[None, "frequency", "units", "seasonal_adjustment"] = Field(
        default=None, description="Filter by an attribute."
    )
    filter_value: Optional[str] = Field(
        default=None,
        description="String value to filter the variable by.  Used in conjunction with filter_variable.",
    )
    tag_names: Optional[str] = Field(
        default=None,
        description="A semicolon delimited list of tag names that series match all of.  Example: 'japan;imports'",
    )
    exclude_tag_names: Optional[str] = Field(
        default=None,
        description="A semicolon delimited list of tag names that series match none of.  Example: 'imports;services'."
        + " Requires that variable tag_names also be set to limit the number of matching series.",
    )
    series_id: Optional[str] = Field(
        default=None,
        description="A FRED Series ID to return series group information for."
        + " This returns the required information to query for regional data."
        + " Not all series that are in FRED have geographical data."
        + " Entering a value for series_id will override all other parameters."
        + " Multiple series_ids can be separated by commas.",
    )


class FredSearchData(SearchData):
    """FRED Search Data."""

    __alias_dict__ = {
        "url": "link",
        "observation_start": "min_date",
        "observation_end": "max_date",
        "seasonal_adjustment": "season",
    }
    popularity: Optional[int] = Field(
        default=None,
        description="Popularity of the series",
    )
    group_popularity: Optional[int] = Field(
        default=None,
        description="Group popularity of the release",
    )
    region_type: Optional[str] = Field(
        default=None,
        description="The region type of the series.",
    )
    series_group: Optional[Union[str, int]] = Field(
        default=None,
        description="The series group ID of the series. This value is used to query for regional data.",
    )


class FredSearchFetcher(
    Fetcher[
        FredSearchQueryParams,
        List[FredSearchData],
    ]
):
    """FRED Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredSearchQueryParams:
        """Transform query."""
        transformed_params = FredSearchQueryParams(**params)
        if transformed_params.query is None and transformed_params.release_id is None:
            transformed_params.is_release = True

        return transformed_params

    @staticmethod
    async def aextract_data(
        query: FredSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""
        api_key = credentials.get("fred_api_key") if credentials else ""

        if query.series_id is not None:
            results = []

            async def get_one(_id: str):
                data = {}
                url = f"https://api.stlouisfed.org/geofred/series/group?series_id={_id}&api_key={api_key}&file_type=json"
                response = await amake_request(url)
                data = response.get("series_group")  # type: ignore
                if data:
                    data.update({"series_id": _id})
                    results.append(data)

            tasks = [get_one(_id) for _id in query.series_id.split(",")]
            await asyncio.gather(*tasks)

            if results:
                return results

        if query.is_release is True:
            url = f"https://api.stlouisfed.org/fred/releases?api_key={api_key}&file_type=json"

            response = await amake_request(url, timeout=5, **kwargs)

            return response.get("releases")  #  type: ignore[return-value, union-attr]

        url = (
            "https://api.stlouisfed.org/fred/release/series?"
            if query.release_id is not None
            else "https://api.stlouisfed.org/fred/series/search?"
        )

        exclude = (
            ["is_release", "search_text"]
            if query.release_id is not None
            else ["is_release"]
        )

        querystring = get_querystring(query.model_dump(), exclude).replace(" ", "+")

        url = url + querystring + f"&file_type=json&api_key={api_key}"
        response = await amake_request(url, timeout=5, **kwargs)

        return response.get("seriess")  #  type: ignore[return-value, union-attr]

    @staticmethod
    def transform_data(
        query: FredSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FredSearchData]:
        """Transform data."""
        if query.series_id is None:
            for observation in data:
                id_column_name = (
                    "release_id" if query.is_release is True else "series_id"
                )
                observation[id_column_name] = observation.pop("id")
                observation.pop("realtime_start", None)
                observation.pop("realtime_end", None)
        return [FredSearchData.model_validate(d) for d in data]
