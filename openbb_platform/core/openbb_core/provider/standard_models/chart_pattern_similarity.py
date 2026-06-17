"""Chart Pattern Similarity Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, PositiveInt, field_validator


class ChartPatternSimilarityQueryParams(QueryParams):
    """Chart Pattern Similarity Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description="Reference date for the source chart pattern.")
    timeframe: (
        Literal["rth", "premarket", "rth_3d", "rth_5d", "rth_10d", "auto"] | str
    ) = Field(
        default="rth",
        description="Timeframe to use for the pattern search.",
    )
    limit: PositiveInt | None = Field(
        default=None,
        le=50,
        description="Maximum number of similar historical patterns to return.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("timeframe", mode="before", check_fields=False)
    @classmethod
    def normalize_timeframe(cls, v: str) -> str:
        """Normalize timeframe values."""
        return str(v).lower()


class ChartPatternSimilarityData(Data):
    """Chart Pattern Similarity Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType | datetime = Field(
        description="Date of the matched historical chart pattern."
    )
    rank: int | None = Field(
        default=None,
        description="Similarity rank of the matched pattern.",
    )
    distance: float | None = Field(
        default=None,
        description="Embedding distance or provider-supplied distance score.",
    )
    similarity_score: float | None = Field(
        default=None,
        description="Provider-supplied similarity score, when available.",
    )
    timeframe: str | None = Field(
        default=None,
        description="Timeframe used for the pattern match.",
    )
    forward_return_1d: float | None = Field(
        default=None,
        description="Forward return one trading day after the matched pattern.",
    )
    forward_return_3d: float | None = Field(
        default=None,
        description="Forward return three trading days after the matched pattern.",
    )
    forward_return_5d: float | None = Field(
        default=None,
        description="Forward return five trading days after the matched pattern.",
    )
    forward_return_10d: float | None = Field(
        default=None,
        description="Forward return ten trading days after the matched pattern.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def data_to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return formatted date."""
        # pylint: disable=import-outside-toplevel
        from dateutil import parser

        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
