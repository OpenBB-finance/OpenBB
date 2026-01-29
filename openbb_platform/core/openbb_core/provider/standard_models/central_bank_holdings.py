"""央行持仓标准模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CentralBankHoldingsQueryParams(QueryParams):
    """央行持仓查询。"""

    date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )


class CentralBankHoldingsData(Data):
    """央行持仓数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
