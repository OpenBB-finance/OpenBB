"""TMX Stock Analysts Model"""

# pylint: disable=unused-argument
import asyncio
import json
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field, field_validator


class TmxPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """TMX Price Target Consensus Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_symbol(cls, value):
        """Check the symbol."""
        if not value:
            raise RuntimeError("Error: Symbol is a required field for TMX.")
        return value


class TmxPriceTargetConsensusData(PriceTargetConsensusData):
    """TMX Price Target Consensus Data."""

    __alias_dict__ = {
        "target_consensus": "price_target",
        "target_high": "price_target_high",
        "target_low": "price_target_low",
        "target_upside": "price_target_upside",
    }

    target_upside: Optional[float] = Field(
        default=None,
        description="Percent of upside, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    total_analysts: Optional[int] = Field(
        default=None, description="Total number of analyst."
    )
    buy_ratings: Optional[int] = Field(
        default=None, description="Number of buy ratings."
    )
    sell_ratings: Optional[int] = Field(
        default=None, description="Number of sell ratings."
    )
    hold_ratings: Optional[int] = Field(
        default=None, description="Number of hold ratings."
    )
    consensus_action: Optional[str] = Field(
        default=None, description="Consensus action."
    )

    @field_validator("target_upside", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None

    @field_validator(
        "target_consensus",
        "target_high",
        "target_low",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def round_targets(cls, v):
        """Return rounded prices to two decimals."""
        return round(float(v), 2) if v else None


class TmxPriceTargetConsensusFetcher(
    Fetcher[TmxPriceTargetConsensusQueryParams, List[TmxPriceTargetConsensusData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxPriceTargetConsensusQueryParams:
        """Transform the query."""
        return TmxPriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxPriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        symbols = query.symbol.split(",")  # type: ignore
        results: List[Dict] = []

        async def create_task(symbol, results):
            """Create a task for each symbol provided."""
            symbol = (
                symbol.upper()
                .replace("-", ".")
                .replace(".TO", "")
                .replace(".TSXV", "")
                .replace(".TSX", "")
            )

            payload = gql.get_company_analysts_payload.copy()
            payload["variables"]["symbol"] = symbol
            payload["variables"]["datatype"] = "equity"

            data = {}
            url = "https://app-money.tmx.com/graphql"
            response = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": get_random_agent(),
                    "Accept": "*/*",
                },
                timeout=10,
            )
            r_data = (
                response["data"].get("analysts", None) if response.get("data") else None
            )
            if r_data:
                data.update(
                    {
                        "symbol": symbol,
                        "total_analysts": r_data["totalAnalysts"],
                        "consensus_action": r_data["consensusAnalysts"]["consensus"],
                        "buy_ratings": r_data["consensusAnalysts"]["buy"],
                        "sell_ratings": r_data["consensusAnalysts"]["sell"],
                        "hold_ratings": r_data["consensusAnalysts"]["hold"],
                        "price_target": r_data["priceTarget"]["priceTarget"],
                        "price_target_high": r_data["priceTarget"]["highPriceTarget"],
                        "price_target_low": r_data["priceTarget"]["lowPriceTarget"],
                        "price_target_upside": r_data["priceTarget"][
                            "priceTargetUpside"
                        ],
                    }
                )
                results.append(data)
            return results

        tasks = [create_task(symbol, results) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: TmxPriceTargetConsensusQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxPriceTargetConsensusData]:
        """Return the transformed data."""
        return [TmxPriceTargetConsensusData.model_validate(d) for d in data]
