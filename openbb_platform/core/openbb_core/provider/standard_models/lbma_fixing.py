"""LBMA Fixing Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class LbmaFixingQueryParams(QueryParams):
    """
    LBMA Fixing Query.

    Source: https://www.lbma.org.uk/prices-and-data/precious-metal-prices#/table
    """

    asset: Literal["gold", "silver"] = Field(
        description="The metal to get price fixing rates for.",
        default="gold",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("asset", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class LbmaFixingData(Data):
    """LBMA Fixing Data.  Historical fixing prices in USD, GBP and EUR."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    usd_am: Optional[float] = Field(
        default=None,
        description="AM fixing price in USD.",
    )
    usd_pm: Optional[float] = Field(
        default=None,
        description="PM fixing price in USD.",
    )
    gbp_am: Optional[float] = Field(
        default=None,
        description="AM fixing price in GBP.",
    )
    gbp_pm: Optional[float] = Field(
        default=None,
        description="PM fixing price in GBP.",
    )
    euro_am: Optional[float] = Field(
        default=None,
        description="AM fixing price in EUR.",
    )
    euro_pm: Optional[float] = Field(
        default=None,
        description="PM fixing price in EUR.",
    )
    usd: Optional[float] = Field(
        default=None,
        description="Daily fixing price in USD.",
    )
    gbp: Optional[float] = Field(
        default=None,
        description="Daily fixing price in GBP.",
    )
    eur: Optional[float] = Field(
        default=None,
        description="Daily fixing price in EUR.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v) -> dateType:
        """Validate date."""
        if isinstance(v, datetime):
            return v.date()
        return datetime.strptime(v, "%Y-%m-%d").date()
