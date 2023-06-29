"""Stock News Data Model."""

# IMPORT STANDARD
from datetime import date
from typing import Optional

# IMPORT THIRD-PARTY
from pydantic import Field, validator

from openbb_provider.metadata import DESCRIPTIONS

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams


class StockNewsQueryParams(QueryParams):
    """Stock news query.


    Parameter
    ---------
    symbols : str
        The symbols of the company.
    page : int
        The page of the stock news to be retrieved.
    """

    __name__ = "StockNewsQueryParams"
    symbols: str = Field(min_length=1, description=DESCRIPTIONS.get("symbols", ""))
    page: int = Field(default=0)

    @validator("symbols", pre=True)
    def time_validate(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class StockNewsData(Data):
    """Stock News data.

    Returns
    -------
    date : date
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

    date: date
    title: str
    image: Optional[str]
    text: Optional[str]
    url: str
