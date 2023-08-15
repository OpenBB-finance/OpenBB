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

    expiration: datetime = Field(description="The expiration date of the contract.")
    strike: float = Field(description="The strike price of the contract.")
    optionType: str = Field(description="Call or Put.")
    bid: float = Field(description="The bid price of the contract.")
    ask: float = Field(description="The ask price of the contract.")
    openInterest: float = Field(description="The open interest on the contract.")
    volume: float = Field(description="The current trading volume on the contract.")
