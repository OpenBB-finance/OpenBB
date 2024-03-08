"""High Quality Market Corporate Bond Standard Model."""

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


class HighQualityMarketCorporateBondQueryParams(QueryParams):
    """High Quality Market Corporate Bond Query."""

    date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )
    yield_curve: Literal["spot", "par"] = Field(
        default="spot",
        description="The yield curve type.",
    )

    @field_validator("yield_curve", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class HighQualityMarketCorporateBondData(Data):
    """High Quality Market Corporate Bond Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(description="HighQualityMarketCorporateBond Rate.")
    maturity: str = Field(description="Maturity.")
    yield_curve: Literal["spot", "par"] = Field(description="The yield curve type.")
