"""DeFiLlama TVL Historical model"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from defillama import tvl
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class DeFiLlamaTvlHistoricalQueryParams(QueryParams):
    """DeFiLlama TVL Historical Query.

    Source: https://defillama.com/docs/api
    """

    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Should be a protocol or chain.",
    )
    symbol_type: Optional[Literal["protocol", "chain"]] = Field(
        default="protocol",
        description="Type of symbol to get data for.",
    )


class DeFiLlamaProtocolTokens(Data):
    """DeFiLlama Protocol Tokens Data."""

    date: datetime = Field(description="Date of the token")
    tokens: Dict[str, float] = Field(description="Total Value Locked for each token")

    @field_validator("date", mode="before")
    def convert_timestamp_to_datetime(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaTvlData(Data):
    """DeFiLlama TVL Data"""

    date: datetime = Field(description="Date of the TVL")
    total_liquidity_usd: float = Field(
        description="Total Value Locked in USD", alias="totalLiquidityUSD"
    )

    @field_validator("date", mode="before")
    def convert_timestamp_to_datetime(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaChainTvlsData(Data):
    """DeFiLlama Chain TVLs Data."""

    tvl: List[DeFiLlamaTvlData] = Field(description="Date of the chain")
    tokens: Optional[List[DeFiLlamaProtocolTokens]] = Field(
        default=None, description="Total Value Locked for each token"
    )
    tokens_in_usd: Optional[List[DeFiLlamaProtocolTokens]] = Field(
        default=None,
        description="Total Value Locked in USD for each token",
        alias="tokensInUsd",
    )

    @field_validator("tokens", "tokens_in_usd", mode="before")
    def validate_fields(cls, v):
        return [DeFiLlamaProtocolTokens.model_validate(d) for d in v] if v else None

    @field_validator("tvl", mode="before")
    def validate_tvl(cls, v):
        if isinstance(v, list):
            return [DeFiLlamaTvlData.model_validate(d) for d in v]
        else:
            return v


class DeFiLlamaProtocolRaisesData(Data):
    """DeFiLlama Protocol Raises Data."""

    date: datetime = Field(description="Date of the raise")
    name: str = Field(description="Name of the protocol")
    round: str = Field(description="Round of the raise")
    amount: float = Field(description="Amount of the raise in USD")
    chains: List[str] = Field(description="List of chains the protocol is deployed on")
    sector: str = Field(description="Sector of the protocol")
    category: str = Field(description="Category of the protocol")
    source: str = Field(description="Source of the raise")
    lead_investors: List[str] = Field(
        description="List of lead investors", alias="leadInvestors"
    )
    other_investors: List[str] = Field(
        description="List of other investors", alias="otherInvestors"
    )
    valuation: Optional[float] = Field(
        default=None, description="Valuation of the protocol"
    )
    defillama_id: str = Field(
        description="DeFiLlama ID of the protocol", alias="defillamaId"
    )

    @field_validator("date", mode="before")
    def convert_timestamp_to_datetime(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaProtocolHallmarksData(Data):
    """DeFiLlama Protocol Hallmarks Data"""

    date: datetime = Field(description="Date of the hallmark")
    label: str = Field(description="Label of the hallmark")

    @field_validator("date", mode="before")
    def convert_timestamp_to_datetime(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaTvlHistoricalData(Data):
    """DeFiLlama TVL Historical Data."""

    # Field(s) returned for both protocols and chains
    tvl: Optional[Union[float, List[DeFiLlamaTvlData]]] = Field(
        default=None, description="Total Value Locked in USD"
    )

    # Field(s) returned when symbol_type is "chain"
    date: Optional[datetime] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )

    # Field(s) returned when symbol_type is "protocol"
    id: Optional[str] = Field(default=None, description="ID of the protocol")
    name: Optional[str] = Field(default=None, description="Name of the protocol")
    address: Optional[str] = Field(default=None, description="Address of the protocol")
    symbol: Optional[str] = Field(default=None, description="Symbol of the protocol")
    url: Optional[str] = Field(default=None, description="Website URL of the protocol")
    description: Optional[str] = Field(
        default=None, description="Description of the protocol"
    )
    chain: Optional[str] = Field(default=None, description="Name of the blockchain")
    logo: Optional[str] = Field(default=None, description="URL of the protocol's logo")
    audits: Optional[str] = Field(
        default=None, description="Number of audits the protocol has undergone"
    )
    audit_note: Optional[str] = Field(
        default=None, description="Note about the audit status"
    )
    gecko_id: Optional[str] = Field(
        default=None, description="CoinGecko ID of the token"
    )
    cmc_id: Optional[str] = Field(
        default=None, description="CoinMarketCap ID of the token", alias="cmcId"
    )
    category: Optional[str] = Field(
        default=None, description="Category of the protocol"
    )
    chains: Optional[List[str]] = Field(
        default=None, description="List of chains the protocol is deployed on"
    )
    module: Optional[str] = Field(
        default=None, description="Module used for TVL calculation"
    )
    twitter: Optional[str] = Field(
        default=None, description="Twitter handle of the protocol"
    )
    forked_from: Optional[List[str]] = Field(
        default=None,
        description="List of protocols that the current protocol has forked from",
        alias="forkedFrom",
    )
    oracles: Optional[List[str]] = Field(
        default=None, description="List of oracles used for TVL calculation"
    )
    listed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of when the protocol was listed",
        alias="listedAt",
    )
    methodology: Optional[str] = Field(
        default=None, description="Methodology used for TVL calculation"
    )
    slug: Optional[str] = Field(default=None, description="Slug of the protocol")
    chain_tvls: Optional[Union[Dict[str, float], Dict[str, DeFiLlamaChainTvlsData]]] = (
        Field(
            default=None,
            description="Total Value Locked in USD for each chain of the protocol",
            alias="chainTvls",
        )
    )
    change_1h: Optional[float] = Field(
        default=None, description="Change in TVL over the last hour"
    )
    change_1d: Optional[float] = Field(
        default=None, description="Change in TVL over the last day"
    )
    change_7d: Optional[float] = Field(
        default=None, description="Change in TVL over the last week"
    )

    # Additional fields returned when a protocol is provided
    token_breakdowns: Optional[Dict[str, float]] = Field(
        default=None, description="Breakdown of TVL by token", alias="tokenBreakdowns"
    )
    mcap: Optional[float] = Field(
        default=None, description="Market capitalization in USD"
    )
    treasury: Optional[str] = Field(
        default=None, description="Treasury address of the protocol"
    )
    governance_id: Optional[List[str]] = Field(
        default=None, description="List of governance IDs", alias="governanceID"
    )
    github: Optional[List[str]] = Field(
        default=None, description="List of GitHub repositories"
    )
    wrong_liquidity: Optional[bool] = Field(
        default=None,
        description="Whether the protocol has wrong liquidity",
        alias="wrongLiquidity",
    )
    current_chain_tvls: Optional[Dict[str, float]] = Field(
        default=None,
        description="Total Value Locked in USD for each chain",
        alias="currentChainTvls",
    )
    tokens: Optional[List[DeFiLlamaProtocolTokens]] = Field(
        default=None, description="Total Value Locked in USD for each token"
    )
    tokens_in_usd: Optional[List[DeFiLlamaProtocolTokens]] = Field(
        default=None,
        description="Total Value Locked in USD for each token",
        alias="tokensInUsd",
    )
    is_parent_protocol: Optional[bool] = Field(
        default=None,
        description="Whether the protocol is a parent protocol",
        alias="isParentProtocol",
    )
    raises: Optional[List[DeFiLlamaProtocolRaisesData]] = Field(
        default=None, description="List of raises the protocol has undergone"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Metrics of the protocol"
    )
    other_protocols: Optional[List[str]] = Field(
        default=None, description="List of other protocols", alias="otherProtocols"
    )
    hallmarks: Optional[List[DeFiLlamaProtocolHallmarksData]] = Field(
        default=None, description="List of hallmarks"
    )

    @field_validator("listed_at", mode="before")
    def convert_timestamp_to_datetime(cls, v):
        return datetime.fromtimestamp(v) if v else None

    @field_validator("tokens", "tokens_in_usd", mode="before")
    def validate_tokens(cls, v):
        return [DeFiLlamaProtocolTokens.model_validate(d) for d in v] if v else None

    @field_validator("tvl", mode="before")
    def validate_tvl(cls, v):
        if isinstance(v, list):
            return [DeFiLlamaTvlData.model_validate(d) for d in v]
        else:
            return v

    @field_validator("chain_tvls", mode="before")
    def validate_chain_tvls(cls, v):
        return (
            {
                k: (
                    DeFiLlamaChainTvlsData.model_validate(v)
                    if isinstance(v, dict)
                    else v
                )
                for k, v in v.items()
            }
            if v
            else None
        )

    @field_validator("raises", mode="before")
    def validate_raises(cls, v):
        return [DeFiLlamaProtocolRaisesData.model_validate(d) for d in v] if v else None

    @field_validator("hallmarks", mode="before")
    def validate_hallmarks(cls, v):
        if isinstance(v, list):
            return [DeFiLlamaProtocolHallmarksData.model_validate(d) for d in v]
        else:
            return v


class DeFiLlamaTvlHistoricalFetcher(
    Fetcher[DeFiLlamaTvlHistoricalQueryParams, List[DeFiLlamaTvlHistoricalData]]
):
    """DeFiLlama TVL Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaTvlHistoricalQueryParams:
        """Transform query parameters."""
        return DeFiLlamaTvlHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaTvlHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Extract data from DeFiLlama API."""
        if query.symbol_type == "protocol":
            if query.symbol is None:
                return tvl.get_protocols()
            else:
                return [tvl.get_protocols(query.symbol)]
        elif query.symbol_type == "chain":
            if query.symbol is None:
                return tvl.get_historical_chains_tvl()
            else:
                return tvl.get_historical_chains_tvl(query.symbol)

        return []

    @staticmethod
    def transform_data(
        query: DeFiLlamaTvlHistoricalQueryParams,
        data: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> List[DeFiLlamaTvlHistoricalData]:
        """Transform the data into the desired format."""
        data = [
            {
                **d,
                "hallmarks": (
                    [{"date": item[0], "label": item[1]} for item in d["hallmarks"]]
                    if "hallmarks" in d
                    else None
                ),
            }
            for d in data
        ]

        return [DeFiLlamaTvlHistoricalData.model_validate(d) for d in data]
