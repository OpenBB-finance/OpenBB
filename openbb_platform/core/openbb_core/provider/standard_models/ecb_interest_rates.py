"""European Central Bank Interest Rates Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EuropeanCentralBankInterestRatesParams(QueryParams):
    """European Central Bank Interest Rates Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    interest_rate_type: Literal["deposit", "lending", "refinancing"] = Field(
        default="lending",
        description="The type of interest rate.",
    )

    @field_validator("interest_rate_type", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class EuropeanCentralBankInterestRatesData(Data):
    """European Central Bank Interest Rates Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(description="European Central Bank Interest Rate.")
