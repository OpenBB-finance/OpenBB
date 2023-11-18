"""Key Executives Standard Model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class KeyExecutivesQueryParams(QueryParams):
    """Key Executives Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class KeyExecutivesData(Data):
    """Key Executives Data."""

    title: str = Field(description="Designation of the key executive.")
    name: str = Field(description="Name of the key executive.")
    pay: Optional[StrictInt] = Field(
        default=None, description="Pay of the key executive."
    )
    currency_pay: str = Field(description="Currency of the pay.")
    gender: Optional[str] = Field(
        default=None, description="Gender of the key executive."
    )
    year_born: Optional[StrictInt] = Field(
        default=None, description="Birth year of the key executive."
    )
    title_since: Optional[StrictInt] = Field(
        default=None, description="Date the tile was held since."
    )
