from typing import Literal, Optional

from pydantic import BaseModel, Field, NonNegativeInt, validator

from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.descriptions import QUERY_DESCRIPTIONS


class BaseSymbol(BaseModel):
    symbol: str = Field(min_length=1, description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True)
    def upper_symbol(cls, v: str):  # pylint: disable=E0213
        return v.upper()


class FinancialStatementQueryParams(QueryParams, BaseSymbol):
    period: Literal["annually", "quarterly"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=1, description="The limit of the income statement."
    )
