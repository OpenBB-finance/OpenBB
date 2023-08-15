from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, NonNegativeInt, validator

from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class BaseSymbol(BaseModel):
    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], set[str]]):
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FinancialStatementQueryParams(QueryParams, BaseSymbol):
    period: Literal["annually", "quarterly"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
