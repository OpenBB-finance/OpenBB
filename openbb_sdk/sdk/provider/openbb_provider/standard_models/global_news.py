"""Global News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class GlobalNewsQueryParams(QueryParams):
    """Global news query."""

    page: NonNegativeInt = Field(default=0, description="Page of the global news.")


class GlobalNewsData(Data):
    """Return Global News Data."""

    date: datetime = Field(description="Published date of the news.")
    title: str = Field(description="Title of the news.")
    image: Optional[str] = Field(description="Image URL of the news.")
    text: str = Field(description="Text/body of the news.")
    url: str = Field(description="URL of the news.")
