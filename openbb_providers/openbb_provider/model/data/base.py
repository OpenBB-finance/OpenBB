# IMPORT STANDARD
from typing import Literal

# IMPORT THIRD-PARTY
from pydantic import BaseModel, Field, validator

# IMPORT INTERNAL
from openbb_provider.metadata import DESCRIPTIONS
from openbb_provider.model.abstract.data import QueryParams


class BaseSymbol(BaseModel):
    symbol: str = Field(min_length=1, description=DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True)
    def upper_symbol(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class FinancialStatementQueryParams(QueryParams, BaseSymbol):
    __name__ = "FinancialStatementQueryParams"
    period: Literal["annually", "quarterly"] = Field(
        default="annually", description=DESCRIPTIONS.get("period", "")
    )
