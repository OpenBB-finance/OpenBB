"""High Quality Market Corporate Bond Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Optional, Union

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HighQualityMarketCorporateBondQueryParams(QueryParams):
    """High Quality Market Corporate Bond Query."""

    date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )


class HighQualityMarketCorporateBondData(Data):
    """High Quality Market Corporate Bond Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="Interest rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    maturity: str = Field(description="Maturity.")
