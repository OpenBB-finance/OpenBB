"""ETF Sectors data model."""

from typing import List, Literal, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfSectorsQueryParams(QueryParams):
    """ETF Sectors Query Params"""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")
    scope: Optional[Literal["sector", "country"]] = Field(
        description="""
            The scope of the query.

            sector: The weighting by sector/industry of the ETF.
            country: The weighting by country/region of the ETF.
            """,
        default="sector",
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfSectorsData(Data):
    """ETF Sectors Data."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")
