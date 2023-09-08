"""Key Executives Data Model."""


from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class KeyExecutivesQueryParams(QueryParams):
    """Key Executives Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class KeyExecutivesData(Data):
    """Key Executives Data."""

    title: str = Field(description="Designation of the key executive.")
    name: str = Field(description="Name of the key executive.")
    pay: Optional[int] = Field(description="Pay of the key executive.")
    currency_pay: str = Field(description="Currency of the pay.")
    gender: Optional[str] = Field(description="Gender of the key executive.")
    year_born: Optional[str] = Field(description="Birth year of the key executive.")
    title_since: Optional[int] = Field(description="Date the tile was held since.")
