"""Commitment of Traders Reports Search Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CotSearchQueryParams(QueryParams):
    """Commitment of Traders Reports Search Query."""

    query: str = Field(description="Search query.", default="")


class CotSearchData(Data):
    """Commitment of Traders Reports Search Data."""

    code: str = Field(description="CFTC market contract code of the report.")
    name: str = Field(description="Name of the underlying asset.")
    category: Optional[str] = Field(
        default=None, description="Category of the underlying asset."
    )
    subcategory: Optional[str] = Field(
        default=None, description="Subcategory of the underlying asset."
    )
    units: Optional[str] = Field(
        default=None, description="The units for one contract."
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
