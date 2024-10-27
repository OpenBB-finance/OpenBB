"""DeFiLlama Revenue Overview Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from defillama import fees_revenue
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaRevenueOverviewQueryParams(QueryParams):
    """DeFiLlama Revenue Overview Query.

    Source: https://defillama.com/docs/api
    """

    chain: Optional[str] = Field(
        default=None, description="The chain to fetch data for."
    )
    all: bool = Field(
        default=False, description="Whether to fetch details of all protocols."
    )
    # NOTE: Disabled since the API does not return any data
    # aggregate: Literal["daily", "total"] = Field(
    #     default="daily",
    #     description="Whether to fetch daily or total aggregate data.",
    # )


class DeFiLlamaChainsBreakdownData(Data):
    """DeFiLlama Chains Breakdown Data."""

    date: datetime = Field(description="The date of the data.")
    chains: Dict[str, int] = Field(description="The chains data.")

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaProtocolsData(Data):
    """DeFiLlama Protocols Data."""

    total_24h: Optional[int] = Field(
        default=None, description="Total value in the last 24 hours", alias="total24h"
    )
    total_48h_to_24h: Optional[int] = Field(
        default=None,
        description="Total value from 48 to 24 hours ago",
        alias="total48hto24h",
    )
    total_7d: Optional[int] = Field(
        default=None, description="Total value in the last 7 days", alias="total7d"
    )
    total_14d_to_7d: Optional[int] = Field(
        default=None,
        description="Total value from 14 to 7 days ago",
        alias="total14dto7d",
    )
    total_60d_to_30d: Optional[int] = Field(
        default=None,
        description="Total value from 60 to 30 days ago",
        alias="total60dto30d",
    )
    total_30d: Optional[int] = Field(
        default=None, description="Total value in the last 30 days", alias="total30d"
    )
    total_1y: Optional[int] = Field(
        default=None, description="Total value in the last year", alias="total1y"
    )
    total_all_time: Optional[float] = Field(
        default=None, description="Total value of all time", alias="totalAllTime"
    )
    average_1y: Optional[float] = Field(
        default=None, description="Average value over the last year", alias="average1y"
    )
    change_1d: Optional[float] = Field(
        default=None, description="Percentage change in the last day"
    )
    change_7d: Optional[float] = Field(
        default=None, description="Percentage change in the last 7 days"
    )
    change_1m: Optional[float] = Field(
        default=None, description="Percentage change in the last month"
    )
    change_7d_over_7d: Optional[float] = Field(
        default=None,
        description="Percentage change over the last two 7-day periods",
        alias="change_7dover7d",
    )
    change_30d_over_30d: Optional[float] = Field(
        default=None,
        description="Percentage change over the last two 30-day periods",
        alias="change_30dover30d",
    )
    breakdown_24h: Optional[Dict[str, Dict[str, int]]] = Field(
        default=None,
        description="Breakdown of values in the last 24 hours",
        alias="breakdown24h",
    )
    defillama_id: int = Field(description="DeFiLlama ID", alias="defillamaId")
    name: str = Field(description="Name of the chain or protocol")
    display_name: str = Field(
        description="Display name of the chain or protocol", alias="displayName"
    )
    module: str = Field(description="Module name")
    category: str = Field(description="Category of the chain or protocol")
    logo: str = Field(description="URL to the logo image")
    chains: List[str] = Field(description="List of chains")
    protocol_type: str = Field(description="Type of protocol", alias="protocolType")
    methodology_url: str = Field(
        description="URL to the methodology document", alias="methodologyURL"
    )
    methodology: Union[str, Dict[str, str]] = Field(description="Methodology details")
    latest_fetch_is_ok: bool = Field(
        description="Indicates if the latest fetch was successful",
        alias="latestFetchIsOk",
    )
    slug: str = Field(description="Slug identifier")
    id: int = Field(description="Unique identifier")


class DeFiLlamaRevenueOverviewData(Data):
    """DeFiLlama Revenue Overview Data."""

    total_data_chart: List[Dict[datetime, int]] = Field(
        description="Aggregated chart data.", alias="totalDataChart"
    )
    total_data_chart_breakdown: List[DeFiLlamaChainsBreakdownData] = Field(
        description="Aggregated chart data breakdown by chains.",
        alias="totalDataChartBreakdown",
    )
    breakdown_24h: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Total revenue collected in the last 24 hours broken down by chains",
        alias="breakdown24h",
    )
    total_24h: int = Field(description="Total 24h revenue.", alias="total24h")
    total_48h_to_24h: int = Field(
        description="Total 48h to 24h revenue.", alias="total48hto24h"
    )
    total_7d: int = Field(description="Total 7d revenue.", alias="total7d")
    total_14d_to_7d: int = Field(
        description="Total 14d to 7d revenue.", alias="total14dto7d"
    )
    total_60d_to_30d: int = Field(
        description="Total 60d to 30d revenue.", alias="total60dto30d"
    )
    total_30d: int = Field(description="Total 30d revenue.", alias="total30d")
    total_1y: int = Field(description="Total 1y revenue.", alias="total1y")
    change_1d: float = Field(description="1d change in revenue.")
    change_7d: float = Field(description="7d change in revenue.")
    change_1m: float = Field(description="1m change in revenue.")
    change_7d_over_7d: float = Field(
        description="7d change in revenue over 7d.", alias="change_7dover7d"
    )
    change_30d_over_30d: float = Field(
        description="30d change in revenue over 30d.", alias="change_30dover30d"
    )
    protocols: Optional[List[DeFiLlamaProtocolsData]] = Field(
        default=None, description="Protocols data.", alias="protocols"
    )

    @field_validator("total_data_chart_breakdown", mode="before")
    def validate_total_data_chart_breakdown(cls, v):
        return [DeFiLlamaChainsBreakdownData.model_validate(item) for item in v]

    @field_validator("protocols", mode="before")
    def validate_protocols(cls, v):
        return (
            [DeFiLlamaProtocolsData.model_validate(item) for item in v] if v else None
        )


class DeFiLlamaRevenueOverviewFetcher(
    Fetcher[DeFiLlamaRevenueOverviewQueryParams, DeFiLlamaRevenueOverviewData]
):
    """DeFiLlama Revenue Overview Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaRevenueOverviewQueryParams:
        """Transform query parameters."""
        return DeFiLlamaRevenueOverviewQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaRevenueOverviewQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API."""
        data = fees_revenue.get_overview(
            chain=query.chain,
            exclude_total_data_chart=False,
            exclude_total_data_chart_breakdown=False,
            type="revenue",
        )

        if not query.all:
            del data["protocols"]
            return data

        return data

    @staticmethod
    def transform_data(
        query: DeFiLlamaRevenueOverviewQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> DeFiLlamaRevenueOverviewData:
        """Transform the data into the desired format."""
        transformed_data: Dict[str, Any] = {}

        for k, v in data.items():
            if k in ("chain", "allChains"):
                continue
            elif k == "totalDataChart":
                transformed_data[k] = [
                    {datetime.fromtimestamp(item[0]): item[1]} for item in v
                ]
            elif k == "totalDataChartBreakdown":
                transformed_data[k] = [
                    {"date": item[0], "chains": item[1]} for item in v
                ]
            else:
                transformed_data[k] = v

        return DeFiLlamaRevenueOverviewData.model_validate(transformed_data)
