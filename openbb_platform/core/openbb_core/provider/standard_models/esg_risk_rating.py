"""ESG 风险评级标准模型。"""

from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ESGRiskRatingQueryParams(QueryParams):
    """ESG 风险评级查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class ESGRiskRatingData(Data):
    """ESG 风险评级数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    company_name: str = Field(description="公司名称。")
    industry: str = Field(description="公司所属行业。")
    year: int = Field(description="ESG 风险评级的年份。")
    esg_risk_rating: Literal[
        "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
    ] = Field(description="公司的 ESG 风险评级。")
    industry_rank: str = Field(description="公司的行业排名。")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str | list[str] | set[str]):
        """将字段转换为大写。"""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
