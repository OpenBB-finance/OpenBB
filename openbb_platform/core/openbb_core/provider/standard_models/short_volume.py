"""卖空成交量标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ShortVolumeQueryParams(QueryParams):
    """卖空成交量查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))


class ShortVolumeData(Data):
    """卖空成交量数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )

    market: str | None = Field(
        default=None,
        description="报告机构 ID。N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF",
    )

    short_volume: int | None = Field(
        default=None,
        description=(
            "常规交易时段内卖空成交以及卖空豁免成交的累计报告股份量"
        ),
    )

    short_exempt_volume: int | None = Field(
        default=None,
        description="常规交易时段内卖空豁免成交的累计报告股份量",
    )

    total_volume: int | None = Field(
        default=None,
        description="常规交易时段内的累计报告股份成交量",
    )
