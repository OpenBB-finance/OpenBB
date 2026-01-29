"""海上咽喉点过境呼叫和贸易额估算时间序列。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class MaritimeChokePointVolumeQueryParams(QueryParams):
    """海上咽喉点运量查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class MaritimeChokePointVolumeData(Data):
    """海上咽喉点运量数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
