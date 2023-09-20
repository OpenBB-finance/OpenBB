"""Price Target data model."""


from datetime import datetime
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class PriceTargetQueryParams(QueryParams):
    """Price Target Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class PriceTargetData(Data):
    """Price target Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    published_date: datetime = Field(description="Published date of the price target.")
    news_url: str = Field(description="News URL of the price target.")
    news_title: Optional[str] = Field(description="News title of the price target.")
    analyst_name: Optional[str] = Field(description="Analyst name.")
    analyst_company: Optional[str] = Field(description="Analyst company.")
    price_target: Optional[float] = Field(description="Price target.")
    adj_price_target: Optional[float] = Field(description="Adjusted price target.")
    price_when_posted: Optional[float] = Field(description="Price when posted.")
    news_publisher: Optional[str] = Field(
        description="News publisher of the price target."
    )
    news_base_url: Optional[str] = Field(
        description="News base URL of the price target."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
