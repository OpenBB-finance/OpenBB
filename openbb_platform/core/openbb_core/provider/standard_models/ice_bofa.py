"""ICE BofA US Corporate Bond Indices Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ICEBofAQueryParams(QueryParams):
    """ICE BofA US Corporate Bond Indices Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    index_type: Literal["yield", "yield_to_worst", "total_return", "spread"] = Field(
        default="yield",
        description="The type of series.",
    )


class ICEBofAData(Data):
    """ICE BofA US Corporate Bond Indices Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(
        description="ICE BofA US Corporate Bond Indices Rate."
    )
