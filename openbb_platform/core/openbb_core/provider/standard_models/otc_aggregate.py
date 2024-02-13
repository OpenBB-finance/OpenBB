"""OTC Aggregate Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class OTCAggregateQueryParams(QueryParams):
    """OTC Aggregate Query."""

    symbol: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
        default=None,
    )


class OTCAggregateData(Data):
    """OTC Aggregate Data."""

    update_date: dateType = Field(
        description="Most recent date on which total trades is updated based on data received from each ATS/OTC."
    )
    share_quantity: float = Field(
        description="Aggregate weekly total number of shares reported by each ATS for the Symbol."
    )
    trade_quantity: float = Field(
        description="Aggregate weekly total number of trades reported by each ATS for the Symbol"
    )
