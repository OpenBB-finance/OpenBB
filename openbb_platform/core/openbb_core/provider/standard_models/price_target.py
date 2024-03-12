"""Price Target Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    time,
)
from typing import Optional, Union

from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class PriceTargetQueryParams(QueryParams):
    """Price Target Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    limit: NonNegativeInt = Field(
        default=200, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper() if v else None


class PriceTargetData(Data):
    """Price Target Data."""

    published_date: Union[dateType, datetime] = Field(
        description="Published date of the price target."
    )
    published_time: Optional[time] = Field(
        default=None, description="Time of the original rating, UTC."
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    exchange: Optional[str] = Field(
        default=None, description="Exchange where the company is traded."
    )
    company_name: Optional[str] = Field(
        default=None, description="Name of company that is the subject of rating."
    )
    analyst_name: Optional[str] = Field(default=None, description="Analyst name.")
    analyst_firm: Optional[str] = Field(
        default=None,
        description="Name of the analyst firm that published the price target.",
    )
    currency: Optional[str] = Field(
        default=None, description="Currency the data is denominated in."
    )
    price_target: Optional[float] = Field(
        default=None, description="The current price target."
    )
    adj_price_target: Optional[float] = Field(
        default=None,
        description="Adjusted price target for splits and stock dividends.",
    )
    price_target_previous: Optional[float] = Field(
        default=None, description="Previous price target."
    )
    previous_adj_price_target: Optional[float] = Field(
        default=None, description="Previous adjusted price target."
    )
    price_when_posted: Optional[float] = Field(
        default=None, description="Price when posted."
    )
    rating_current: Optional[str] = Field(
        default=None, description="The analyst's rating for the company."
    )
    rating_previous: Optional[str] = Field(
        default=None, description="Previous analyst rating for the company."
    )
    action: Optional[str] = Field(
        default=None,
        description="Description of the change in rating from firm's last rating.",
    )
