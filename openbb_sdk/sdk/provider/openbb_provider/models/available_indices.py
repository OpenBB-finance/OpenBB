"""Available Indices data model."""


from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams


class AvailableIndicesQueryParams(QueryParams):
    """Available Indices query."""


class AvailableIndicesData(Data):
    """Available Indices data.

    Returns the major indices from Dow Jones, Nasdaq and, S&P 500.

    Returns
    -------
    symbol : str
        The symbol of the index.
    name : Optional[str]
        The name of the index.
    currency : Optional[str]
        The currency the index is traded in.
    stock_exchange : str
        The stock exchange where the index is listed.
    exchange_short_name : str
        The short name of the stock exchange where the index is listed.
    """

    symbol: str
    name: Optional[str]
    currency: Optional[str]
    stock_exchange: str
    exchange_short_name: str
