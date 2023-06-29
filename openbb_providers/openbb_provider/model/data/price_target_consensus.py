"""Price target consensus data model."""

# IMPORT STANDARD
# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class PriceTargetConsensusQueryParams(QueryParams, BaseSymbol):
    """Price Target Consensus query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "PriceTargetConsensusQueryParams"


class PriceTargetConsensusData(Data):
    """Price target consensus data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    target_high : float
        The high target of the price target consensus.
    target_low : float
        The low target of the price target consensus.
    target_consensus : float
        The consensus target of the price target consensus.
    target_median : float
        The median target of the price target consensus.
    """

    symbol: str
    target_high: float
    target_low: float
    target_consensus: float
    target_median: float
