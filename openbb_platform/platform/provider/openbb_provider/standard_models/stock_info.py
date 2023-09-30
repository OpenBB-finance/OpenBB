"""Stock Info data model."""


from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockInfoQueryParams(QueryParams):
    """Stock Info Query Params"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class StockInfoData(Data):
    """Stock Info Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Name associated with the ticker symbol.")
    price: Optional[float] = Field(default=None, description="Last transaction price.")
    open: Optional[float] = Field(
        default=None, description="Opening price of the stock."
    )
    high: Optional[float] = Field(
        default=None, description="High price of the current trading day."
    )
    low: Optional[float] = Field(
        default=None, description="Low price of the current trading day."
    )
    close: Optional[float] = Field(
        default=None, description="Closing price of the most recent trading day."
    )
    change: Optional[float] = Field(
        default=None, description="Change in price over the current trading period."
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Percent change in price over the current trading period.",
    )
    prev_close: Optional[float] = Field(
        default=None, description="Previous closing price."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
