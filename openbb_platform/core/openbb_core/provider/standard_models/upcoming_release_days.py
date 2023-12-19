"""Upcoming Release Days Standard Model."""

from datetime import date as dateType

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class UpcomingReleaseDaysQueryParams(QueryParams):
    """Upcoming Release Days Query."""


class UpcomingReleaseDaysData(Data):
    """Upcoming Release Days Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="The full name of the asset.")
    exchange: str = Field(description="The exchange the asset is traded on.")
    release_time_type: str = Field(description="The type of release time.")
    release_date: dateType = Field(description="The date of the release.")
