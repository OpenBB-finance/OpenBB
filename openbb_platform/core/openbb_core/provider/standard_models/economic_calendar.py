"""Economic Calendar Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal, Optional, Union

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EconomicCalendarQueryParams(QueryParams):
    """Economic Calendar Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class EconomicCalendarData(Data):
    """Economic Calendar Data."""

    date: Optional[datetime] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    country: Optional[str] = Field(default=None, description="Country of event.")
    event: Optional[str] = Field(default=None, description="Event name.")
    reference: Optional[str] = Field(
        default=None,
        description="Abbreviated period for which released data refers to.",
    )
    source: Optional[str] = Field(default=None, description="Source of the data.")
    sourceurl: Optional[str] = Field(default=None, description="Source URL.")
    actual: Optional[Union[str, float]] = Field(
        default=None, description="Latest released value."
    )
    previous: Optional[Union[str, float]] = Field(
        default=None,
        description="Value for the previous period after the revision (if revision is applicable).",
    )
    consensus: Optional[Union[str, float]] = Field(
        default=None,
        description="Average forecast among a representative group of economists.",
    )
    forecast: Optional[Union[str, float]] = Field(
        default=None, description="Trading Economics projections"
    )
    url: Optional[str] = Field(default=None, description="Trading Economics URL")
    importance: Optional[Union[Literal[0, 1, 2, 3], str]] = Field(
        default=None, description="Importance of the event. 1-Low, 2-Medium, 3-High"
    )
    currency: Optional[str] = Field(default=None, description="Currency of the data.")
    unit: Optional[str] = Field(default=None, description="Unit of the data.")
