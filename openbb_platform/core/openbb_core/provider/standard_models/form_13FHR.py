"""13F-HR 表格标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class Form13FHRQueryParams(QueryParams):
    """13F-HR 表格查询。"""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " 可以使用 CIK 或股票代码。"
    )
    date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " 该日期代表报告期的结束。"
        + " 所有 13F-HR 表格备案均基于日历年，"
        + " 并且按季度报告。"
        + " 如果未提供日期，则返回最近的备案。"
        + " 支持从 2013-06-30 开始的提交。",
    )
    limit: int | None = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " 要返回的先前备案数量。"
        + " 日期参数优先于此参数。",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return str(v).upper()


class Form13FHRData(Data):
    """
    13F-HR 表格数据。

    有关备案的详细文档可以在此处找到：
    https://www.sec.gov/pdf/form13f.pdf
    """

    period_ending: dateType = Field(
        description="备案的季度末日期。"
    )
    issuer: str = Field(description="发行人名称。")
    cusip: str = Field(description="证券的 CUSIP 码。")
    asset_class: str = Field(
        description="证券资产类别的标题。"
    )
    security_type: Literal["SH", "PRN"] | None = Field(
        default=None,
        description="本金额代表的是股份数量还是该类证券的本金额。"
        + " 'SH' 代表股份。'PRN' 代表本金额。"
        + " 可转换债券报告为 'PRN'。",
    )
    option_type: Literal["call", "put"] | None = Field(
        default=None,
        description="当所报告的持仓为认沽或认购期权时定义。"
        + " 仅报告多头头寸。",
    )
    investment_discretion: str | None = Field(
        default=None,
        description="经理持有的投资决策权。"
        + " 唯一 (Sole)、共享定义的 (DFN) 或共享其他的 (OTR)。",
    )
    voting_authority_sole: int | None = Field(
        default=None,
        description="经理行使唯一投票权的股份数量。",
    )
    voting_authority_shared: int | None = Field(
        default=None,
        description="经理行使定义的共享投票权的股份数量。",
    )
    voting_authority_none: int | None = Field(
        default=None,
        description="经理不行使投票权的股份数量。",
    )
    principal_amount: int = Field(
        description="该类证券的总股数或该类证券的本金额。由 'security_type' 定义。仅报告多头头寸。"
    )
    value: int = Field(
        description="该特定类别证券持仓的公允市场价值。"
        + " 期权报告的价值是相对于受控股份数量的标的证券的公允市场价值。"
        + " 价值四舍五入到最近的美元，"
        + " 并使用日历年或季度最后一个交易日的收盘价。",
    )

    @field_validator("option_type", mode="before", check_fields=False)
    @classmethod
    def validate_option_type(cls, v: str):
        """验证并转换为小写。"""
        return v.lower() if v else None
