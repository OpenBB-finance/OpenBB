"""Risk Premium Standard Model."""

from typing import Optional

from pydantic import Field, NonNegativeFloat, PositiveFloat

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class RiskPremiumQueryParams(QueryParams):
    """Risk Premium Query."""


class RiskPremiumData(Data):
    """Risk Premium Data."""

    country: str = Field(description="Market country.")
    continent: Optional[str] = Field(
        default=None, description="Continent of the country."
    )
    total_equity_risk_premium: Optional[PositiveFloat] = Field(
        default=None, description="Total equity risk premium for the country."
    )
    country_risk_premium: Optional[NonNegativeFloat] = Field(
        default=None, description="Country-specific risk premium."
    )
