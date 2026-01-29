"""高级信贷官意见调查 (SLOOS) 标准模型。"""

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


class SeniorLoanOfficerSurveyQueryParams(QueryParams):
    """高级信贷官意见调查 (SLOOS) 查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class SeniorLoanOfficerSurveyData(Data):
    """高级信贷官意见调查 (SLOOS) 数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    value: float = Field(description="调查分值。")
    title: str | None = Field(description="调查标题。")
