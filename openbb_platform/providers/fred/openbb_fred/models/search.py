"""FRED Releases Search Model."""

from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import async_make_request, get_querystring
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


class FredSearchData(SearchData):
    """FRED Search Data."""

    __alias_dict__ = {"url": "link"}

    popularity: Optional[int] = Field(
        default=None,
        description="Popularity of the series",
    )
    group_popularity: Optional[int] = Field(
        default=None,
        description="Group popularity of the release",
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
    async def extract_data(
        query: FredSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""

        api_key = credentials.get("fred_api_key") if credentials else ""

        if query.is_release is True:
            url = f"https://api.stlouisfed.org/fred/releases?api_key={api_key}&file_type=json"

            response = await async_make_request(url, timeout=5, **kwargs)

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
        response = await async_make_request(url, timeout=5, **kwargs)

        return response.get("seriess")  #  type: ignore[return-value, union-attr]

    @staticmethod
    def transform_data(
        query: FredSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FredSearchData]:
        """Transform data."""

        df = pd.DataFrame()
        if data is not None:
            [d.pop("realtime_start") for d in data]
            [d.pop("realtime_end") for d in data]
            df = (
                pd.DataFrame.from_records(data)
                .fillna("N/A")
                .replace("N/A", None)
                .rename(
                    columns={"id": "release_id"}
                    if query.is_release is True
                    else {"id": "series_id"}
                )
            )
            target = "name" if query.is_release is True else "title"
            if query.query is not None:
                df = df[
                    df[target].str.contains(query.query, case=False)
                    | df["notes"].str.contains(query.query, case=False)
                ]

        return [FredSearchData.model_validate(d) for d in df.to_dict("records")]
