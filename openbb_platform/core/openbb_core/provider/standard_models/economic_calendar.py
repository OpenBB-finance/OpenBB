"""Economic Calendar Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class EconomicCalendarQueryParams(QueryParams):
    """Economic Calendar Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class EconomicCalendarData(Data):
    """Economic Calendar Data."""

    date: datetime | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    country: str | None = Field(default=None, description="Country of event.")
    category: str | None = Field(default=None, description="Category of event.")
    event: str | None = Field(default=None, description="Event name.")
    importance: str | None = Field(
        default=None, description="The importance level for the event."
    )
    source: str | None = Field(default=None, description="Source of the data.")
    currency: str | None = Field(default=None, description="Currency of the data.")
    unit: str | None = Field(default=None, description="Unit of the data.")
    consensus: str | float | None = Field(
        default=None,
        description="Average forecast among a representative group of economists.",
    )
    previous: str | float | None = Field(
        default=None,
        description="Value for the previous period after the revision (if revision is applicable).",
    )
    revised: str | float | None = Field(
        default=None,
        description="Revised previous value, if applicable.",
    )
    actual: str | float | None = Field(
        default=None, description="Latest released value."
    )
