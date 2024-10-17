"""House Disclosure Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS, DATA_DESCRIPTIONS


class HouseDisclosureQueryParams(QueryParams):
    """House Disclosure Query Parameters."""

    symbol: str = Field(..., description=QUERY_DESCRIPTIONS.get("symbol", "The symbol of the company."))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class HouseDisclosureData(Data):
    """House Disclosure Data Model."""

    disclosure_year: str = Field(description="The year of the disclosure.")
    disclosure_date: dateType = Field(description="The date of the disclosure.")
    transaction_date: dateType = Field(description="The date of the transaction.")
    owner: str = Field(description="The owner of the transaction.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "The symbol of the company."))
    asset_description: str = Field(description="The description of the asset.")
    type: str = Field(description="The type of transaction.")
    amount: str = Field(description="The amount of the transaction.")
    representative: str = Field(description="The representative associated with the transaction.")
    district: str = Field(description="The district of the representative.")
    link: str = Field(description="The link to the disclosure document.")
    capital_gains_over_200_usd: Optional[bool] = Field(default=None, description="Whether the capital gains exceed 200 USD.")
