"""ICE BofA US Corporate Bond Indices Model."""
from datetime import (
    date as dateType,
)
from typing import Optional, Literal

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class ICEBofAParams(QueryParams):
    """ICE BofA US Corporate Bond Indices Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    type_: Literal["yield", "yield_to_worst", "total_return", "spread"] = Field(
        default="yield",
        description=".",
    )


class ICEBofAsData(Data):
    """ICE BofA US Corporate Bond Indices Data."""

    # date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    # rate: Optional[float] = Field(description="European Central Bank Interest Rate.")
