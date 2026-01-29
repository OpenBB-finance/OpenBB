"""内幕交易标准模型。"""

from datetime import (
    date as dateType,
    datetime,
    time,
)

from dateutil import parser
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class InsiderTradingQueryParams(QueryParams):
    """内幕交易查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class InsiderTradingData(Data):
    """内幕交易数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    company_cik: str | None = Field(
        default=None,
        description="公司的 CIK 编号。",
        coerce_numbers_to_str=True,
    )
    filing_date: dateType | datetime | None = Field(
        default=None, description="交易申报日期。"
    )
    transaction_date: dateType | None = Field(
        default=None, description="交易日期。"
    )
    owner_cik: int | str | None = Field(
        default=None, description="报告个人的 CIK。"
    )
    owner_name: str | None = Field(
        default=None, description="报告个人的姓名。"
    )
    owner_title: str | None = Field(
        default=None, description="报告个人拥有的职位。"
    )
    ownership_type: str | None = Field(
        default=None, description="所有权类型，例如：直接或间接。"
    )
    transaction_type: str | None = Field(
        default=None, description="正在报告的交易类型。"
    )
    acquisition_or_disposition: str | None = Field(
        default=None, description="股票的取得或处置。"
    )
    security_type: str | None = Field(
        default=None, description="交易的证券类型。"
    )
    securities_owned: float | None = Field(
        default=None,
        description="报告个人拥有的证券数量。",
    )
    securities_transacted: float | None = Field(
        default=None,
        description="报告个人交易的证券数量。",
    )
    transaction_price: float | None = Field(
        default=None, description="交易价格。"
    )
    filing_url: str | None = Field(default=None, description="申报文件链接。")

    @field_validator(
        "filing_date", "transaction_date", mode="before", check_fields=False
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """返回格式化的日期时间。"""
        if v:
            filing_date = parser.isoparse(str(v))
            if filing_date.time() == time(0, 0):
                return filing_date.date()
            return filing_date
        return None
