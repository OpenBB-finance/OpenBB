"""公司备案标准模型。"""

from datetime import (
    date as dateType,
)

from dateutil import parser
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class CompanyFilingsQueryParams(QueryParams):
    """公司备案查询。"""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str | list[str] | set[str]):
        """将字段转换为大写。"""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None


class CompanyFilingsData(Data):
    """公司备案数据。"""

    filing_date: dateType = Field(description="备案日期。")
    report_type: str | None = Field(default=None, description="备案类型。")
    report_url: str = Field(description="实际报告的 URL。")

    @field_validator("filing_date", "accepted_date", mode="before", check_fields=False)
    @classmethod
    def convert_date(cls, v: str):
        """将日期转换为日期类型。"""
        return parser.parse(str(v)).date() if v else None
