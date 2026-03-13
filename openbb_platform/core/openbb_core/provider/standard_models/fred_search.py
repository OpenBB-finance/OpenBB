"""FRED Search Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SearchQueryParams(QueryParams):
    """FRED Search Query Params."""

    query: str | None = Field(default=None, description="The search word(s).")


class SearchData(Data):
    """FRED Search Data."""

    release_id: str | None = Field(
        default=None,
        description="The release ID for queries.",
    )
    series_id: str | None = Field(
        default=None,
        description="The series ID for the item in the release.",
    )
    series_group: str | None = Field(
        default=None,
        description="The series group ID of the series. This value is used to query for regional data.",
    )
    region_type: str | None = Field(
        default=None,
        description="The region type of the series.",
    )
    name: str | None = Field(
        default=None,
        description="The name of the release.",
    )
    title: str | None = Field(
        default=None,
        description="The title of the series.",
    )
    observation_start: dateType | None = Field(
        default=None, description="The date of the first observation in the series."
    )
    observation_end: dateType | None = Field(
        default=None, description="The date of the last observation in the series."
    )
    frequency: str | None = Field(
        default=None,
        description="The frequency of the data.",
    )
    frequency_short: str | None = Field(
        default=None,
        description="Short form of the data frequency.",
    )
    units: str | None = Field(
        default=None,
        description="The units of the data.",
    )
    units_short: str | None = Field(
        default=None,
        description="Short form of the data units.",
    )
    seasonal_adjustment: str | None = Field(
        default=None,
        description="The seasonal adjustment of the data.",
    )
    seasonal_adjustment_short: str | None = Field(
        default=None,
        description="Short form of the data seasonal adjustment.",
    )
    last_updated: datetime | None = Field(
        default=None,
        description="The datetime of the last update to the data.",
    )
    popularity: int | None = Field(
        default=None,
        description="Popularity of the series",
    )
    group_popularity: int | None = Field(
        default=None,
        description="Group popularity of the release",
    )
    realtime_start: dateType | None = Field(
        default=None,
        description="The realtime start date of the series.",
    )
    realtime_end: dateType | None = Field(
        default=None,
        description="The realtime end date of the series.",
    )
    notes: str | None = Field(default=None, description="Description of the release.")
    press_release: bool | None = Field(
        description="If the release is a press release.",
        default=None,
    )
    url: str | None = Field(default=None, description="URL to the release.")
