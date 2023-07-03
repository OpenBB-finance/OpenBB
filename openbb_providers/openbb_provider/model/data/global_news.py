"""Global News Data Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.model.abstract.data import Data, QueryParams


class GlobalNewsQueryParams(QueryParams):
    """Global news query.

    Parameter
    ---------
    page : NonNegativeInt
        The page of the global news to be retrieved.
    """

    __name__ = "GlobalNewsQueryParams"
    page: NonNegativeInt = Field(default=0)


class GlobalNewsData(Data):
    """Return Global News Data.

    Returns
    -------
    date : datetime
        The published date of the news.
    title : str
        The title of the news.
    image : Optional[str]
        The image URL of the news.
    text : str
        The text/body of the news.
    url : str
        The URL of the news.
    """

    date: datetime
    title: str
    image: Optional[str]
    text: str
    url: str
