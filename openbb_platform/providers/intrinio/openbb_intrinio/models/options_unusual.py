"""Intrinio Unusual Options Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_unusual import (
    OptionsUnusualData,
    OptionsUnusualQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator


class IntrinioOptionsUnusualQueryParams(OptionsUnusualQueryParams):
    """Intrinio Unusual Options Query.

    source: https://docs.intrinio.com/documentation/web_api/get_unusual_activity_v2
    """

    source: Literal["delayed", "realtime"] = Field(
        default="delayed",
        description="The source of the data. Either realtime or delayed.",
    )


class IntrinioOptionsUnusualData(OptionsUnusualData):
    """Intrinio Unusual Options Data."""

    __alias_dict__ = {
        "contract_symbol": "contract",
        "underlying_symbol": "symbol",
    }

    @field_validator("contract_symbol", mode="before", check_fields=False)
    @classmethod
    def validate_contract_symbol(cls, v: str):  # pylint: disable=E0213
        """Return the symbol as the OCC standard format."""
        return v.replace("_", "") if v else None

    trade_type: str = Field(description="The type of unusual trade.", alias="type")
    sentiment: str = Field(
        description=(
            "Bullish, Bearish, or Neutral Sentiment is estimated based on whether"
            + " the trade was executed at the bid, ask, or mark price."
        )
    )
    total_value: Union[int, float] = Field(
        description="The aggregated value of all option contract premiums included in the trade."
    )
    total_size: int = Field(
        description="The total number of contracts involved in a single transaction."
    )
    average_price: float = Field(
        description="The average premium paid per option contract."
    )
    ask_at_execution: float = Field(description="Ask price at execution.")
    bid_at_execution: float = Field(description="Bid price at execution.")
    underlying_price_at_execution: float = Field(
        description="Price of the underlying security at execution of trade."
    )
    timestamp: datetime = Field(description="The UTC timestamp of order placement.")


class IntrinioOptionsUnusualFetcher(
    Fetcher[IntrinioOptionsUnusualQueryParams, List[IntrinioOptionsUnusualData]]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsUnusualQueryParams:
        """Transform the query."""
        return IntrinioOptionsUnusualQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioOptionsUnusualQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        data: List = []

        base_url = "https://api-v2.intrinio.com/options/unusual_activity"
        url = (
            base_url + f"/{query.symbol}?source={query.source}&api_key={api_key}"
            if query.symbol
            else base_url + f"?source={query.source}&api_key={api_key}"
        )
        response = await get_data_one(url, **kwargs)

        if "trades" in response:
            data = sorted(
                response["trades"], key=lambda x: x["timestamp"], reverse=True
            )

        return data

    @staticmethod
    def transform_data(
        query: IntrinioOptionsUnusualQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioOptionsUnusualData]:
        """Return the transformed data."""
        return [IntrinioOptionsUnusualData.model_validate(d) for d in data]
