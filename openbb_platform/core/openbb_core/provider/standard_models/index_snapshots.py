"""Index Snapshots Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class IndexSnapshotsQueryParams(QueryParams):
    """Index Snapshots Query."""

    region: str = Field(
        default="us", description="The region of focus for the data - i.e., us, eu."
    )


class IndexSnapshotsData(Data):
    """Index Snapshots Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(default=None, description="Name of the index.")
    currency: Optional[str] = Field(default=None, description="Currency of the index.")
    price: Optional[float] = Field(
        default=None, description="Current price of the index."
    )
    open: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: Optional[int] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    prev_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: Optional[float] = Field(
        default=None, description="Change in value of the index."
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change, in normalized percentage points, of the index.",
    )
