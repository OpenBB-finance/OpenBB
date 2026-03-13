"""Money Measures Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import AliasGenerator, ConfigDict, Field


class MoneyMeasuresQueryParams(QueryParams):
    """Treasury Rates Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    adjusted: bool | None = Field(
        default=True, description="Whether to return seasonally adjusted data."
    )


class MoneyMeasuresData(Data):
    """Money Measures Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.refetchInterval": False,
            }
        },
        alias_generator=AliasGenerator(
            serialization_alias=lambda x: x,
        ),
    )

    month: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    m1: float = Field(
        description="Value of the M1 money supply in billions.",
        json_schema_extra={
            "x-widget_config": {"prefix": "$", "suffix": "B", "headerName": "M1"}
        },
    )
    m2: float = Field(
        description="Value of the M2 money supply in billions.",
        json_schema_extra={
            "x-widget_config": {"prefix": "$", "suffix": "B", "headerName": "M2"}
        },
    )
    currency: float | None = Field(
        description="Value of currency in circulation in billions.",
        default=None,
        json_schema_extra={"x-widget_config": {"prefix": "$", "suffix": "B"}},
    )
    demand_deposits: float | None = Field(
        description="Value of demand deposits in billions.",
        default=None,
        json_schema_extra={"x-widget_config": {"prefix": "$", "suffix": "B"}},
    )
    retail_money_market_funds: float | None = Field(
        description="Value of retail money market funds in billions.",
        default=None,
        json_schema_extra={"x-widget_config": {"prefix": "$", "suffix": "B"}},
    )
    other_liquid_deposits: float | None = Field(
        description="Value of other liquid deposits in billions.",
        default=None,
        json_schema_extra={"x-widget_config": {"prefix": "$", "suffix": "B"}},
    )
    small_denomination_time_deposits: float | None = Field(
        description="Value of small denomination time deposits in billions.",
        default=None,
        json_schema_extra={"x-widget_config": {"prefix": "$", "suffix": "B"}},
    )
