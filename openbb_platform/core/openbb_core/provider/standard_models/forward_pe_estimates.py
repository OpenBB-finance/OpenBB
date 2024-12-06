"""Forward PE Estimates Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ForwardPeEstimatesQueryParams(QueryParams):
    """Forward PE Estimates Query Parameters."""

    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["symbol"],
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert field to uppercase."""
        return v.upper() if v else None


class ForwardPeEstimatesData(Data):
    """Forward PE Estimates Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(default=None, description="Name of the entity.")
    year1: Optional[float] = Field(
        default=None,
        description="Estimated PE ratio for the next fiscal year.",
    )
    year2: Optional[float] = Field(
        default=None,
        description="Estimated PE ratio two fiscal years from now.",
    )
    year3: Optional[float] = Field(
        default=None,
        description="Estimated PE ratio three fiscal years from now.",
    )
    year4: Optional[float] = Field(
        default=None,
        description="Estimated PE ratio four fiscal years from now.",
    )
    year5: Optional[float] = Field(
        default=None,
        description="Estimated PE ratio five fiscal years from now.",
    )
