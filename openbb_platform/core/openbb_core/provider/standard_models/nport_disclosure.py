"""N-PORT 披露标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class NportDisclosureQueryParams(QueryParams):
    """N-PORT 披露查询。"""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + "（基金代码或 CIK）"
    )
    year: int | None = Field(
        default=None,
        description="申报文件的报告年度。默认是最近报告季度的年份。",
    )
    quarter: int | None = Field(
        default=None,
        description="申报文件的报告季度。默认是最近报告的季度。",
    )

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class NportDisclosureData(Data):
    """N-PORT 披露数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: str | None = Field(
        default=None,
        description="资产名称。",
    )
    title: str | None = Field(
        default=None,
        description="资产标题。",
    )
    cusip: str | None = Field(
        default=None,
        description="持仓的 CUSIP 编码。",
        coerce_numbers_to_str=True,
    )
    lei: str | None = Field(
        default=None,
        description="持仓的 LEI（法人团体识别码）。",
        coerce_numbers_to_str=True,
    )
    isin: str | None = Field(
        default=None,
        description="持仓的 ISIN 编码。",
        coerce_numbers_to_str=True,
    )
    other_id: str | None = Field(
        description="持仓的内部标识符。", default=None
    )
    is_restricted: str | None = Field(
        description="该持仓是否受限。",
        default=None,
    )
    fair_value_level: int | None = Field(
        description="持仓的公允价值等级。",
        default=None,
    )
    is_cash_collateral: str | None = Field(
        description="该持仓是否为现金质押物。",
        default=None,
    )
    is_non_cash_collateral: str | None = Field(
        description="该持仓是否为非现金质押物。",
        default=None,
    )
    is_loan_by_fund: str | None = Field(
        description="该持仓是否为基金贷款。",
        default=None,
    )
    loan_value: float | None = Field(
        description="持仓的贷款价值。",
        default=None,
    )
    issuer_conditional: str | None = Field(
        description="持仓的发行人条件。", default=None
    )
    asset_conditional: str | None = Field(
        description="持仓的资产条件。", default=None
    )
    payoff_profile: str | None = Field(
        description="持仓的收益曲线。",
        default=None,
    )
    asset_category: str | None = Field(
        description="持仓的资产类别。", default=None
    )
    issuer_category: str | None = Field(
        description="持仓的发行人类别。",
        default=None,
    )
    country: str | None = Field(description="持仓所属国家。", default=None)
    balance: int | float | None = Field(
        description="持仓余额（以股或单位计）。", default=None
    )
    units: int | float | str | None = Field(
        description="单位类型。", default=None
    )
    currency: str | None = Field(
        description="持仓的货币。", default=None
    )
    value: int | float | None = Field(
        description="持仓价值（以美元计）。",
        default=None,
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    weight: float | None = Field(
        description="持仓权重（以归一化百分比计）。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
