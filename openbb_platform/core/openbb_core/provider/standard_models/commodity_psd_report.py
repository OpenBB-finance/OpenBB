"""Commodity Production Supply & Distribution Report Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CommodityPsdReportQueryParams(QueryParams):
    """Commodity Production Supply & Distribution Report Query."""

    commodity: str = Field(
        description="Commodity for the report.",
    )
    year: int = Field(
        description="Year of the report.",
    )
    month: int = Field(
        description="Month of the report.",
        ge=1,
        le=12,
    )


class CommodityPsdReportData(Data):
    """Commodity Production Supply & Distribution Report Data."""

    content: str = Field(
        description="Base64 encoded content.",
    )
