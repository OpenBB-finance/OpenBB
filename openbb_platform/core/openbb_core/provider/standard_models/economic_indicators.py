"""经济指标标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class EconomicIndicatorsQueryParams(QueryParams):
    """经济指标查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    country: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("country", "")
    )
    frequency: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("frequency", "")
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class EconomicIndicatorsData(Data):
    """经济指标数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    symbol_root: str | None = Field(
        default=None, description="指标的根符号（例如 GDP）。"
    )
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str | None = Field(
        default=None, description="数据代表的国家。"
    )
    value: int | float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("value", "")
    )
