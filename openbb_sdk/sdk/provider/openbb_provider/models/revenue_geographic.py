"""Revenue by geographic segments data model."""


from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class RevenueGeographicQueryParams(QueryParams, BaseSymbol):
    """Revenue by Geographic Segments Query."""

    period: Literal["quarterly", "annually"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat", description="The structure of the returned data."
    )  # should always be flat # should always be flat


class RevenueGeographicData(Data):
    """Revenue by Geographic Segments Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    americas: Optional[int] = Field(
        description="The revenue from the the American segment."
    )
    europe: Optional[int] = Field(
        description="The revenue from the the European segment."
    )
    greater_china: Optional[int] = Field(
        description="The revenue from the the Greater China segment."
    )
    japan: Optional[int] = Field(description="The revenue from the the Japan segment.")
    rest_of_asia_pacific: Optional[int] = Field(
        description="The revenue from the the Rest of Asia Pacific segment."
    )
