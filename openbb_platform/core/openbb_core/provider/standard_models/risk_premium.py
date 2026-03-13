"""Risk Premium Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeFloat, PositiveFloat


class RiskPremiumQueryParams(QueryParams):
    """Risk Premium Query."""


class RiskPremiumData(Data):
    """Risk Premium Data."""

    country: str = Field(description="Market country.")
    continent: str | None = Field(default=None, description="Continent of the country.")
    total_equity_risk_premium: PositiveFloat | None = Field(
        default=None, description="Total equity risk premium for the country."
    )
    country_risk_premium: NonNegativeFloat | None = Field(
        default=None, description="Country-specific risk premium."
    )
