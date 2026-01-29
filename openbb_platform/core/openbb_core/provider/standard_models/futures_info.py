"""期货信息标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class FuturesInfoQueryParams(QueryParams):
    """期货信息查询。"""

    # leaving this empty to let the provider create custom symbol docstrings.


class FuturesInfoData(Data):
    """期货信息数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
