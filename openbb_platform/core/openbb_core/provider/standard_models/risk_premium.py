"""Risk Premium Standard Model."""


from typing import Optional

from pydantic import Field

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
    total_equity_risk_premium: Optional[float] = Field(
        default=None,
        description="Total equity risk premium for the country, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    country_risk_premium: Optional[float] = Field(
        default=None,
        description="Country-specific risk premium, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
