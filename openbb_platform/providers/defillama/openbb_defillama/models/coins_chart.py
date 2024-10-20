"""DeFiLlama Coins Chart Model."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_defillama.utils.helpers import get_data
from pydantic import Field, field_validator, model_validator


class DeFiLlamaCoinsChartQuery(QueryParams):
    """DeFiLlama Coins Chart Query."""

    token: str = Field(description="The token to get the chart for.")
    start_date: Optional[Union[int, str, datetime]] = Field(
        default=None,
        description="The start date to get the chart for. If a string is provided, it should follow the 'day-first' format.",  # noqa: E501
    )
    end_date: Optional[Union[int, str, datetime]] = Field(
        default=None,
        description="The end date to get the chart for. If a string is provided, it should follow the 'day-first' format.",  # noqa: E501
    )
    span: int = Field(default=0, description="The number of data points to return.")
    period: str = Field(
        default="24h",
        description="Duration between data points. Acceptable format: <int>W, <int>D, <int>H, or <int>M (case insensitive).",  # noqa: E501
    )
    search_width: str = Field(
        default="2h",
        description="Time range to get the current price for. Acceptable format: <int>W, <int>D, <int>H, or <int>M (case insensitive).",  # noqa: E501
    )

    @field_validator("start_date", "end_date", mode="before")
    def validate_timestamp(cls, v):
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            return int(v)
        elif isinstance(v, str):
            try:
                return int(datetime.fromisoformat(v).timestamp())
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {v}") from e
        elif isinstance(v, datetime):
            return int(v.timestamp())
        else:
            raise ValueError(f"Invalid timestamp type: {type(v)}")

    @field_validator("period", "search_width", mode="before")
    def validate_search_width(cls, v):
        pattern = re.compile(r"^(\d+)[WwDdHhMm]$")
        if not pattern.match(v):
            raise ValueError(
                "search_width must be in the format <int>W, <int>D, <int>H, or <int>M (case insensitive)"
            )
        return v.lower()

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date is not None and self.end_date is not None:
            raise ValueError("Only one of start_date or end_date should be provided")
        if self.start_date is None and self.end_date is None:
            raise ValueError("Either start_date or end_date must be provided")
        return self


class DeFiLlamaCoinsPricesData(Data):
    """DeFiLlama Coins Prices Data."""

    timestamp: datetime = Field(description="The timestamp of the data.")
    price: float = Field(description="The price of the token.")

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaCoinsChartData(Data):
    """DeFiLlama Coins Chart Data."""

    chain: str = Field(description="The chain the token is on.")
    address: str = Field(description="The address of the token.")
    symbol: str = Field(description="The symbol of the token.")
    confidence: float = Field(description="The confidence of the data.")
    decimals: Optional[int] = Field(
        default=None,
        description="Smallest unit of the token that can be traded or transferred",
    )
    prices: List[DeFiLlamaCoinsPricesData] = Field(
        description="The prices of the token."
    )

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()

    @field_validator("prices", mode="before")
    def validate_prices(cls, v):
        return [DeFiLlamaCoinsPricesData.model_validate(price) for price in v]


class DeFiLlamaCoinsChartFetcher(
    Fetcher[DeFiLlamaCoinsChartQuery, List[DeFiLlamaCoinsChartData]]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaCoinsChartQuery:
        transformed_params = params

        if params.get("end_date") is None:
            transformed_params["start_date"] = datetime.now().timestamp()

        if params.get("start_date") is None:
            transformed_params["end_date"] = datetime.now().timestamp()

        return DeFiLlamaCoinsChartQuery(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsChartQuery,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama."""
        date_params = (
            f"start={query.start_date}" if query.start_date else f"end={query.end_date}"
        )
        url = (
            f"https://coins.llama.fi/chart/{query.token}?"
            f"{date_params}&span={query.span}&period={query.period}&searchWidth={query.search_width}"
        )
        data = await get_data(url)
        return data.get("coins", {})

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsChartQuery, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaCoinsChartData]:
        """Transform the data into the desired format."""
        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                "chain": k.split(":")[0],
                "address": k.split(":")[1],
                "symbol": v["symbol"],
                "confidence": v["confidence"],
                "decimals": v.get("decimals", None),
                "prices": v["prices"],
            }
            for k, v in data.items()
        ]

        return [DeFiLlamaCoinsChartData.model_validate(d) for d in transformed_data]
