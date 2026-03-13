"""Key Executives Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class KeyExecutivesQueryParams(QueryParams):
    """Key Executives Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class KeyExecutivesData(Data):
    """Key Executives Data."""

    title: str = Field(description="Designation of the key executive.")
    name: str = Field(description="Name of the key executive.")
    pay: int | None = Field(default=None, description="Pay of the key executive.")
    currency_pay: str | None = Field(default=None, description="Currency of the pay.")
    gender: str | None = Field(default=None, description="Gender of the key executive.")
    year_born: int | None = Field(
        default=None, description="Birth year of the key executive."
    )
