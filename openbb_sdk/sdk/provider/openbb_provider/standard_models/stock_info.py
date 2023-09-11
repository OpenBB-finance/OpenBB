"""Stock Info data model."""

from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockInfoQueryParams(QueryParams):
    """Stock Info Query Params"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class StockInfoData(Data):
    """Stock Info Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Name associated with the ticker symbol.")
    price: float = Field(description="Last transaction price.")
    open: Optional[float] = Field(description="Opening price of the stock.")
    high: Optional[float] = Field(description="High price of the current trading day.")
    low: Optional[float] = Field(description="Low price of the current trading day.")
    close: Optional[float] = Field(
        description="Closing price of the most recent trading day."
    )
    change: Optional[float] = Field(
        description="Change in price over the current trading period."
    )
    change_percent: Optional[float] = Field(
        description="Percent change in price over the current trading period."
    )
    prev_close: Optional[float] = Field(description="Previous closing price.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
