"""Price target consensus data model."""


from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class PriceTargetConsensusQueryParams(QueryParams, BaseSymbol):
    """Price Target Consensus Query."""


class PriceTargetConsensusData(Data, BaseSymbol):
    """Price target consensus Data."""

    target_high: float = Field(
        description="The high target of the price target consensus."
    )
    target_low: float = Field(
        description="The low target of the price target consensus."
    )
    target_consensus: float = Field(
        description="The consensus target of the price target consensus."
    )
    target_median: float = Field(
        description="The median target of the price target consensus."
    )
