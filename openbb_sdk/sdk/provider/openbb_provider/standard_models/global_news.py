"""Global News Data Model."""


from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class GlobalNewsQueryParams(QueryParams):
    """Global news query."""

    page: int = Field(default=0, description="Page of the global news.")


class GlobalNewsData(Data):
    """Return Global News Data."""

    date: datetime = Field(description="Published date of the news.")
    title: str = Field(description="Title of the news.")
    text: Optional[str] = Field(description="Text/body of the news.")
    tags: Optional[List[str]] = Field(description="Tags for the article.")
    site: Optional[str] = Field(description="Base url for the article source.")
    url: str = Field(description="URL of the news.")
    image: Optional[Any] = Field(description="Image URL of the news.")
