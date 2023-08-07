from typing import Literal, Optional

from pydantic import field_validator, BaseModel, Field, NonNegativeInt

from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class BaseSymbol(BaseModel):
    symbol: str = Field(min_length=1, description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before")
    @classmethod
    def upper_symbol(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class FinancialStatementQueryParams(QueryParams, BaseSymbol):
    period: Literal["annually", "quarterly"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=200, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
