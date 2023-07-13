"""Forex available pairs data model."""


from typing import Optional

from openbb_provider.model.abstract.data import Data, QueryParams


class ForexPairsQueryParams(QueryParams):
    """Forex available pairs query."""


class ForexPairsData(Data):
    """Forex available pairs data.

    Returns
    -------
    symbol : str
        The symbol of the currency pair.
    name : str
        The name of the currency pair separated by '/'.
    currency : str
        The base currency of the currency pair.
    stock_exchange : Optional[str]
        The stock exchange of the currency pair.
    exchange_short_name : Optional[str]
        The short name of the stock exchange of the currency pair.
    """

    symbol: str
    name: str
    currency: str
    stock_exchange: Optional[str]
    exchange_short_name: Optional[str]
