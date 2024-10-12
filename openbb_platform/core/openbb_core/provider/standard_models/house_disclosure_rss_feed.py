"""House Disclosure RSS Feed Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams



class HouseDisclosureRSSFeedQueryParams(QueryParams):
    """House Disclosure RSS Feed Query Parameters."""

    page: Optional[int] = Field(None, description="The page number of the RSS feed.", ge=0)


class HouseDisclosureRSSFeedData(Data):
    """House Disclosure RSS Feed Data Model."""

    disclosure_year: str = Field(description="The year of the disclosure.")
    disclosure_date: dateType = Field(description="The date of the disclosure.")
    transaction_date: dateType = Field(description="The date of the transaction.")
    owner: str = Field(description="The owner of the transaction.")
    ticker: str = Field(description="The ticker symbol of the asset.")
    asset_description: str = Field(description="The description of the asset.")
    type: str = Field(description="The type of transaction.")
    amount: str = Field(description="The amount of the transaction.")
    representative: str = Field(description="The representative associated with the transaction.")
    district: str = Field(description="The district of the representative.")
    link: str = Field(description="The link to the disclosure document.")
    capital_gains_over_200_usd: Optional[str] = Field(None, description="Whether the capital gains exceed 200 USD.")
