"""Global News Data Model."""


from datetime import datetime
from typing import Dict, List, Optional

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
    images: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Images associated with the news."
    )
    text: Optional[str] = Field(default=None, description="Text/body of the news.")
    url: Optional[str] = Field(default=None, description="URL of the news.")
