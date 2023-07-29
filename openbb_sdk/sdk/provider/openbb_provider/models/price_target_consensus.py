"""Price target consensus data model."""


from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class PriceTargetConsensusQueryParams(QueryParams, BaseSymbol):
    """Price Target Consensus query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


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
