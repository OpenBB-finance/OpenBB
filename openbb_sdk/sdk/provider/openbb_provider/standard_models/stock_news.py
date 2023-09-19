"""Stock News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class StockNewsQueryParams(QueryParams):
    """Stock news query."""

    symbols: str = Field(min_length=1, description="Comma separated list of symbols.")
    limit: Optional[NonNegativeInt] = Field(
        default=20, description="Number of results to return per page."
    )

    @validator("symbols", pre=True)
    def symbols_validate(cls, v: str):  # pylint: disable=E0213
        """Validate the symbols."""
        return v.upper()


class StockNewsData(Data):
    """Stock News data."""

    date: datetime = Field(description="Published date of the news.")
    title: str = Field(description="Title of the news.")
    image: Optional[str] = Field(default=None, description="Image URL of the news.")
    text: Optional[str] = Field(default=None, description="Text/body of the news.")
    url: str = Field(description="URL of the news.")
