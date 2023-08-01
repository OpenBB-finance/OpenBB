"""Revenue by Business Line data model."""


from datetime import date as dateType
from typing import Dict, Literal

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.descriptions import QUERY_DESCRIPTIONS, DATA_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol

from pydantic import Field


class RevenueBusinessLineQueryParams(QueryParams, BaseSymbol):
    """Revenue Business Line Query."""

    period: Literal["quarterly", "annually"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat", description="The structure of the returned data."
    )  # should always be flat


class RevenueBusinessLineData(Data):
    """Revenue by Business Line Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    business_line: Dict[str, int] = Field(
        description="Day level data containing the revenue of the business line."
    )
