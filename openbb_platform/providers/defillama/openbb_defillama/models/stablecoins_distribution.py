"""DeFiLlama Stablecoins Distribution Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import stablecoins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaStablecoinsDistributionQueryParams(QueryParams):
    """DeFiLlama Stablecoins Distribution Query.

    Source: https://defillama.com/docs/api
    """

    stablecoin: str = Field(description="Stablecoin ID to get the distribution of.")


class DeFiLlamaStablecoinsChainTokensData(Data):
    """DeFiLlama Stablecoins Distribution Chain Tokens."""

    date: datetime = Field(description="Date of the data.")
    circulating: Optional[Dict[str, float]] = Field(
        default=None,
        description="Circulating of the stablecoin on each chain.",
    )
    bridged_to: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Currency bridges value of the stablecoin on each chain.",
        alias="bridgedTo",
    )
    minted: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Minted amount of the stablecoin on each chain.",
    )

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaStablecoinsTokensData(Data):
    """DeFiLlama Stablecoins Distribution Tokens Data."""

    date: datetime = Field(description="Date of the data.")
    circulating: Optional[Dict[str, float]] = Field(
        default=None,
        description="Circulating of the stablecoin on each chain.",
    )
    unreleased: Optional[Dict[str, float]] = Field(
        default=None,
        description="Unreleased of the stablecoin on each chain.",
    )

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaStablecoinsDistributionData(Data):
    """DeFiLlama Stablecoins Distribution Data."""

    id: str = Field(description="ID of the stablecoin.")
    name: str = Field(description="Name of the stablecoin.")
    address: str = Field(description="Address of the stablecoin.")
    symbol: str = Field(description="Symbol of the stablecoin.")
    url: str = Field(description="URL of the stablecoin.")
    description: str = Field(description="Description of the stablecoin.")
    mint_redeem_description: str = Field(
        description="Mint/Redeem description of the stablecoin.",
        alias="mintRedeemDescription",
    )
    on_coin_gecko: bool = Field(
        description="Whether the stablecoin is on CoinGecko.", alias="onCoinGecko"
    )
    gecko_id: str = Field(description="CoinGecko ID of the stablecoin.")
    cmc_id: str = Field(description="CMC ID of the stablecoin.", alias="cmcId")
    peg_type: str = Field(description="Peg type of the stablecoin.", alias="pegType")
    peg_mechanism: str = Field(
        description="Peg mechanism of the stablecoin.", alias="pegMechanism"
    )
    price_source: str = Field(
        description="Price source of the stablecoin.", alias="priceSource"
    )
    price: float = Field(description="Price of the stablecoin.")
    audit_links: List[str] = Field(description="Audit links of the stablecoin.")
    twitter: str = Field(description="Twitter of the stablecoin.")
    wiki: str = Field(description="Wiki of the stablecoin.")
    chain_balances: Dict[str, List[DeFiLlamaStablecoinsChainTokensData]] = Field(
        description="Chain balances of the stablecoin.", alias="chainBalances"
    )
    current_chain_balances: Dict[str, Dict[str, float]] = Field(
        description="Current chain balances of the stablecoin.",
        alias="currentChainBalances",
    )
    tokens: List[DeFiLlamaStablecoinsTokensData] = Field(
        description="Tokens of the stablecoin."
    )

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()

    @field_validator("chain_balances", mode="before")
    def validate_chain_balances(cls, v):
        return {
            c: [DeFiLlamaStablecoinsChainTokensData.model_validate(i) for i in d]
            for c, d in v.items()
        }

    @field_validator("tokens", mode="before")
    def validate_tokens(cls, v):
        return [DeFiLlamaStablecoinsTokensData.model_validate(d) for d in v]


class DeFiLlamaStablecoinsDistributionFetcher(
    Fetcher[
        DeFiLlamaStablecoinsDistributionQueryParams,
        DeFiLlamaStablecoinsDistributionData,
    ]
):
    """DeFiLlama Stablecoins Distribution Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> DeFiLlamaStablecoinsDistributionQueryParams:
        """Transform query parameters."""
        return DeFiLlamaStablecoinsDistributionQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaStablecoinsDistributionQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama."""
        return stablecoins.get_distribution(query.stablecoin)

    @staticmethod
    def transform_data(
        query: DeFiLlamaStablecoinsDistributionQueryParams,
        data: Dict[str, Any],
        **kwargs: Any
    ) -> DeFiLlamaStablecoinsDistributionData:
        """Transform the data into the desired format."""
        transformed_data: Dict[str, Any] = {}

        transformed_data = {
            **data,
            "chainBalances": {k: v["tokens"] for k, v in data["chainBalances"].items()},
        }

        return DeFiLlamaStablecoinsDistributionData.model_validate(transformed_data)
