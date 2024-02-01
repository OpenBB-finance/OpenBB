"""Nasdaq Data Link Standard Query Params."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class DataLinkQueryParams(QueryParams):
    """Standard Nasdaq Data Link Query Params"""

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
        default=None,
    )
    transform: Literal["diff", "rdiff", "cumul", "normalize", None] = Field(
        description="Transform the data as difference, percent change, cumulative, or normalize.",
        default=None,
    )
    collapse: Literal["daily", "weekly", "monthly", "quarterly", "annual", None] = (
        Field(
            description="Collapse the frequency of the time series.",
            default=None,
        )
    )
