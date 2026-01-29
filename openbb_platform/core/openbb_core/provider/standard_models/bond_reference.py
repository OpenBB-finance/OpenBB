"""债券参考标准模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class BondReferenceQueryParams(QueryParams):
    """债券参考查询。"""

    country: str | None = Field(
        default=None,
        description="获取数据的国家。匹配部分名称。",
    )
    issuer_name: str | None = Field(
        default=None,
        description="发行人名称。返回部分匹配项，不区分大小写。",
    )
    isin: list | str | None = Field(
        default=None,
        description="债券的国际证券识别编码 (ISIN)。",
    )
    lei: str | None = Field(
        default=None,
        description="发行实体的法人识别编码 (LEI)。",
    )
    currency: list | str | None = Field(
        default=None,
        description="债券货币。格式为 3 字母 ISO 4217 代码（例如 GBP、EUR、USD）。",
    )
    coupon_min: float | None = Field(
        default=None,
        description="债券的最低票面利率。",
    )
    coupon_max: float | None = Field(
        default=None,
        description="债券的最高票面利率。",
    )
    issued_amount_min: int | None = Field(
        default=None,
        description="债券的最低发行金额。",
    )
    issued_amount_max: str | None = Field(
        default=None,
        description="债券的最高发行金额。",
    )
    maturity_date_min: dateType | None = Field(
        default=None,
        description="债券的最早到期日。",
    )
    maturity_date_max: dateType | None = Field(
        default=None,
        description="债券的最晚到期日。",
    )

    @field_validator("isin", "currency", "lei", mode="before", check_fields=False)
    @classmethod
    def validate_upper_case(cls, v):
        """将字段转换为大写并将列表转换为查询字符串。"""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None


class BondReferenceData(Data):
    """债券参考搜索数据。"""

    isin: str | None = Field(
        default=None,
        description="债券的国际证券识别编码 (ISIN)。",
    )
    lei: str | None = Field(
        default=None,
        description="发行实体的法人识别编码 (LEI)。",
    )
    figi: str | None = Field(default=None, description="债券的 FIGI。")
    cusip: str | None = Field(
        default=None,
        description="债券的 CUSIP。",
    )
    coupon_rate: float | None = Field(
        default=None,
        description="债券的票面利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
