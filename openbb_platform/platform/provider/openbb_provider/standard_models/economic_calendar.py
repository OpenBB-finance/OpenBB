"""Economic Calendar Standard Model"""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Union

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class EconomicCalendarQueryParams(QueryParams):
    """Economic calendar Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    # TODO: Probably want to figure out the list we can use.
    country: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Country of the event",
    )


class EconomicCalendarData(Data):
    """Economic calendar Data."""

    date: Optional[datetime] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    country: Optional[str] = Field(default=None, description="Country of event.")
    event: Optional[str] = Field(default=None, description="Event name.")
    actual: Optional[str] = Field(default=None, description="Latest released value.")
    previous: Optional[str] = Field(
        default=None,
        description="Value for the previous period after the revision (if revision is applicable).",
    )
    consensus: Optional[str] = Field(
        default=None,
        description="Average forecast among a representative group of economists.",
    )
