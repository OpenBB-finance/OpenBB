"""DeFiLlama Volumes Summary Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from defillama import volumes
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaVolumesSummaryQueryParams(QueryParams):
    """DeFiLlama Volumes Summary Query."""

    protocol: str = Field(description="The protocol to fetch data for.")
    is_options: bool = Field(
        default=False, description="Whether to fetch options dex data."
    )
    volume_type: Optional[Literal["premium", "notional"]] = Field(
        default="premium", description="The type of volume to fetch."
    )
    # NOTE: Disabled since the API does not return any data
    # aggregate: Literal["daily", "total"] = Field(default="daily", description="Whether to fetch daily or total aggregate data.")


class DeFiLlamaChainsBreakdownData(Data):
    """DeFiLlama Chains Breakdown."""

    date: datetime = Field(description="The date of the data.")
    chains: Dict[str, Dict[str, int]] = Field(description="The chains data.")

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaVolumesSummaryData(Data):
    """DeFiLlama Volumes Summary Data."""

    id: str = Field(description="The id of the protocol.")
    name: str = Field(description="The name of the protocol.")
    url: Optional[str] = Field(default=None, description="The url of the protocol.")
    description: Optional[str] = Field(
        default=None, description="The description of the protocol."
    )
    logo: str = Field(description="The logo of the protocol.")
    gecko_id: Optional[str] = Field(
        default=None, description="The gecko id of the protocol."
    )
    cmc_id: Optional[str] = Field(
        default=None, description="The cmc id of the protocol.", alias="cmcId"
    )
    chains: List[str] = Field(description="The chains of the protocol.")
    twitter: Optional[str] = Field(
        default=None, description="The twitter of the protocol."
    )
    treasury: Optional[str] = Field(
        default=None, description="The treasury of the protocol."
    )
    governance_id: Optional[List[str]] = Field(
        default=None,
        description="The governance id of the protocol.",
        alias="governanceID",
    )
    github: Optional[List[str]] = Field(
        default=None, description="The github of the protocol."
    )
    child_protocols: Optional[List[str]] = Field(
        default=None,
        description="The child protocols of the protocol.",
        alias="childProtocols",
    )
    defillama_id: Optional[str] = Field(
        default=None,
        description="The defillama id of the protocol.",
        alias="defillamaId",
    )
    disabled: Optional[bool] = Field(
        default=None, description="Whether the protocol is disabled."
    )
    display_name: str = Field(
        description="The display name of the protocol.", alias="displayName"
    )
    module: Optional[str] = Field(
        default=None, description="The module of the protocol."
    )
    category: Optional[str] = Field(
        default=None, description="The category of the protocol."
    )
    methodology_url: Optional[str] = Field(
        default=None,
        description="The methodology URL of the protocol.",
        alias="methodologyURL",
    )
    methodology: Optional[Union[str, Dict[str, str]]] = Field(
        default=None, description="The methodology of the protocol."
    )
    oracles: Optional[List[str]] = Field(
        default=None, description="The oracles of the protocol."
    )
    forked_from: Optional[Union[str, List[str]]] = Field(
        default=None, description="The forked from of the protocol.", alias="forkedFrom"
    )
    audits: Optional[str] = Field(
        default=None, description="The audits of the protocol."
    )
    audit_note: Optional[str] = Field(
        default=None, description="The audit note of the protocol.", alias="auditNote"
    )
    address: Optional[str] = Field(
        default=None, description="The address of the protocol."
    )
    audit_links: Optional[List[str]] = Field(
        default=None, description="The audit links of the protocol."
    )
    version_key: Optional[str] = Field(
        default=None, description="The version key of the protocol.", alias="versionKey"
    )
    parent_protocol: Optional[str] = Field(
        default=None,
        description="The parent protocol of the protocol.",
        alias="parentProtocol",
    )
    latest_fetch_is_ok: bool = Field(
        default=None,
        description="Whether the latest fetch is ok.",
        alias="latestFetchIsOk",
    )
    slug: str = Field(description="The slug of the protocol.")
    protocol_type: str = Field(
        description="The protocol type of the protocol.", alias="protocolType"
    )
    total_24h: int = Field(
        description="The total 24h of the protocol.", alias="total24h"
    )
    total_48h_to_24h: int = Field(
        description="The total 48h to 24h of the protocol.", alias="total48hto24h"
    )
    total_7d: int = Field(description="The total 7d of the protocol.", alias="total7d")
    total_all_time: int = Field(
        description="The total all time of the protocol.", alias="totalAllTime"
    )
    total_data_chart: List[Dict[datetime, int]] = Field(
        description="Aggregated chart data.", alias="totalDataChart"
    )
    total_data_chart_breakdown: List[DeFiLlamaChainsBreakdownData] = Field(
        description="Aggregated chart data breakdown by chains.",
        alias="totalDataChartBreakdown",
    )
    change_1d: Optional[float] = Field(
        default=None, description="The change 1d of the protocol."
    )

    @field_validator("total_data_chart_breakdown", mode="before")
    def validate_total_data_chart_breakdown(cls, v):
        return [DeFiLlamaChainsBreakdownData.model_validate(item) for item in v]


class DeFiLlamaVolumesSummaryFetcher(
    Fetcher[DeFiLlamaVolumesSummaryQueryParams, List[DeFiLlamaVolumesSummaryData]]
):
    """Fetcher for DeFiLlama Volumes Summary data"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaVolumesSummaryQueryParams:
        """Transform query parameters"""
        return DeFiLlamaVolumesSummaryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaVolumesSummaryQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API"""

        if query.is_options:
            return volumes.get_options_summary(
                protocol=query.protocol,
                type=query.volume_type,
            )
        else:
            return volumes.get_dex_summary(
                protocol=query.protocol,
                exclude_total_data_chart=False,
                exclude_total_data_chart_breakdown=False,
            )

    @staticmethod
    def transform_data(
        query: DeFiLlamaVolumesSummaryQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaVolumesSummaryData]:
        """Transform the data into the desired format"""
        transformed_data: Dict[str, Any] = dict(data)

        transformed_data["totalDataChart"] = [
            {datetime.fromtimestamp(item[0]): item[1]}
            for item in data["totalDataChart"]
        ]
        transformed_data["totalDataChartBreakdown"] = [
            {"date": item[0], "chains": item[1]}
            for item in data["totalDataChartBreakdown"]
        ]

        return DeFiLlamaVolumesSummaryData.model_validate(transformed_data)
