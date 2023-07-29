"""Risk Premium data model."""


from typing import Optional

from pydantic import Field, NonNegativeFloat, PositiveFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class RiskPremiumQueryParams(QueryParams):
    """Risk Premium query."""


class RiskPremiumData(Data):
    """Risk Premium data.

    Returns
    -------
    country : str
    continent : str
    totalEquityRiskPremium : PositiveFloat
    countryRiskPremium : PositiveFloat
    """

    country: str
    continent: Optional[str]
    totalEquityRiskPremium: PositiveFloat = Field(alias="total_equity_risk_premium")
    countryRiskPremium: NonNegativeFloat = Field(alias="country_risk_premium")
