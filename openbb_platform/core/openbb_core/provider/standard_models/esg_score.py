"""ESG 评分标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EsgScoreQueryParams(QueryParams):
    """ESG 评分查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EsgScoreData(Data):
    """ESG 评分数据。"""

    period_ending: dateType = Field(description="报告的截止日期。")
    disclosure_date: dateType | datetime | None = Field(
        description="报告提交日期。"
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
        coerce_numbers_to_str=True,
    )
    company_name: str | None = Field(
        default=None, description="公司名称。"
    )
    form_type: str | None = Field(
        default=None, description="进行披露的表格类型。"
    )
    environmental_score: float = Field(
        description="公司的环境评分。"
    )
    social_score: float = Field(description="公司的社会评分。")
    governance_score: float = Field(description="公司的治理评分。")
    esg_score: float = Field(description="公司的 ESG 评分。")
    url: str | None = Field(default=None, description="报告或备案的 URL。")
