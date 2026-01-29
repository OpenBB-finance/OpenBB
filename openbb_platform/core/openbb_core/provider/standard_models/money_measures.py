"""货币供应量标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class MoneyMeasuresQueryParams(QueryParams):
    """货币供应量查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    adjusted: bool | None = Field(
        default=True, description="是否返回季节性调整后的数据。"
    )


class MoneyMeasuresData(Data):
    """货币供应量数据。"""

    month: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    M1: float = Field(description="M1 货币供应量（单位：十亿）。")
    M2: float = Field(description="M2 货币供应量（单位：十亿）。")
    currency: float | None = Field(
        description="流通中货币价值（单位：十亿）。", default=None
    )
    demand_deposits: float | None = Field(
        description="活期存款价值（单位：十亿）。", default=None
    )
    retail_money_market_funds: float | None = Field(
        description="零售货币市场基金价值（单位：十亿）。", default=None
    )
    other_liquid_deposits: float | None = Field(
        description="其他流动性存款价值（单位：十亿）。", default=None
    )
    small_denomination_time_deposits: float | None = Field(
        description="小额定期存款价值（单位：十亿）。",
        default=None,
    )
