"""Price target consensus data model."""


from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class PriceTargetConsensusQueryParams(QueryParams, BaseSymbol):
    """Price Target Consensus Query."""


class PriceTargetConsensusData(Data, BaseSymbol):
    """Price target consensus Data."""

    target_high: Optional[float] = Field(
        default=None, description="High target of the price target consensus."
    )
    target_low: Optional[float] = Field(
        default=None, description="Low target of the price target consensus."
    )
    target_consensus: Optional[float] = Field(
        default=None, description="Consensus target of the price target consensus."
    )
    target_median: Optional[float] = Field(
        default=None, description="Median target of the price target consensus."
    )
