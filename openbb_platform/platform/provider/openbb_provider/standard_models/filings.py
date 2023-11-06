"""Filings Data Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class FilingsQueryParams(QueryParams):
    """Filings query."""

    pages: NonNegativeInt = Field(
        default=1,
        description="The range of most-recent pages to get entries from (1000 per page, max 30 pages)",
    )
    limit: NonNegativeInt = Field(
        default=5, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    today: bool = Field(
        default=False,
        description="Show all from today",
    )


class FilingsData(Data):
    """Filings data."""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    title: str = Field(
        description="The title of the filing",
    )
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    url: Optional[str] = Field(description="The URL of the filing", default=None)
    cik: str = Field(
        description="The CIK of the filing",
    )
    form_type: str = Field(
        description="The form type of the filing",
    )
