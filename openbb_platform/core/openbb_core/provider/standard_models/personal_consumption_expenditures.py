"""Personal Consumption Expenditures Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class PersonalConsumptionExpendituresQueryParams(QueryParams):
    """Personal Consumption Expenditures Query."""

    date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " Default is the latest report.",
    )


class PersonalConsumptionExpendituresData(Data):
    """Personal Consumption Expenditures Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    value: float = Field(description=DATA_DESCRIPTIONS.get("value", ""))
