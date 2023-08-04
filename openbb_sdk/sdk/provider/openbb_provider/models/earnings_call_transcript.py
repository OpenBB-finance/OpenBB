"""Earnings call transcript data model."""


from datetime import datetime
from typing import Literal

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class EarningsCallTranscriptQueryParams(QueryParams, BaseSymbol):
    """Earnings call transcript rating Query."""

    year: int = Field(description="The year of the earnings call transcript.")
    quarter: Literal[1, 2, 3, 4] = Field(
        default=1, description="The quarter of the earnings call transcript."
    )


class EarningsCallTranscriptData(Data, BaseSymbol):
    """Earnings call transcript Data."""

    quarter: int = Field(description="The quarter of the earnings call transcript.")
    year: int = Field(description="The year of the earnings call transcript.")
    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    content: str = Field(description="The content of the earnings call transcript.")
