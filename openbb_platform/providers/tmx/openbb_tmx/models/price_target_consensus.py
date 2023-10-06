"""TMX Stock Analysts Model"""

import json
from typing import Any, Dict, Optional

import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_all_tmx_companies, get_random_agent
from pydantic import Field


class TmxPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """TMX Price Target Consensus Query."""


class TmxPriceTargetConsensusData(PriceTargetConsensusData):
    """TMX Price Target Consensus Data."""

    __alias_dict__ = {
        "target_consensus": "price_target",
        "target_high": "price_target_high",
        "target_low": "price_target_low",
    }

    target_upside: Optional[float] = Field(
        default=None, description="Percent of upside."
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


class TmxPriceTargetConsensusFetcher(
    Fetcher[TmxPriceTargetConsensusQueryParams, TmxPriceTargetConsensusData]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxPriceTargetConsensusQueryParams:
        """Transform the query."""
        return TmxPriceTargetConsensusQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxPriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the TMX endpoint."""

        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSXV", "")
            .replace(".TSX", "")
        )
        if symbol not in list(get_all_tmx_companies().keys()):
            raise ValueError(f"{symbol} is not a valid TMX company.")

        payload = GQL.get_company_analysts_payload.copy()
        payload["variables"]["symbol"] = symbol
        payload["variables"]["datatype"] = "equity"

        data = {}
        url = "https://app-money.tmx.com/graphql"
        r = requests.post(
            url,
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
        try:
            if r.status_code == 403:
                raise RuntimeError(f"HTTP error - > {r.text}")
            else:
                r_data = r.json()["data"]["analysts"]
                if r_data is None:
                    raise RuntimeError(f"No results found for symbol -> {symbol}")
                data.update(
                    {
                        "symbol": symbol,
                        "total_analysts": r_data["totalAnalysts"],
                        "consensus": r_data["consensusAnalysts"]["consensus"],
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
                return data
        except Exception as e:
            raise (e)

    @staticmethod
    def transform_data(data: Dict) -> TmxPriceTargetConsensusData:
        """Return the transformed data."""
        return TmxPriceTargetConsensusData.model_validate(data)
