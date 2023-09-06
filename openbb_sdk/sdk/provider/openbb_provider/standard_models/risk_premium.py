"""Risk Premium data model."""


from typing import Optional

from pydantic import Field, NonNegativeFloat, PositiveFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class RiskPremiumQueryParams(QueryParams):
    """Risk Premium Query."""


class RiskPremiumData(Data):
    """Risk Premium Data."""

    country: str = Field(description="Market country.")
    continent: Optional[str] = Field(description="Continent of the country.")
    total_equity_risk_premium: PositiveFloat = Field(
        description="Total equity risk premium for the country."
    )
    country_risk_premium: NonNegativeFloat = Field(
        description="Country-specific risk premium."
    )
