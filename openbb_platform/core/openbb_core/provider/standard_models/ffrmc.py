"""Selected Treasury Constant Maturity Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class SelectedTreasuryConstantMaturityQueryParams(QueryParams):
    """Selected Treasury Constant Maturity Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    maturity: Literal["10y", "5y", "1y", "6m", "3m"] | None = Field(
        default="10y",
        description="The maturity",
    )

    @field_validator("maturity", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """Convert field to lowercase."""
        return v.lower() if v else v


class SelectedTreasuryConstantMaturityData(Data):
    """Selected Treasury Constant Maturity Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float | None = Field(description="Selected Treasury Constant Maturity Rate.")
