"""ETF Sectors Standard Model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class EtfSectorsQueryParams(QueryParams):
    """ETF Sectors Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfSectorsData(Data):
    """ETF Sectors Data."""

    sector: str = Field(description="Sector of exposure.")
    weight: Optional[float] = Field(
        description="Exposure of the ETF to the sector in normalized percentage points."
    )
