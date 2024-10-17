"""Senate Trading RSS Feed Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)


class SenateTradingRSSFeedQueryParams(QueryParams):
    """Senate Trading RSS Feed Query."""

    page: int = Field(description="The page number of the RSS feed.", ge=0)


class SenateTradingRSSFeedData(Data):
    """Senate Trading RSS Feed data."""

    first_name: str = Field(description="The first name of the Senator.")
    last_name: str = Field(description="The last name of the Senator.")
    office: str = Field(description="The office of the Senator.")
    link: str = Field(description="The link to the transaction details.")
    date_received: Optional[dateType] = Field(default=None, description="The date the transaction was received.")
    transaction_date: dateType = Field(description="The date of the transaction.")
    owner: str = Field(description="The owner of the asset.")
    asset_description: str = Field(description="The description of the asset.")
    asset_type: str = Field(description="The type of the asset.")
    type: str = Field(description="The type of transaction.")
    amount: str = Field(description="The amount range of the transaction.")
    comment: str = Field(description="Any comments regarding the transaction.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
