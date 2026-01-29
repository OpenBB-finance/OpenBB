"""交易者持仓报告 (COT) 搜索标准模型。"""

from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SymbolMapQueryParams(QueryParams):
    """交易者持仓报告 (COT) 搜索查询。"""

    query: str = Field(description="搜索查询词。")
    use_cache: bool | None = Field(
        default=True,
        description="是否使用缓存。如果为 True，缓存将存储七天。",
    )
