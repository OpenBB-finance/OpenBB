"""SDK Helper Functions."""
__docfromat__ = "numpy"

import pandas as pd

from openbb_terminal.cryptocurrency.discovery import (
    coinmarketcap_model,
    pycoingecko_model,
)


def top_coins(source: str = "CoinGecko", limit: int = 10) -> pd.DataFrame:
    """Get top cryptp coins.

    Parameters
    ----------
    source : str, optional
        Source of data, by default "CoinGecko"
    limit : int, optional
        Number of coins to return, by default 10

    Returns
    -------
    pd.DataFrame
        DataFrame with top coins

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> top_coins = openbb.crypto.disc.top_coins()

    To get 30 results from coinmarketcap, use the source parameter and the limit parameter:
    >>> top_coins = openbb.crypto.disc.top_coins(source="CoinMarketCap", limit=30)

    """
    if source.lower() == "coingecko":
        df = pycoingecko_model.get_coins(limit=limit)
        return df
    if source.lower() == "coinmarketcap":
        df = coinmarketcap_model.get_cmc_top_n()
        return df
    return pd.DataFrame()
