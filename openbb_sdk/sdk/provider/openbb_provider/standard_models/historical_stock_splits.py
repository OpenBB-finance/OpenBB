"""Historical Stock Splits data model."""


from datetime import date as dateType

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class HistoricalStockSplitsQueryParams(QueryParams, BaseSymbol):
    """Historical Stock Splits Query."""


class HistoricalStockSplitsData(Data):
    """Historical Stock Splits Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    label: str = Field(description="Label of the historical stock splits.")
    numerator: float = Field(description="Numerator of the historical stock splits.")
    denominator: float = Field(
        description="Denominator of the historical stock splits."
    )
