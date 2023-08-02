"""Price Target data model."""


from datetime import datetime
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class PriceTargetQueryParams(QueryParams, BaseSymbol):
    """Price Target Query."""


class PriceTargetData(Data, BaseSymbol):
    """Price target Data."""

    published_date: datetime = Field(
        description="The published date of the price target."
    )
    news_url: str = Field(description="The news URL of the price target.")
    news_title: Optional[str] = Field(description="The news title of the price target.")
    analyst_name: Optional[str] = Field(
        description="The analyst name of the price target."
    )
    price_target: float = Field(description="The price target of the price target.")
    adj_price_target: float = Field(
        description="The adjusted price target of the price target."
    )
    price_when_posted: float = Field(
        description="The price when posted of the price target."
    )
    news_publisher: str = Field(description="The news publisher of the price target.")
    news_base_url: str = Field(description="The news base URL of the price target.")
    analyst_company: str = Field(description="The analyst company of the price target.")
