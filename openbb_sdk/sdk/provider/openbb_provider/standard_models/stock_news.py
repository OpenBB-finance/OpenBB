"""Stock News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockNewsQueryParams(QueryParams):
    """Stock news query."""

    symbols: str = Field(min_length=1, description=QUERY_DESCRIPTIONS.get("symbol", ""))
    page: int = Field(
        default=0, description="The page of the stock news to be retrieved."
    )
    limit: Optional[NonNegativeInt] = Field(
        default=15, description="The number of results to return per page."
    )

    @validator("symbols", pre=True)
    def symbol_validate(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class StockNewsData(Data):
    """Stock News data."""

    date: datetime = Field(description="The published date of the news.")
    title: str = Field(description="The title of the news.")
    text: Optional[str] = Field(default=None, description="The text/body of the news.")
    url: str = Field(description="The URL of the news.")
