"""Revenue by Business Line data model."""


from datetime import date as dateType
from typing import Dict, List, Literal, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class RevenueBusinessLineQueryParams(QueryParams):
    """Revenue Business Line Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat", description="Structure of the returned data."
    )  # should always be flat

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class RevenueBusinessLineData(Data):
    """Revenue by Business Line Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    business_line: Dict[str, int] = Field(
        description="Day level data containing the revenue of the business line."
    )
