"""ETF Sectors data model."""

from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfSectorsQueryParams(QueryParams):
    """ETF Sectors Query Params"""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfSectorsData(Data):
    """ETF Sectors Data."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")
    energy: Optional[float] = Field(description="Energy Sector Weight")
    materials: Optional[float] = Field(description="Materials Sector Weight.")
    industrials: Optional[float] = Field(description="Industrials Sector Weight.")
    consumer_cyclical: Optional[float] = Field(
        description="Consumer Cyclical Sector Weight."
    )
    consumer_defensive: Optional[float] = Field(
        description="Consumer Defensive Sector Weight."
    )
    financial_services: Optional[float] = Field(
        description="Financial Services Sector Weight."
    )
    technology: Optional[float] = Field(description="Technology Sector Weight.")
    health_care: Optional[float] = Field(description="Health Care Sector Weight.")
    communication_services: Optional[float] = Field(
        description="Communication Services Sector Weight.",
        alias="Communication Services",
    )
    utilities: Optional[float] = Field(description="Utilities Sector Weight.")
    real_estate: Optional[float] = Field(description="Real Estate Sector Weight.")
