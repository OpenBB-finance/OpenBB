"""Options Chains data model."""

from datetime import datetime

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class OptionsChainsQueryParams(QueryParams, BaseSymbol):
    """Options Chains Query Params"""


class OptionsChainsData(Data):
    """Options Chains Data."""

    expiration: datetime = Field(description="Expiration date of the contract.")
    strike: float = Field(description="Strike price of the contract.")
    optionType: str = Field(description="Call or Put.")
    bid: float = Field(description="Bid price of the contract.")
    ask: float = Field(description="Ask price of the contract.")
    openInterest: float = Field(description="Open interest on the contract.")
    volume: float = Field(description="Current trading volume on the contract.")
