"""Key Executives Data Model."""


from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class KeyExecutivesQueryParams(QueryParams, BaseSymbol):
    """Key Executives Query."""


class KeyExecutivesData(Data):
    """Key Executives Data."""

    title: str = Field(description="Designation of the key executive.")
    name: str = Field(description="Name of the key executive.")
    pay: Optional[int] = Field(description="Pay of the key executive.")
    currency_pay: str = Field(description="Currency of the pay.")
    gender: Optional[str] = Field(description="Gender of the key executive.")
    year_born: Optional[str] = Field(description="Birth year of the key executive.")
    title_since: Optional[int] = Field(description="Date the tile was held since.")
