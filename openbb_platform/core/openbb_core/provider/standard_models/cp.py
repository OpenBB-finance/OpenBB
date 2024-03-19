"""Commercial Paper Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CommercialPaperParams(QueryParams):
    """Commercial Paper Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    maturity: Literal["overnight", "7d", "15d", "30d", "60d", "90d"] = Field(
        default="30d",
        description="The maturity.",
    )
    category: Literal["asset_backed", "financial", "nonfinancial"] = Field(
        default="financial",
        description="The category.",
    )
    grade: Literal["aa", "a2_p2"] = Field(
        default="aa",
        description="The grade.",
    )

    @field_validator("maturity", "category", "grade", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class CommercialPaperData(Data):
    """Commercial Paper Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(description="Commercial Paper Rate.")
