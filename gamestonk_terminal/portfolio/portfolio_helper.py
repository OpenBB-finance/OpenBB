"""Portfolio Helper"""
__docformat__ = "numpy"

import yfinance as yf


def is_ticker(ticker: str) -> bool:
    """Determine whether a string is a valid ticker

    Parameters
    ----------
    ticker : str
        The string to be tested

    Returns
    ----------
    answer : bool
        Whether the string is a ticker
    """
    item = yf.Ticker(ticker)
    return "previousClose" in item.info


def beta_word(beta: float) -> str:
    """Describe a beta

    Parameters
    ----------
    beta : float
        The beta for a portfolio

    Returns
    ----------
    text : str
        The description of the beta
    """
    if abs(1 - beta) > 3:
        part = "extremely "
    elif abs(1 - beta) > 2:
        part = "very "
    elif abs(1 - beta) > 1:
        part = ""
    else:
        part = "moderately "

    return part + "high" if beta > 1 else "low"


def clean_name(name: str) -> str:
    """Clean a name to a ticker

    Parameters
    ----------
    name : str
        The value to be cleaned

    Returns
    ----------
    text : str
        A cleaned value
    """
    return name.replace("beta_", "").upper()


def get_fraction(n: float, d: float) -> str:
    """Turn two numbers into a fraction

    Parameters
    ----------
    n : float
        The numerator
    d : float
        The denominator

    Returns
    ----------
    text : str
        A fraction as a string
    """
    if d > 0:
        return f"{(n/d):.2f}"
    return "N/A"
