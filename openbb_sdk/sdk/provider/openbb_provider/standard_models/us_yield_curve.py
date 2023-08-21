"""Treasury Rates Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class USYieldCurveQueryParams(QueryParams):
    """Treasury Rates Query."""

    date: Optional[dateType] = Field(
        default=None,
        description="Date to get Yield Curve data.  Defaults to the most recent FRED entry.",
    )
    inflation_adjusted: Optional[bool] = Field(
        default=False, description="Get inflation adjusted rates."
    )


class USYieldCurveData(Data):
    """Return Treasury Rates Data."""

    maturity: float = Field(description="Maturity of the treasury rate in years.")
    rate: float = Field(
        description="Associated rate given in decimal form (0.05 is 5%)"
    )
