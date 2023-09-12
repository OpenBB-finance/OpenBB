"""Price Target data model."""


from datetime import datetime
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class PriceTargetQueryParams(QueryParams, BaseSymbol):
    """Price Target Query."""


class PriceTargetData(Data, BaseSymbol):
    """Price target Data."""

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
