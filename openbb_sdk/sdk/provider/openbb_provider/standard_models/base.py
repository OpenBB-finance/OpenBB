"""Base models for OpenBB Provider."""
from typing import List, Literal, Optional, Set, Union

from pydantic import BaseModel, Field, NonNegativeInt, validator

from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class BaseSymbol(BaseModel):
    """Base model for symbol query params."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FinancialStatementQueryParams(QueryParams, BaseSymbol):
    """Base model for financial statement query params."""

    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
