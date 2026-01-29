"""出口目的地标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class ExportDestinationsQueryParams(QueryParams):
    """出口目的地查询。"""

    country: str = Field(description=QUERY_DESCRIPTIONS.get("country", ""))


class ExportDestinationsData(Data):
    """出口目的地数据。"""

    origin_country: str = Field(
        description="原产国。",
    )
    destination_country: str = Field(
        description="目的地国家。",
    )
    value: float | int = Field(
        description="出口额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
