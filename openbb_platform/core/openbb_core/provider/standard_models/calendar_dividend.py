"""股息日历标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarDividendQueryParams(QueryParams):
    """股息日历查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class CalendarDividendData(Data):
    """股息日历数据。"""

    ex_dividend_date: dateType = Field(
        description="除息日 - 股票开始在没有股息权的情况下交易的日期。"
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    amount: float | None = Field(
        default=None, description="每股股息金额。"
    )
    name: str | None = Field(default=None, description="实体名称。")
    record_date: dateType | None = Field(
        default=None,
        description="所有权资格的登记日。",
    )
    payment_date: dateType | None = Field(
        default=None,
        description="股息支付日期。",
    )
    declaration_date: dateType | None = Field(
        default=None,
        description="股息宣告日期。",
    )
