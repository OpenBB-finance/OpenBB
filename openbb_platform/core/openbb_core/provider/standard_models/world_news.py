"""World News Standard Model."""


from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, NonNegativeInt

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class WorldNewsQueryParams(QueryParams):
    """World News Query."""

    limit: NonNegativeInt = Field(
        default=20,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " Here its the no. of articles to return.",
    )


class WorldNewsData(Data):
    """World News Data."""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " Here it is the published date of the news."
    )
    title: str = Field(description="Title of the news.")
    images: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Images associated with the news."
    )
    text: Optional[str] = Field(default=None, description="Text/body of the news.")
    url: Optional[str] = Field(default=None, description="URL of the news.")
