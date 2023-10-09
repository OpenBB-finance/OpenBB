"""ETF Sectors data model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfSectorsQueryParams(QueryParams):
    """ETF Sectors Query Params."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfSectorsData(Data):
    """ETF Sectors Data."""

    energy: Optional[float] = Field(description="Energy Sector Weight", default=None)
    materials: Optional[float] = Field(
        description="Materials Sector Weight.", default=None
    )
    industrials: Optional[float] = Field(
        description="Industrials Sector Weight.", default=None
    )
    consumer_cyclical: Optional[float] = Field(
        description="Consumer Cyclical Sector Weight.", default=None
    )
    consumer_defensive: Optional[float] = Field(
        description="Consumer Defensive Sector Weight.", default=None
    )
    financial_services: Optional[float] = Field(
        description="Financial Services Sector Weight.", default=None
    )
    technology: Optional[float] = Field(
        description="Technology Sector Weight.", default=None
    )
    health_care: Optional[float] = Field(
        description="Health Care Sector Weight.", default=None
    )
    communication_services: Optional[float] = Field(
        description="Communication Services Sector Weight.",
        alias="Communication Services",
        default=None,
    )
    utilities: Optional[float] = Field(
        description="Utilities Sector Weight.", default=None
    )
    real_estate: Optional[float] = Field(
        description="Real Estate Sector Weight.", default=None
    )
