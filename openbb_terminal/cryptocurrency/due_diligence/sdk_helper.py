"""Crypto DD SDK helper"""
__docformat__ = "numpy"

import pandas as pd

import openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model as gecko


def dev_stats(symbol: str) -> pd.DataFrame:
    """Get developer stats for a coin

    Parameters
    ----------
    symbol : str
        Coin to get stats for

    Returns
    -------
    pd.DataFrame
        Dataframe of stats

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> btc_dev_stats = openbb.crypto.dd.dev("btc")
    """
    coin = gecko.Coin(symbol)
    return coin.get_developers_data()


def score(symbol: str) -> pd.DataFrame:
    """Get scores for a coin from CoinGecko

    Parameters
    ----------
    symbol : str
        Coin to get scores for

    Returns
    -------
    pd.DataFrame
        Dataframe of scores

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> btc_scores = openbb.crypto.dd.score("btc")
    """
    return gecko.Coin(symbol).get_scores()


def social(symbol: str) -> pd.DataFrame:
    """Get social media stats for a coin

    Parameters
    ----------
    symbol : str
        Coin to get social stats for

    Returns
    -------
    pd.DataFrame
        Dataframe of social stats

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> btc_socials = openbb.crypto.dd.social("btc")
    """
    return gecko.Coin(symbol).get_social_media()


def ath(symbol: str, currency: str = "USD") -> pd.DataFrame:
    """Get all time high for a coin in a given currency

    Parameters
    ----------
    symbol : str
        Coin to get all time high for
    currency: str
        Currency to get all time high in

    Returns
    -------
    pd.DataFrame
        Dataframe of all time high

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> btc_ath = openbb.crypto.dd.ath("btc")
    """
    return gecko.Coin(symbol).get_all_time_high(currency=currency.lower())


def atl(symbol: str, currency: str = "USD") -> pd.DataFrame:
    """Get all time low for a coin in a given currency

    Parameters
    ----------
    symbol : str
        Coin to get all time low for
    currency: str
        Currency to get all time low in

    Returns
    -------
    pd.DataFrame
        Dataframe of all time low

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> btc_atl = openbb.crypto.dd.atl("btc")
    """
    return gecko.Coin(symbol).get_all_time_low(currency=currency.lower())
