"""Price Target Standard Model."""

from datetime import datetime
from typing import List, Optional, Set, Union

from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class PriceTargetQueryParams(QueryParams):
    """Price Target Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: NonNegativeInt = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class PriceTargetData(Data):
    """Price Target Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    published_date: datetime = Field(description="Published date of the price target.")
    news_url: Optional[str] = Field(
        default=None, description="News URL of the price target."
    )
    news_title: Optional[str] = Field(
        default=None, description="News title of the price target."
    )
    analyst_name: Optional[str] = Field(default=None, description="Analyst name.")
    analyst_company: Optional[str] = Field(default=None, description="Analyst company.")
    price_target: Optional[float] = Field(default=None, description="Price target.")
    adj_price_target: Optional[float] = Field(
        default=None, description="Adjusted price target."
    )
    price_when_posted: Optional[float] = Field(
        default=None, description="Price when posted."
    )
    news_publisher: Optional[str] = Field(
        default=None, description="News publisher of the price target."
    )
    news_base_url: Optional[str] = Field(
        default=None, description="News base URL of the price target."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
