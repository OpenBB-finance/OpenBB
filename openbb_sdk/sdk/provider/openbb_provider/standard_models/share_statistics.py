"""Share Statistics Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class ShareStatisticsQueryParams(QueryParams, BaseSymbol):
    """Share Statistics Query."""


class ShareStatisticsData(Data, BaseSymbol):
    """Return Share Statistics Data."""

    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )
    free_float: Optional[float] = Field(
        default=None,
        description="Percentage of unrestricted shares of a publicly-traded company.",
    )
    float_shares: Optional[float] = Field(
        default=None,
        description="Number of shares available for trading by the general public.",
    )
    outstanding_shares: Optional[float] = Field(
        default=None, description="Total number of shares of a publicly-traded company."
    )
    source: Optional[str] = Field(
        default=None, description="Source of the received data."
    )
