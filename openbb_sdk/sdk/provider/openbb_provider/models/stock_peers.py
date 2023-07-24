"""Stock Peers data model."""

from typing import List, Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class StockPeersQueryParams(QueryParams, BaseSymbol):
    """Stock Peers query model.

    Parameter
    ---------
    symbol: str
        The symbol of the company.
    """


class StockPeersData(Data):
    """Stock Peers data.

    Returns
    -------
    symbol : str
        The symbol of the company to retrieve the stock peers of.
    peers_list : List[str]
        A list of stock peers based on sector, exchange and market cap
    """

    symbol: str
    peers_list: Optional[List[str]]
