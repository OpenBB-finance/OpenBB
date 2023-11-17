"""Filings Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class FilingsQueryParams(QueryParams):
    """Filings Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    form_type: Optional[str] = Field(
        default=None,
        description="Fuzzy filter by form type. E.g. 10-K, 10, 8, 6-K, etc.",
    )
    limit: NonNegativeInt = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class FilingsData(Data):
    """Filings Data."""

    timestamp: datetime = Field(
        description="The timestamp from when the filing was accepted.",
    )
    symbol: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    cik: str = Field(
        description="The CIK of the filing",
    )
    title: str = Field(
        description="The title of the filing",
    )
    form_type: str = Field(
        description="The form type of the filing",
    )
    url: Optional[str] = Field(description="The URL of the filing", default=None)
