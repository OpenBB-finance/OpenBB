"""CBOE Options Chains fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import get_chains


class CboeOptionsChainsQueryParams(OptionsChainsQueryParams):
    """CBOE Options Chains query.

    Source: https://www.cboe.com/
    """


class CboeOptionsChainsData(OptionsChainsData):
    """CBOE Options Chains Data."""

    contractSymbol: str = Field(
        description="Contract symbol for the option.",
    )
    dte: int = Field(
        description="Days to expiration for the option.",
    )
    bidSize: int = Field(
        description="Bid size for the option.",
    )
    askSize: int = Field(
        description="Ask size for the option.",
    )
    impliedVolatility: float = Field(
        description="Implied volatility of the option.",
    )
    delta: float = Field(
        description="Delta of the option.",
    )
    gamma: float = Field(
        description="Gamma of the option.",
    )
    theta: float = Field(
        description="Theta of the option.",
    )
    rho: float = Field(
        description="Rho of the option.",
    )
    vega: float = Field(
        description="Vega of the option.",
    )
    theoretical: float = Field(
        description="Theoretical value of the option.",
    )
    open: float = Field(
        description="Opening price of the option.",
    )
    high: float = Field(
        description="High price of the option.",
    )
    low: float = Field(
        description="Low price of the option.",
    )
    lastTradePrice: float = Field(
        description="Last trade price of the option.",
    )
    tick: str = Field(
        description="Whether the last tick was up or down in price.",
    )
    previousClose: float = Field(
        description="Previous closing price of the option.",
    )
    change: float = Field(
        description="Change in  price of the option.",
    )
    changePercent: float = Field(
        description="Change, in percent, of the option.",
    )
    lastTradeTimestamp: datetime = Field(
        description="Last trade timestamp of the option.",
    )

    @validator("expiration", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""
        return datetime.strptime(v, "%Y-%m-%d")


class CboeOptionsChainsFetcher(
    Fetcher[
        CboeOptionsChainsQueryParams,
        List[CboeOptionsChainsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeOptionsChainsQueryParams:
        """Transform the query"""
        return CboeOptionsChainsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the CBOE endpoint"""
        return get_chains(query.symbol).to_dict("records")

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[CboeOptionsChainsData]:
        """Transform the data to the standard format"""
        return [CboeOptionsChainsData.parse_obj(d) for d in data]
