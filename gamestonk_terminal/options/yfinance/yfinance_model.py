"""Yfinance options model"""
__docformat__ = "numpy"

import yfinance as yf
import pandas as pd
import numpy as np


# pylint: disable=R1710


def option_expirations(ticker: str):
    """Get available expiration dates for given ticker

    Parameters
    ----------
    ticker: str
        Ticker to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yf_ticker = yf.Ticker(ticker)
    dates = list(yf_ticker.options)
    return dates


def get_option_chain(ticker: str, expiration: str):
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    ticker: str
        Ticker to get options for
    expiration: str
        Date to get options for

    Returns
    -------
    chains: yf.ticker.Options
        Options chain
    """
    yf_ticker = yf.Ticker(ticker)
    chains = yf_ticker.option_chain(expiration)
    return chains


def get_loss_at_strike(strike: float, chain: pd.DataFrame) -> float:
    """Function to get the loss at the given expiry

    Parameters
    ----------
    strike: Union[int,float]
        Value to calculate total loss at
    chain: Dataframe:
        Dataframe containing at least strike and openInterest

    Returns
    -------
    loss: Union[float,int]
        Total loss
    """

    itm_calls = chain[chain.index < strike][["OI_call"]]
    itm_calls["loss"] = (strike - itm_calls.index) * itm_calls["OI_call"]
    call_loss = itm_calls["loss"].sum()

    itm_puts = chain[chain.index > strike][["OI_put"]]
    itm_puts["loss"] = (itm_puts.index - strike) * itm_puts["OI_put"]
    put_loss = itm_puts.loss.sum()
    loss = call_loss + put_loss

    return loss


def calculate_max_pain(chain: pd.DataFrame) -> int:
    """Returns the max pain for a given call/put dataframe

    Parameters
    ----------
    chain: DataFrame
        Dataframe to calculate value from

    Returns
    -------
    max_pain : int
        Max pain value
    """

    strikes = np.array(chain.index)
    if ("OI_call" not in chain.columns) or ("OI_put" not in chain.columns):
        print("Incorrect columns.  Unable to parse max pain")
        return np.nan

    loss = []
    for price_at_exp in strikes:
        loss.append(get_loss_at_strike(price_at_exp, chain))

    chain["loss"] = loss
    max_pain = chain["loss"].idxmin()

    return max_pain
