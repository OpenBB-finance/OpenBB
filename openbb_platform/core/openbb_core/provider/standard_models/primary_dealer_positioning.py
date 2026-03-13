"""Primray Dealer Positioning Standard Model."""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class PrimaryDealerPositioningQueryParams(QueryParams):
    """Primary Dealer Positioning Query."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class PrimaryDealerPositioningData(Data):
    """Primary Dealer Positioning Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
