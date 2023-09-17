"""Global News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class GlobalNewsQueryParams(QueryParams):
    """Global news Query."""

    limit: NonNegativeInt = Field(
        default=20, description="Number of articles to return."
    )


class GlobalNewsData(Data):
    """Global News Data."""

    date: datetime = Field(description="Published date of the news.")
    title: str = Field(description="Title of the news.")
    image: Optional[str] = Field(description="Image URL of the news.")
    text: Optional[str] = Field(description="Text/body of the news.")
    url: str = Field(description="URL of the news.")
