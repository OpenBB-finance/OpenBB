"""远期 PE 预测标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ForwardPeEstimatesQueryParams(QueryParams):
    """远期 PE 预测查询参数。"""

    symbol: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["symbol"],
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """将字段转换为大写。"""
        return v.upper() if v else None


class ForwardPeEstimatesData(Data):
    """远期 PE 预测数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="实体名称。")
    year1: float | None = Field(
        default=None,
        description="下一财政年度的预测 PE 比率。",
    )
    year2: float | None = Field(
        default=None,
        description="两个财政年度后的预测 PE 比率。",
    )
    year3: float | None = Field(
        default=None,
        description="三个财政年度后的预测 PE 比率。",
    )
    year4: float | None = Field(
        default=None,
        description="四个财政年度后的预测 PE 比率。",
    )
    year5: float | None = Field(
        default=None,
        description="五个财政年度后的预测 PE 比率。",
    )
