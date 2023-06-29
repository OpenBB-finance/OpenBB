"""Earnings call transcript data model."""

# IMPORT STANDARD
from datetime import datetime

# IMPORT THIRD-PARTY
from pydantic import validator

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class EarningsCallTranscriptQueryParams(QueryParams, BaseSymbol):
    """Earnings call transcript rating query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    year : int
        The year of the earnings call transcript.
    """

    __name__ = "EarningsCallTranscriptQueryParams"

    year: int

    @validator("year", pre=True)
    def time_validate(cls, v: int):  # pylint: disable=E0213
        current_year = datetime.now().year
        if v > current_year:
            return current_year
        if v < 1950:
            return current_year
        return v


class EarningsCallTranscriptData(Data, BaseSymbol):
    """Earnings call transcript data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    quarter : int
        The quarter of the earnings call transcript.
    year : int
        The year of the earnings call transcript.
    date : datetime
        The date of the earnings call transcript.
    content : str
        The content of the earnings call transcript.
    """

    symbol: str
    quarter: int
    year: int
    date: datetime
    content: str
