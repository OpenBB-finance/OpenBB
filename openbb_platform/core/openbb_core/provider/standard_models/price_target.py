"""Price Target Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    time,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class PriceTargetQueryParams(QueryParams):
    """Price Target Query."""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    limit: int | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper() if v else None


class PriceTargetData(Data):
    """Price Target Data."""

    published_date: dateType | datetime = Field(
        description="Published date of the price target."
    )
    published_time: time | None = Field(
        default=None, description="Time of the original rating, UTC."
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    exchange: str | None = Field(
        default=None, description="Exchange where the company is traded."
    )
    company_name: str | None = Field(
        default=None, description="Name of company that is the subject of rating."
    )
    analyst_name: str | None = Field(default=None, description="Analyst name.")
    analyst_firm: str | None = Field(
        default=None,
        description="Name of the analyst firm that published the price target.",
    )
    currency: str | None = Field(
        default=None, description="Currency the data is denominated in."
    )
    price_target: float | None = Field(
        default=None, description="The current price target."
    )
    adj_price_target: float | None = Field(
        default=None,
        description="Adjusted price target for splits and stock dividends.",
    )
    price_target_previous: float | None = Field(
        default=None, description="Previous price target."
    )
    previous_adj_price_target: float | None = Field(
        default=None, description="Previous adjusted price target."
    )
    price_when_posted: float | None = Field(
        default=None, description="Price when posted."
    )
    rating_current: str | None = Field(
        default=None, description="The analyst's rating for the company."
    )
    rating_previous: str | None = Field(
        default=None, description="Previous analyst rating for the company."
    )
    action: str | None = Field(
        default=None,
        description="Description of the change in rating from firm's last rating.",
    )
