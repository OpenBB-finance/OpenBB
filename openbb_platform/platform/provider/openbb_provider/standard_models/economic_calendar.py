"""Economic Calendar Standard Model"""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Literal, Optional, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


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
    importance: Literal["Low", "Medium", "High"] = Field(
        default=None,
        description="Importance of the event.",
    )
    group: Literal[
        "interest rate",
        "inflation",
        "bonds",
        "consumer",
        "gdp",
        "government",
        "housing",
        "labour",
        "markets",
        "money",
        "prices",
        "trade",
        "business",
    ] = Field(default=None, description="Grouping of events")
    # TODO: Probably want to figure out the list we can use.
    country: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Country of the event",
    )

    @field_validator("importance")
    @classmethod
    def importance_to_number(cls, v):
        string_to_value = {"Low": 1, "Medium": 2, "High": 3}
        return string_to_value[v]


class EconomicCalendarData(Data):
    """Economic calendar Data."""

    date: Optional[datetime] = Field(
        default=None, description="Date and time of event."
    )
    country: Optional[str] = Field(default=None, description="Country of event.")
    category: Optional[str] = Field(default=None, description="Category of event.")
    event: Optional[str] = Field(default=None, description="Event name.")
    reference: Optional[str] = Field(
        default=None,
        description="Abbreviated period for which released data refers to.",
    )
    source: Optional[str] = Field(default=None, description="Source of the data.")
    sourceurl: Optional[str] = Field(default=None, description="Source URL.")
    actual: Optional[str] = Field(default=None, description="Latest released value.")
    previous: Optional[str] = Field(
        default=None,
        description="Value for the previous period after the revision (if revision is applicable).",
    )
    consensus: Optional[str] = Field(
        default=None,
        description="Average forecast among a representative group of economists.",
    )
    forecast: Optional[str] = Field(
        default=None, description="Trading Economics projections"
    )
    url: Optional[str] = Field(default=None, description="Trading Economics URL")
    importance: Optional[Literal[0, 1, 2, 3]] = Field(
        default=None, description="Importance of the event. 1-Low, 2-Medium, 3-High"
    )
    currency: Optional[str] = Field(default=None, description="Currency of the data.")
    unit: Optional[str] = Field(default=None, description="Unit of the data.")
