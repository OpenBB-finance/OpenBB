"""指数行业标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class IndexSectorsQueryParams(QueryParams):
    """指数行业查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class IndexSectorsData(Data):
    """指数行业数据。"""

    sector: str = Field(description="行业名称。")
    weight: float = Field(description="该行业在指数中的权重。")
