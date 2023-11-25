"""FRED Releases Series Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_releases_series import (
    EconomicReleasesSeriesData,
    EconomicReleasesSeriesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import async_make_request, get_querystring
from pydantic import Field, NonNegativeInt


class FredReleasesSeriesQueryParams(EconomicReleasesSeriesQueryParams):
    """FRED Releases Series Query Params."""

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
        description="A semicolon delimited list of tag names that series match none of.  Example: 'imports;services'",
    )


class FredReleasesSeriesData(EconomicReleasesSeriesData):
    """FRED Releases Series Data."""

    __alias_dict__ = {"series_id": "id"}

    popularity: Optional[int] = Field(
        default=None,
        description="Popularity of the series",
    )
    group_popularity: Optional[int] = Field(
        default=None,
        description="Group popularity of the release",
    )


class FredEconomicReleasesSeriesFetcher(
    Fetcher[
        FredReleasesSeriesQueryParams,
        List[FredReleasesSeriesData],
    ]
):
    """FRED Economic Releases Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredReleasesSeriesQueryParams:
        """Transform query."""
        return FredReleasesSeriesQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: FredReleasesSeriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""

        api_key = credentials.get("fred_api_key") if credentials else ""
        base_url = "https://api.stlouisfed.org/fred/release/series?"
        querystring = get_querystring(query.model_dump(), [])
        url = base_url + querystring + f"&file_type=json&api_key={api_key}"

        response = await async_make_request(url, timeout=5, **kwargs)

        return response.get("seriess")  #  type: ignore[return-value, union-attr]

    @staticmethod
    def transform_data(
        query: FredReleasesSeriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FredReleasesSeriesData]:
        """Transform data."""

        [d.pop("realtime_start") for d in data]
        [d.pop("realtime_end") for d in data]

        return [FredReleasesSeriesData.model_validate(d) for d in data]
