"""Money Measures Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class MoneyMeasuresQueryParams(QueryParams):
    """Treasury Rates Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    adjusted: Optional[bool] = Field(
        default=True, description="Whether to return seasonally adjusted data."
    )


class MoneyMeasuresData(Data):
    """Money Measures Data."""

    month: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    M1: float = Field(description="Value of the M1 money supply in billions.")
    M2: float = Field(description="Value of the M2 money supply in billions.")
    currency: Optional[float] = Field(
        description="Value of currency in circulation in billions.", default=None
    )
    demand_deposits: Optional[float] = Field(
        description="Value of demand deposits in billions.", default=None
    )
    retail_money_market_funds: Optional[float] = Field(
        description="Value of retail money market funds in billions.", default=None
    )
    other_liquid_deposits: Optional[float] = Field(
        description="Value of other liquid deposits in billions.", default=None
    )
    small_denomination_time_deposits: Optional[float] = Field(
        description="Value of small denomination time deposits in billions.",
        default=None,
    )
