"""交易者持仓报告搜索标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CotSearchQueryParams(QueryParams):
    """交易者持仓报告搜索查询。"""

    query: str = Field(description="搜索查询。", default="")


class CotSearchData(Data):
    """交易者持仓报告搜索数据。"""

    code: str = Field(description="报告的 CFTC 市场合约代码。")
    name: str = Field(description="标的资产名称。")
    category: str | None = Field(
        default=None, description="标的资产类别。"
    )
    subcategory: str | None = Field(
        default=None, description="标的资产子类别。"
    )
    units: str | None = Field(default=None, description="一份合约的单位。")
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
