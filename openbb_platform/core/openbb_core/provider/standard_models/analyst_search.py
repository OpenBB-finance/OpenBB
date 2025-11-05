"""Analyst Search Standard Model."""

from datetime import (
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class AnalystSearchQueryParams(QueryParams):
    """Analyst Search Query."""

    analyst_name: str | None = Field(
        default=None,
        description="Analyst names to return."
        + " Omitting will return all available analysts.",
    )
    firm_name: str | None = Field(
        default=None,
        description="Firm names to return."
        + " Omitting will return all available firms.",
    )


class AnalystSearchData(Data):
    """Analyst Search data."""

    last_updated: datetime | None = Field(
        default=None,
        description="Date of the last update.",
    )
    firm_name: str | None = Field(
        default=None,
        description="Firm name of the analyst.",
    )
    name_first: str | None = Field(
        default=None,
        description="Analyst first name.",
    )
    name_last: str | None = Field(
        default=None,
        description="Analyst last name.",
    )
    name_full: str = Field(
        description="Analyst full name.",
    )
