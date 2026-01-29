"""股票信息标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityInfoQueryParams(QueryParams):
    """股票信息查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EquityInfoData(Data):
    """股票信息数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="公司的通用名称。")
    cik: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    cusip: str | None = Field(
        default=None, description="公司的 CUSIP 标识符。"
    )
    isin: str | None = Field(
        default=None, description="国际证券识别码。"
    )
    lei: str | None = Field(
        default=None, description="分配给公司的法人实体标识符。"
    )
    legal_name: str | None = Field(
        default=None, description="公司的正式法定名称。"
    )
    stock_exchange: str | None = Field(
        default=None, description="公司交易的证券交易所。"
    )
    sic: int | None = Field(
        default=None,
        description="公司的标准行业分类代码。",
    )
    short_description: str | None = Field(
        default=None, description="公司简介。"
    )
    long_description: str | None = Field(
        default=None, description="公司详细描述。"
    )
    ceo: str | None = Field(
        default=None, description="公司首席执行官。"
    )
    company_url: str | None = Field(
        default=None, description="公司网站的 URL。"
    )
    business_address: str | None = Field(
        default=None, description="公司总部地址。"
    )
    mailing_address: str | None = Field(
        default=None, description="公司的邮寄地址。"
    )
    business_phone_no: str | None = Field(
        default=None, description="公司总部的电话号码。"
    )
    hq_address1: str | None = Field(
        default=None, description="公司总部地址。"
    )
    hq_address2: str | None = Field(
        default=None, description="公司总部地址。"
    )
    hq_address_city: str | None = Field(
        default=None, description="公司总部所在城市。"
    )
    hq_address_postal_code: str | None = Field(
        default=None, description="公司总部的邮政编码。"
    )
    hq_state: str | None = Field(
        default=None, description="公司总部所在的州。"
    )
    hq_country: str | None = Field(
        default=None, description="公司总部所在的国家。"
    )
    inc_state: str | None = Field(
        default=None, description="公司注册成立的州。"
    )
    inc_country: str | None = Field(
        default=None, description="公司注册成立的国家。"
    )
    employees: int | None = Field(
        default=None, description="公司员工人数。"
    )
    entity_legal_form: str | None = Field(
        default=None, description="公司的法律形式。"
    )
    entity_status: str | None = Field(
        default=None, description="公司状态。"
    )
    latest_filing_date: dateType | None = Field(
        default=None, description="公司最新备案的日期。"
    )
    irs_number: str | None = Field(
        default=None, description="分配给公司的 IRS 编号。"
    )
    sector: str | None = Field(
        default=None, description="公司经营的部门。"
    )
    industry_category: str | None = Field(
        default=None, description="公司经营的行业类别。"
    )
    industry_group: str | None = Field(
        default=None, description="公司经营的行业组。"
    )
    template: str | None = Field(
        default=None,
        description="用于标准化公司财务报表的模板。",
    )
    standardized_active: bool | None = Field(
        default=None, description="公司是否活跃。"
    )
    first_fundamental_date: dateType | None = Field(
        default=None, description="公司首次基本面的日期。"
    )
    last_fundamental_date: dateType | None = Field(
        default=None, description="公司最后一次基本面的日期。"
    )
    first_stock_price_date: dateType | None = Field(
        default=None, description="公司首次股价的日期。"
    )
    last_stock_price_date: dateType | None = Field(
        default=None, description="公司最后一次股价的日期。"
    )
