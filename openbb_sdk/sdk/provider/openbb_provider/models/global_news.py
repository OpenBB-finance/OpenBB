"""Global News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.abstract.data import Data, QueryParams


class GlobalNewsQueryParams(QueryParams):
    """Global news query."""

    page: NonNegativeInt = Field(default=0, description="The page of the global news.")


class GlobalNewsData(Data):
    """Return Global News Data."""

    date: datetime = Field(description="The published date of the news.")
    title: str = Field(description="The title of the news.")
    image: Optional[str] = Field(description="The image URL of the news.")
    text: str = Field(description="The text/body of the news.")
    url: str = Field(description="The URL of the news.")
