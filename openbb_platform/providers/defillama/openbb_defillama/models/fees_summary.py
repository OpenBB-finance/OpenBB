"""DeFiLlama Fees Summary Model."""

from typing import Any, Dict, List, Optional, Literal, Union
from datetime import datetime
from pydantic import Field, field_validator
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from defillama import fees_revenue


class DeFiLlamaFeesSummaryQueryParams(QueryParams):
    """DeFiLlama Fees Summary Query."""

    protocol: str = Field(description="The protocol to fetch data for.")


class DeFiLlamaChainsBreakdownData(Data):
    """DeFiLlama Chains Breakdown."""

    date: datetime = Field(description="The date of the data.")
    chains: Dict[str, Dict[str, int]] = Field(description="The chains data.")

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaFeesSummaryData(Data):
    """DeFiLlama Fees Summary Data."""

    name: str = Field(description="The name of the protocol.")
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
    logo: str = Field(description="The logo of the protocol.")
    chains: List[str] = Field(description="The chains of the protocol.")
    methodology_url: Optional[str] = Field(
        default=None,
        description="The methodology URL of the protocol.",
        alias="methodologyURL",
    )
    methodology: Optional[Union[str, Dict[str, str]]] = Field(
        default=None, description="The methodology of the protocol."
    )
    gecko_id: str = Field(description="The gecko id of the protocol.")
    forked_from: Optional[str] = Field(
        default=None, description="The forked from of the protocol.", alias="forkedFrom"
    )
    twitter: Optional[str] = Field(
        default=None, description="The twitter of the protocol."
    )
    audits: Optional[str] = Field(
        default=None, description="The audits of the protocol."
    )
    description: Optional[str] = Field(
        default=None, description="The description of the protocol."
    )
    address: Optional[str] = Field(
        default=None, description="The address of the protocol."
    )
    url: Optional[str] = Field(default=None, description="The url of the protocol.")
    audit_links: Optional[List[str]] = Field(
        default=None, description="The audit links of the protocol."
    )
    version_key: Optional[str] = Field(
        default=None, description="The version key of the protocol.", alias="versionKey"
    )
    cmc_id: Optional[str] = Field(
        default=None, description="The cmc id of the protocol.", alias="cmcId"
    )
    id: str = Field(description="The id of the protocol.")
    github: Optional[List[str]] = Field(
        default=None, description="The github of the protocol."
    )
    governance_id: Optional[List[str]] = Field(
        default=None,
        description="The governance id of the protocol.",
        alias="governanceID",
    )
    treasury: Optional[str] = Field(
        default=None, description="The treasury of the protocol."
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
    change_1d: float = Field(description="The change 1d of the protocol.")

    @field_validator("total_data_chart_breakdown", mode="before")
    def validate_total_data_chart_breakdown(cls, v):
        return [DeFiLlamaChainsBreakdownData.model_validate(item) for item in v]


class DeFiLlamaFeesSummaryFetcher(
    Fetcher[DeFiLlamaFeesSummaryQueryParams, List[DeFiLlamaFeesSummaryData]]
):
    """Fetcher for DeFiLlama Fees Summary data"""

    @staticmethod
    def transform_query(params: DeFiLlamaFeesSummaryQueryParams) -> Dict[str, Any]:
        """Transform query parameters"""
        return DeFiLlamaFeesSummaryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaFeesSummaryQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API"""
        return fees_revenue.get_summary(
            protocol=query.protocol,
            data="daily",
            type="fees",
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaFeesSummaryQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaFeesSummaryData]:
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

        return DeFiLlamaFeesSummaryData.model_validate(transformed_data)
