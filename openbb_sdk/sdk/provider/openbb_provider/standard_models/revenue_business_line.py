"""Revenue by Business Line data model."""


from datetime import date as dateType
from typing import Dict, Literal

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class RevenueBusinessLineQueryParams(QueryParams, BaseSymbol):
    """Revenue Business Line Query."""

    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat", description="Structure of the returned data."
    )  # should always be flat


class RevenueBusinessLineData(Data):
    """Revenue by Business Line Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    business_line: Dict[str, int] = Field(
        description="Day level data containing the revenue of the business line."
    )
