"""High Quality Market Corporate Bond Model."""
from datetime import (
    date as dateType,
)
from typing import List, Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class HighQualityMarketCorporateBondParams(QueryParams):
    """HighQualityMarketCorporateBond Query."""

    date: Optional[dateType] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    yield_curve: List[Literal["spot", "par"]] = Field(
        default=["spot"],
        description="The yield curve type.",
    )


class HighQualityMarketCorporateBondData(Data):
    """HighQualityMarketCorporateBond Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(description="HighQualityMarketCorporateBond Rate.")
    maturity: str = Field(description="Maturity.")
    yield_curve: Literal["spot", "par"] = Field(description="The yield curve type.")
