"""Analyst ratings Standard Model."""


from pydantic import Field, NonNegativeInt

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class AnalystRatingsQueryParams(QueryParams):
    """Analyst ratings Query."""

    # symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    # symbols: str = Field(
    #     min_length=1,
    #     description=DATA_DESCRIPTIONS.get("symbols", "")
    #     + " Comma separated list of symbols.",
    # )
    limit: NonNegativeInt = Field(
        default=20, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    # @field_validator("symbol", mode="before", check_fields=False)
    # @classmethod
    # def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
    #     """Convert symbol to uppercase."""
    #     if isinstance(v, str):
    #         return v.upper()
    #     return ",".join([symbol.upper() for symbol in list(v)])


class AnalystRatingsData(Data):
    """Analyst ratings Data."""

    # symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    # target_high: Optional[float] = Field(
    #     default=None, description="High target of the analyst ratings."
    # )
    # target_low: Optional[float] = Field(
    #     default=None, description="Low target of the analyst ratings."
    # )
    # target_consensus: Optional[float] = Field(
    #     default=None, description="Consensus target of the analyst ratings."
    # )
    # target_median: Optional[float] = Field(
    #     default=None, description="Median target of the analyst ratings."
    # )

    # @field_validator("symbol", mode="before", check_fields=False)
    # @classmethod
    # def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
    #     """Convert symbol to uppercase."""
    #     if isinstance(v, str):
    #         return v.upper()
    #     return ",".join([symbol.upper() for symbol in list(v)])
