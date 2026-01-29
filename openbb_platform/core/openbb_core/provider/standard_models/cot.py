"""交易者持仓报告标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class COTQueryParams(QueryParams):
    """交易者持仓报告查询。"""

    id: str = Field(
        description="CFTC 市场代码或其他标识字符串，例如合约市场名称、商品名称或商品组 - 即 'gold' 或 'japanese yen'。默认报告是联邦基金期货。使用 'cftc_market_code' 进行精确匹配。",
        default="045601",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " 默认为最近的报告。",
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class COTData(Data):
    """交易者持仓报告数据。
    返回的数据将根据查询而有所不同，此模型不会定义所有可能的字段。
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    report_week: str | None = Field(
        default=None, description="年度报告显示周。"
    )
    market_and_exchange_names: str | None = Field(
        default=None, description="市场和交易所名称。"
    )
    cftc_contract_market_code: str | None = Field(
        default=None, description="CFTC 合约市场代码。"
    )
    cftc_market_code: str | None = Field(default=None, description="CFTC 市场代码。")
    cftc_region_code: str | None = Field(default=None, description="CFTC 区域代码。")
    cftc_commodity_code: str | None = Field(
        default=None, description="CFTC 商品代码。"
    )
    cftc_contract_market_code_quotes: str | None = Field(
        default=None, description="CFTC 合约市场代码报价。"
    )
    cftc_market_code_quotes: str | None = Field(
        default=None, description="CFTC 市场代码报价。"
    )
    cftc_commodity_code_quotes: str | None = Field(
        default=None, description="CFTC 商品代码报价。"
    )
    cftc_subgroup_code: str | None = Field(
        default=None, description="CFTC 子组代码。"
    )
    commodity: str | None = Field(default=None, description="商品。")
    commodity_group: str | None = Field(
        default=None, description="商品组名称。"
    )
    commodity_subgroup: str | None = Field(
        default=None, description="商品子组名称。"
    )
    futonly_or_combined: str | None = Field(
        default=None, description="报告是仅期货还是合并报告。"
    )
    contract_units: str | None = Field(default=None, description="合约单位。")
