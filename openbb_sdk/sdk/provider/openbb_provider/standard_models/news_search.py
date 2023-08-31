"""News Search  data model."""

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class NewsSearchQueryParams(QueryParams):
    """News Search Query Params."""

    term: str = Field(description="Search query.")


class NewsSearchData(Data):
    """News Search Data."""

    date: datetime = Field(description="Published date and time of the news.")
    title: str = Field(description="Headline of the news.")
    text: Optional[str] = Field(description="Text/body of the news.")
    url: str = Field(description="URL of the article.")
    image: Optional[Any] = Field(description="Preview image.")
