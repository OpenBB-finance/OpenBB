"""Stock News Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field, NonNegativeInt, validator

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS


class StockNewsQueryParams(QueryParams):
    """Stock news query."""

    symbols: str = Field(
        min_length=1, description=QUERY_DESCRIPTIONS.get("symbols", "")
    )
    page: int = Field(
        default=0, description="The page of the stock news to be retrieved."
    )
    limit: Optional[NonNegativeInt] = Field(
        default=15, description="The number of results to return per page."
    )

    @validator("symbols", pre=True)
    def time_validate(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class StockNewsData(Data):
    """Stock News data."""

    date: dateType = Field(description="The published date of the news.")
    title: str = Field(description="The title of the news.")
    text: Optional[str] = Field(default=None, description="The text/body of the news.")
    url: str = Field(description="The URL of the news.")
