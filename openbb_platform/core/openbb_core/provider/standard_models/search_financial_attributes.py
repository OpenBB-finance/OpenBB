"""搜索财务属性标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class SearchFinancialAttributesQueryParams(QueryParams):
    """搜索财务属性查询。"""

    query: str = Field(description="要搜索的查询词。")
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))


class SearchFinancialAttributesData(Data):
    """搜索财务属性数据。"""

    id: str = Field(description="财务属性的 ID。")
    name: str = Field(description="财务属性的名称。")
    tag: str = Field(description="财务属性的标签。")
    statement_code: str = Field(description="财务报表代码。")
    statement_type: str | None = Field(
        default=None, description="财务报表类型。"
    )
    parent_name: str | None = Field(
        default=None, description="财务属性的父级名称。"
    )
    sequence: int | None = Field(
        default=None, description="财务报表的顺序。"
    )
    factor: str | None = Field(
        default=None, description="财务属性的倍数因子。"
    )
    transaction: str | None = Field(
        default=None,
        description="财务属性的交易类型（贷记/借记）。",
    )
    type: str | None = Field(
        default=None, description="财务属性的类型。"
    )
    unit: str | None = Field(
        default=None, description="财务属性的单位。"
    )
