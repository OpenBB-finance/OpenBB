"""Short Term Energy Outlook Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ShortTermEnergyOutlookQueryParams(QueryParams):
    """Short Term Energy Outlook Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class ShortTermEnergyOutlookData(Data):
    """Short Term Energy Outlook Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    table: Optional[str] = Field(default=None, description="Table name for the data.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    order: Optional[int] = Field(
        default=None, description="Presented order of the data, relative to the table."
    )
    title: Optional[str] = Field(default=None, description="Title of the data.")
    value: Union[int, float] = Field(description="Value of the data.")
    unit: Optional[str] = Field(default=None, description="Unit or scale of the data.")
