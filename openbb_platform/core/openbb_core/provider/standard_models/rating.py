"""Rating Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class RatingQueryParams(QueryParams):
    """Rating Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class RatingData(Data):
    """Rating data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    rating: Optional[str] = Field(
        default=None, description="Overall rating of the stock."
    )
    rating_score: Optional[int] = Field(
        default=None, description="Overall rating score."
    )
    rating_recommendation: Optional[str] = Field(
        default=None, description="Overall recommendation based on the rating."
    )
    rating_details_dcf_score: Optional[int] = Field(
        default=None, description="Score based on DCF analysis."
    )
    rating_details_dcf_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on DCF score."
    )
    rating_details_roe_score: Optional[int] = Field(
        default=None, description="Score based on ROE analysis."
    )
    rating_details_roe_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on ROE score."
    )
    rating_details_roa_score: Optional[int] = Field(
        default=None, description="Score based on ROA analysis."
    )
    rating_details_roa_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on ROA score."
    )
    rating_details_de_score: Optional[int] = Field(
        default=None, description="Score based on DE (Debt to Equity) analysis."
    )
    rating_details_de_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on DE score."
    )
    rating_details_pe_score: Optional[int] = Field(
        default=None, description="Score based on PE (Price to Earnings) analysis."
    )
    rating_details_pe_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on PE score."
    )
    rating_details_pb_score: Optional[int] = Field(
        default=None, description="Score based on PB (Price to Book) analysis."
    )
    rating_details_pb_recommendation: Optional[str] = Field(
        default=None, description="Recommendation based on PB score."
    )
