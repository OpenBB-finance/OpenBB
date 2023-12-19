"""US Yield Curve Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class USYieldCurveQueryParams(QueryParams):
    """US Yield Curve Query."""

    date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " Defaults to the most recent FRED entry.",
    )
    inflation_adjusted: Optional[bool] = Field(
        default=False, description="Get inflation adjusted rates."
    )


class USYieldCurveData(Data):
    """US Yield Curve Data."""

    maturity: float = Field(description="Maturity of the treasury rate in years.")
    rate: float = Field(
        description="Associated rate given in decimal form (0.05 is 5%)"
    )
