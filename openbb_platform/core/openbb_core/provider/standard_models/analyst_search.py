"""Analyst Search Standard Model."""

from datetime import (
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class AnalystSearchQueryParams(QueryParams):
    """Analyst Search Query."""

    analyst_name: Optional[str] = Field(
        default=None,
        description="Analyst names to return."
        + " Omitting will return all available analysts.",
    )
    firm_name: Optional[str] = Field(
        default=None,
        description="Firm names to return."
        + " Omitting will return all available firms.",
    )


class AnalystSearchData(Data):
    """Analyst Search data."""

    last_updated: Optional[datetime] = Field(
        default=None,
        description="Date of the last update.",
    )
    firm_name: Optional[str] = Field(
        default=None,
        description="Firm name of the analyst.",
    )
    name_first: Optional[str] = Field(
        default=None,
        description="Analyst first name.",
    )
    name_last: Optional[str] = Field(
        default=None,
        description="Analyst last name.",
    )
    name_full: str = Field(
        description="Analyst full name.",
    )
