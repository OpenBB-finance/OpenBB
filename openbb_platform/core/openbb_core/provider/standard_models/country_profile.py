"""Country Profile Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class CountryProfileQueryParams(QueryParams):
    """Country Profile Query."""

    country: str = Field(description=QUERY_DESCRIPTIONS.get("country", ""))

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str) -> str:
        """Convert the country to lowercase."""
        return v.lower().replace(" ", "_")


class CountryProfileData(Data):
    """Country Profile Data."""

    country: str = Field(description=DATA_DESCRIPTIONS.get("country", ""))
    population: Optional[int] = Field(default=None, description="Population.")
    gdp_usd: Optional[float] = Field(
        default=None, description="Gross Domestic Product, in billions of USD."
    )
    gdp_qoq: Optional[float] = Field(
        default=None,
        description="GDP growth quarter-over-quarter change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    gdp_yoy: Optional[float] = Field(
        default=None,
        description="GDP growth year-over-year change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    cpi_yoy: Optional[float] = Field(
        default=None,
        description="Consumer Price Index year-over-year change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    core_yoy: Optional[float] = Field(
        default=None,
        description="Core Consumer Price Index year-over-year change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    retail_sales_yoy: Optional[float] = Field(
        default=None,
        description="Retail Sales year-over-year change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    industrial_production_yoy: Optional[float] = Field(
        default=None,
        description="Industrial Production year-over-year change, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    policy_rate: Optional[float] = Field(
        default=None,
        description="Short term policy rate, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    yield_10y: Optional[float] = Field(
        default=None,
        description="10-year government bond yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    govt_debt_gdp: Optional[float] = Field(
        default=None,
        description="Government debt as a percent (normalized) of GDP.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    current_account_gdp: Optional[float] = Field(
        default=None,
        description="Current account balance as a percent (normalized) of GDP.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    jobless_rate: Optional[float] = Field(
        default=None,
        description="Unemployment rate, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
