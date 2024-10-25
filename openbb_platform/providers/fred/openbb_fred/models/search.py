"""FRED Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from dateutil import parser
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_search import (
    SearchData,
    SearchQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, NonNegativeInt, field_validator


class FredSearchQueryParams(SearchQueryParams):
    """FRED Search Query Params."""

    __alias_dict__ = {
        "query": "search_text",
    }
    __json_schema_extra__ = {
        "tag_names": {"multiple_items_allowed": True},
        "exclude_tag_names": {"multiple_items_allowed": True},
        "search_type": {
            "multiple_items_allowed": False,
            "choices": ["full_text", "series_id", "release"],
        },
        "order_by": {
            "multiple_items_allowed": False,
            "choices": [
                "search_rank",
                "series_id",
                "title",
                "units",
                "frequency",
                "seasonal_adjustment",
                "realtime_start",
                "realtime_end",
                "last_updated",
                "observation_start",
                "observation_end",
                "popularity",
                "group_popularity",
            ],
        },
    }

    search_type: Literal["full_text", "series_id", "release"] = Field(
        default="full_text",
        description="The type of search to perform. Automatically set to 'release' when a 'release_id' is provided.",
    )
    release_id: Optional[NonNegativeInt] = Field(
        default=None,
        description="A specific release ID to target.",
    )
    limit: Optional[NonNegativeInt] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " (1-1000)",
    )
    offset: Optional[NonNegativeInt] = Field(
        default=0,
        description="Offset the results in conjunction with limit."
        + " This parameter is ignored When search_type is 'release'.",
    )
    order_by: Literal[
        "search_rank",
        "series_id",
        "title",
        "units",
        "frequency",
        "seasonal_adjustment",
        "realtime_start",
        "realtime_end",
        "last_updated",
        "observation_start",
        "observation_end",
        "popularity",
        "group_popularity",
    ] = Field(
        default="observation_end",
        description="Order the results by a specific attribute. The default is 'observation_end'.",
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort the 'order_by' item in ascending or descending order. The default is 'desc'.",
    )
    filter_variable: Optional[Literal["frequency", "units", "seasonal_adjustment"]] = (
        Field(default=None, description="Filter by an attribute.")
    )
    filter_value: Optional[str] = Field(
        default=None,
        description="String value to filter the variable by.  Used in conjunction with filter_variable."
        + " This parameter is ignored when search_type is 'release'.",
    )
    tag_names: Optional[str] = Field(
        default=None,
        description="A semicolon delimited list of tag names that series match all of.  Example: 'japan;imports'"
        + " This parameter is ignored when search_type is 'release'.",
    )
    exclude_tag_names: Optional[str] = Field(
        default=None,
        description="A semicolon delimited list of tag names that series match none of.  Example: 'imports;services'."
        + " Requires that variable tag_names also be set to limit the number of matching series."
        + " This parameter is ignored when search_type is 'release'.",
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
        "series_id": "id",
    }

    @field_validator("last_updated", mode="before", check_fields=False)
    @classmethod
    def validate_last_updated(cls, v):
        """Validate last_updated."""
        return parser.parse(v) if v else None


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
        transformed_params = params.copy()

        if (
            transformed_params.get("release_id")
            and not transformed_params.get("search_type")
        ) or (
            not transformed_params.get("query")
            and not transformed_params.get("release_id")
            and not transformed_params.get("series_id")
        ):
            transformed_params["search_type"] = "release"
        elif (
            not transformed_params.get("query")
            and (
                transformed_params.get("search_type") in ["full_text", "series_id"]
                or not transformed_params.get("search_type")
            )
            and not transformed_params.get("series_id")
        ):
            raise OpenBBError(
                "A query is required for search_type 'full_text' or 'series_id'."
            )

        if transformed_params.get("exclude_tag_names") and not transformed_params.get(
            "tag_names"
        ):
            raise OpenBBError(
                "Field 'exclude_tag_names' requires 'tag_names' to be set."
            )

        return FredSearchQueryParams.model_validate(transformed_params)

    @staticmethod
    async def aextract_data(
        query: FredSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import (
            amake_request,
            get_querystring,
        )

        api_key = credentials.get("fred_api_key") if credentials else ""

        if query.series_id is not None:
            results: List = []

            async def get_one(_id: str):
                """Get data for one series."""
                data: Dict = {}
                url = f"https://api.stlouisfed.org/geofred/series/group?series_id={_id}&api_key={api_key}&file_type=json"
                response = await amake_request(url)
                data = response.get("series_group")  # type: ignore
                if data:
                    data.update({"series_id": _id})
                    results.append(data)

            await asyncio.gather(*[get_one(_id) for _id in query.series_id.split(",")])

            if results:
                return results
            raise EmptyDataError("No results found for the provided series_id(s).")

        if query.search_type == "release" and query.release_id is None:
            url = f"https://api.stlouisfed.org/fred/releases?api_key={api_key}&file_type=json"
            response = await amake_request(url)
            results = response.get("releases")  # type: ignore
            if results:
                return results
            raise OpenBBError(
                "Unexpected result while retrieving the list of releases from the FRED API."
            )

        url = (
            "https://api.stlouisfed.org/fred/release/series?"
            if query.release_id is not None
            else "https://api.stlouisfed.org/fred/series/search?"
        )

        exclude = (
            ["search_text", "limit"] if query.release_id is not None else ["limit"]
        )

        if query.release_id is not None and query.order_by == "search_rank":
            query.order_by = None  # type: ignore

        querystring = get_querystring(query.model_dump(), exclude).replace(" ", "%20")
        url = url + querystring + f"&file_type=json&api_key={api_key}"
        response = await amake_request(url)

        if isinstance(response, dict) and "error_code" in response:
            raise OpenBBError(
                f"FRED API Error -> Status Code: {response['error_code']}"
                f" -> {response.get('error_message', '')}"
            )

        if isinstance(response, dict) and "count" in response:
            results = response.get("seriess", [])
            return results
        raise OpenBBError(
            f"Unexpected response format. Expected a dictionary, got {type(response)}"
        )

    @staticmethod
    def transform_data(
        query: FredSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FredSearchData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame, Series

        if not data:
            raise EmptyDataError("The request was returned empty.")

        df = DataFrame(data)

        if query.search_type == "release" and query.release_id is None:
            df = df.rename(columns={"id": "release_id"})

        terms = [term.strip() for term in query.query.split(";")] if query.query else []
        tags = (
            [tag.strip() for tag in query.tag_names.split(";")]
            if query.tag_names and query.search_type != "series_id"
            else []
        )
        terms += tags

        if terms and query.search_type != "series_id":
            combined_mask = Series([True] * len(df))
            for term in terms:
                mask = df.apply(
                    lambda row, term=term: row.astype(str).str.contains(
                        term, case=False, regex=True, na=False
                    )
                ).any(axis=1)
                combined_mask &= mask

            matches = df[combined_mask]

            if matches.empty:
                raise EmptyDataError("No results found for the provided query.")

            df = matches

        df = df.replace({nan: None})

        if query.order_by in df.columns:
            df = df.sort_values(
                by=query.order_by, ascending=query.sort_order == "asc"
            ).reset_index(drop=True)

        if "series_group" in df.columns:
            df.series_group = df.series_group.astype(str)

        if "release_id" in df.columns:
            df.release_id = df.release_id.astype(str)

        if query.limit is not None and len(df) > query.limit:
            df = df.iloc[: query.limit]

        records = df.to_dict(orient="records")

        return [FredSearchData.model_validate(r) for r in records]
