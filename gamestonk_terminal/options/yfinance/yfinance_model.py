"""Yfinance options model"""
__docformat__ = "numpy"

import argparse
from typing import List
import yfinance as yf
import pandas as pd
import numpy as np

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


# pylint: disable=R1710


def load(other_args: List[str]) -> str:
    """Load ticker into object

    Parameters
    ----------
    other_args: List[str]
        Agrparse arguments

    Returns
    -------
    str:
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="yfload",
        description="Load a ticker into option menu",
    )

    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        required="-h" not in other_args,
        help="Stock ticker",
    )

    try:
        if other_args:
            if "-t" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        return ns_parser.ticker
    except Exception as e:
        print(e, "\n")
    except SystemExit:
        print("")
        return


def option_expirations(ticker: str):
    """Get avaialable expiration dates for given ticker

    Parameters
    ----------
    ticker: str
        Ticker to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yfticker = yf.Ticker(ticker)
    dates = list(yfticker.options)
    return dates


def select_option_date(avalaiable_dates: List[str], other_args: List[str]) -> str:
    """Select an option date out of a supplied list

    Parameters
    ----------
    avalaiable_dates: List[str]
        Possible date options
    other_args: List[str]
        Arparse arguments
    Returns
    -------
    expiry_date: str
        Selected expiry date
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="exp",
        description="See and set expiration date",
    )
    parser.add_argument(
        "-d",
        "--date",
        dest="n_date",
        action="store",
        type=int,
        default=-1,
        choices=range(len(avalaiable_dates)),
        help=f"Select index for expiry date.",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-d")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return None

        # Print possible expiry dates
        if ns_parser.n_date == -1:
            print("\nAvailable expiry dates:")
            for i, d in enumerate(avalaiable_dates):
                print(f"   {(2 - len(str(i))) * ' '}{i}.  {d} \n")
            return None

        # It means an expiry date was correctly selected
        else:
            expiry_date = avalaiable_dates[ns_parser.n_date]
            return expiry_date

    except Exception as e:
        print(e, "\n")
        return None


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
    ticker = yf.Ticker(ticker)
    chains = ticker.option_chain(expiration)
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
