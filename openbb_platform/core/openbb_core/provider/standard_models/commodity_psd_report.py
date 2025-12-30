"""Commodity Production Supply & Demand Report Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CommodityPsdReportQueryParams(QueryParams):
    """Commodity Production Supply & Demand Report Query."""

    commodity: str = Field(
        description="Commodity for the report.",
    )
    year: int = Field(
        description="Year of the data.",
    )
    month: int = Field(
        description="Month of the data.",
        ge=1,
        le=12,
    )


class CommodityPsdReportData(Data):
    """Commodity Production Supply & Demand Report Data."""

    content: str = Field(
        description="Base64 encoded content.",
    )
