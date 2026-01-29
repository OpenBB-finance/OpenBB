"""股票 FTD 标准模型。"""

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


class EquityFtdQueryParams(QueryParams):
    """股票 FTD 查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class EquityFtdData(Data):
    """股票 FTD 数据。"""

    settlement_date: dateType | None = Field(
        description="失败的结算日期。", default=None
    )
    symbol: str | None = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
        default=None,
    )
    cusip: str | None = Field(
        description="证券的 CUSIP。",
        default=None,
    )
    quantity: int | None = Field(
        description="该结算日的失败数量。",
        default=None,
    )
    price: float | None = Field(
        description="结算日前一收盘价的价格。",
        default=None,
    )
    description: str | None = Field(
        description="证券的描述。",
        default=None,
    )

    @field_validator("settlement_date", mode="before")
    def date_validate(cls, v):  # pylint: disable=E0213
        """将日期作为 datetime 对象返回。"""
        return datetime.strftime(v, "%Y-%m-%d")
