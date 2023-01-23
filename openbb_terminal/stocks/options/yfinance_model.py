"""Yfinance options model"""
__docformat__ = "numpy"

import logging
import math
import warnings
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import op_helpers
from openbb_terminal.stocks.options.op_helpers import Option

logger = logging.getLogger(__name__)


option_chain_cols = [
    "strike",
    "lastPrice",
    "bid",
    "ask",
    "volume",
    "openInterest",
    "impliedVolatility",
]

option_chain_dict = {"openInterest": "openinterest", "impliedVolatility": "iv"}


def get_full_option_chain(symbol: str) -> pd.DataFrame:
    """Get all options for given ticker [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.Dataframe
        Option chain
    """
    ticker = yf.Ticker(symbol)
    dates = ticker.options

    options = pd.DataFrame()

    for _date in dates:
        calls = ticker.option_chain(_date).calls
        puts = ticker.option_chain(_date).puts
        calls = calls[option_chain_cols].rename(columns=option_chain_dict)
        puts = puts[option_chain_cols].rename(columns=option_chain_dict)
        calls.columns = [x + "_c" if x != "strike" else x for x in calls.columns]
        puts.columns = [x + "_p" if x != "strike" else x for x in puts.columns]

        temp = pd.merge(calls, puts, how="outer", on="strike")
        temp["expiration"] = _date
        options = pd.concat([options, temp], axis=0).reset_index(drop=True)

    return options


# pylint: disable=W0640
@log_start_end(log=logger)
def get_option_chain_expiry(
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls: bool = True,
    puts: bool = True,
) -> pd.DataFrame:
    """Get full option chains with calculated greeks

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date for chain in format YYY-mm-dd
    calls: bool
        Flag to get calls
    puts: bool
        Flag to get puts

    Returns
    -------
    pd.DataFrame
        DataFrame of option chain.  If both calls and puts
    """
    try:
        yf_ticker = yf.Ticker(symbol)
        options = yf_ticker.option_chain(expiry)
    except ValueError:
        console.print(f"[red]{symbol} options for {expiry} not found.[/red]")
        return pd.DataFrame()

    last_price = yf_ticker.info["regularMarketPrice"]

    # Columns we want to get
    yf_option_cols = [
        "strike",
        "lastPrice",
        "bid",
        "ask",
        "volume",
        "openInterest",
        "impliedVolatility",
    ]
    # Get call and put dataframes if the booleans are true
    put_df = options.puts[yf_option_cols].copy() if puts else pd.DataFrame()
    call_df = options.calls[yf_option_cols].copy() if calls else pd.DataFrame()
    # so that the loop below doesn't break if only one call/put is supplied
    df_list, option_factor = [], []
    if puts:
        df_list.append(put_df)
        option_factor.append(-1)
    if calls:
        df_list.append(call_df)
        option_factor.append(1)
    df_list = [x[x["impliedVolatility"] > 0].copy() for x in df_list]
    # Add in greeks to each df
    # Time to expiration:
    dt = (
        datetime.strptime(expiry, "%Y-%m-%d") + timedelta(hours=16) - datetime.now()
    ).total_seconds() / (60 * 60 * 24)
    rf = get_rf()
    # Note the way the Option class is defined, put has a -1 input and call has a +1 input
    for df, option_type in zip(df_list, option_factor):
        df["Delta"] = df.apply(
            lambda x: Option(
                last_price, x.strike, rf, 0, dt, x.impliedVolatility, option_type
            ).Delta(),
            axis=1,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df["Gamma"] = df.apply(
                lambda x: Option(
                    last_price, x.strike, rf, 0, dt, x.impliedVolatility, option_type
                ).Gamma(),
                axis=1,
            )
            df["Theta"] = df.apply(
                lambda x: Option(
                    last_price, x.strike, rf, 0, dt, x.impliedVolatility, option_type
                ).Theta(),
                axis=1,
            )
    if len(df_list) == 1:
        options_df = df_list[0]
    if len(df_list) == 2:
        options_df = pd.merge(
            left=df_list[1],
            right=df_list[0],
            on="strike",
            how="outer",
            suffixes=["_call", "_put"],
        )
        # If min/max strike aren't provided, just get the middle 50% of strikes
    if min_sp == -1:
        min_strike = np.percentile(options_df["strike"], 25)
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = np.percentile(options_df["strike"], 75)
    else:
        max_strike = max_sp

    options_df = options_df[
        (options_df.strike >= min_strike) & (options_df.strike <= max_strike)
    ]
    return options_df


@log_start_end(log=logger)
def option_expirations(symbol: str):
    """Get available expiration dates for given ticker

    Parameters
    ----------
    symbol: str
        Ticker symbol to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yf_ticker = yf.Ticker(symbol)
    dates = list(yf_ticker.options)
    if not dates:
        console.print("No expiration dates found for ticker. \n")
    return dates


@log_start_end(log=logger)
def get_option_chain(symbol: str, expiry: str):
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD

    Returns
    -------
    chains: yf.ticker.Options
        Options chain
    """

    yf_ticker = yf.Ticker(symbol)
    try:
        chains = yf_ticker.option_chain(expiry)
    except Exception:
        console.print(f"[red]Error: Expiration {expiry} cannot be found.[/red]")
        chains = op_helpers.Chain(pd.DataFrame(), "yahoo")

    return chains


@log_start_end(log=logger)
def get_dividend(symbol: str) -> pd.Series:
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for

    Returns
    -------
    chains: yf.ticker.Dividends
        Dividends
    """
    yf_ticker = yf.Ticker(symbol)
    dividend = yf_ticker.dividends
    return dividend


@log_start_end(log=logger)
def get_x_values(current_price: float, options: List[Dict[str, int]]) -> List[float]:
    """Generates different price values that need to be tested"""
    x_list = list(range(101))
    mini = current_price
    maxi = current_price
    if len(options) == 0:
        mini *= 0.5
        maxi *= 1.5
    elif len(options) > 0:
        biggest = max(options, key=lambda x: x["strike"])
        smallest = min(options, key=lambda x: x["strike"])
        maxi = max(maxi, biggest["strike"]) * 1.2
        mini = min(mini, smallest["strike"]) * 0.8
    num_range = maxi - mini
    return [(x / 100) * num_range + mini for x in x_list]


def get_y_values(
    base: float,
    price: float,
    options: List[Dict[Any, Any]],
    underlying: int,
) -> float:
    """Generates y values for corresponding x values"""
    option_change = 0
    change = price - base
    for option in options:
        if option["type"] == "Call":
            abs_change = price - option["strike"] if price > option["strike"] else 0
            option_change += option["sign"] * abs_change
        elif option["type"] == "Put":
            abs_change = option["strike"] - price if price < option["strike"] else 0
            option_change += option["sign"] * abs_change
    return (change * underlying) + option_change


@log_start_end(log=logger)
def generate_data(
    current_price: float, options: List[Dict[str, int]], underlying: int
) -> Tuple[List[float], List[float], List[float]]:
    """Gets x values, and y values before and after premiums"""

    # Remove empty elements from options
    options = [o for o in options if o]

    x_vals = get_x_values(current_price, options)
    base = current_price
    total_cost = sum(x["cost"] for x in options)
    before = [get_y_values(base, x, options, underlying) for x in x_vals]
    if total_cost != 0:
        after = [
            get_y_values(base, x, options, underlying) - total_cost for x in x_vals
        ]
        return x_vals, before, after
    return x_vals, before, []


@log_start_end(log=logger)
def get_price(symbol: str) -> float:
    """Get current price for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : float
        The price of the ticker
    """
    ticker_yahoo = yf.Ticker(symbol)
    data = ticker_yahoo.history()
    last_quote = data.tail(1)["Close"].iloc[0]

    return last_quote


@log_start_end(log=logger)
def get_info(symbol: str):
    """Get info for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : float
        The info for a given ticker
    """
    tick = yf.Ticker(symbol)
    return tick.info


@log_start_end(log=logger)
def get_closing(symbol: str) -> pd.Series:
    """Get closing prices for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : List[float]
        A list of closing prices for a ticker
    """
    tick = yf.Ticker(symbol)
    return tick.history(period="1y")["Close"]


@log_start_end(log=logger)
def get_dte(date_value: str) -> int:
    """Gets days to expiration from yfinance option date"""
    return (datetime.strptime(date_value, "%Y-%m-%d") - datetime.now()).days


@log_start_end(log=logger)
def get_iv_surface(symbol: str) -> pd.DataFrame:
    """Gets IV surface for calls and puts for ticker

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get

    Returns
    -------
    pd.DataFrame
        Dataframe of DTE, Strike and IV
    """

    stock = yf.Ticker(symbol)
    dates = stock.options
    vol_df = pd.DataFrame()
    columns = ["strike", "impliedVolatility", "openInterest", "lastPrice"]
    for date_value in dates:
        df = stock.option_chain(date_value).calls[columns]
        df["dte"] = get_dte(date_value)
        vol_df = pd.concat([vol_df, df], axis=0)
        df = stock.option_chain(date_value).puts[columns]
        df["dte"] = get_dte(date_value)
        vol_df = pd.concat([vol_df, df], axis=0)
    return vol_df


@log_start_end(log=logger)
def get_binom(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    europe: bool = False,
    vol: float = None,
):
    """Gets binomial pricing for options

    Parameters
    ----------
    symbol : str
        The ticker symbol of the option's underlying asset
    expiry : str
        The expiration for the option
    strike : float
        The strike price for the option
    put : bool
        Value a put instead of a call
    europe : bool
        Value a European option instead of an American option
    vol : float
        The annualized volatility for the underlying asset
    """
    # Base variables to calculate values
    info = get_info(symbol)
    price = info["regularMarketPrice"]
    if vol is None:
        closings = get_closing(symbol)
        vol = (closings / closings.shift()).std() * (252**0.5)
    div_yield = (
        info["trailingAnnualDividendYield"]
        if info["trailingAnnualDividendYield"] is not None
        else 0
    )
    delta_t = 1 / 252
    rf = get_rf()
    exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today = date.today()
    days = (exp_date - today).days

    # Binomial pricing specific variables
    up = math.exp(vol * (delta_t**0.5))
    down = 1 / up
    prob_up = (math.exp((rf - div_yield) * delta_t) - down) / (up - down)
    prob_down = 1 - prob_up
    discount = math.exp(delta_t * rf)

    und_vals: List[List[float]] = [[price]]

    # Binomial tree for underlying values
    for i in range(days):
        cur_date = today + timedelta(days=i + 1)
        if cur_date.weekday() < 5:
            last = und_vals[-1]
            new = [x * up for x in last]
            new.append(last[-1] * down)
            und_vals.append(new)

    # Binomial tree for option values
    if put:
        opt_vals = [[max(strike - x, 0) for x in und_vals[-1]]]
    else:
        opt_vals = [[max(x - strike, 0) for x in und_vals[-1]]]

    j = 2
    while len(opt_vals[0]) > 1:
        new_vals = []
        for i in range(len(opt_vals[0]) - 1):
            if europe:
                value = (
                    opt_vals[0][i] * prob_up + opt_vals[0][i + 1] * prob_down
                ) / discount
            else:
                if put:
                    value = max(
                        (opt_vals[0][i] * prob_up + opt_vals[0][i + 1] * prob_down)
                        / discount,
                        strike - und_vals[-j][i],
                    )
                else:
                    value = max(
                        (opt_vals[0][i] * prob_up + opt_vals[0][i + 1] * prob_down)
                        / discount,
                        und_vals[-j][i] - strike,
                    )
            new_vals.append(value)
        opt_vals.insert(0, new_vals)
        j += 1

    return up, prob_up, discount, und_vals, opt_vals, days


@log_start_end(log=logger)
def get_greeks(
    symbol: str,
    expire: str,
    div_cont: float = 0,
    rf: float = None,
    opt_type: int = 1,
    mini: float = None,
    maxi: float = None,
    show_all: bool = False,
) -> pd.DataFrame:
    """
    Gets the greeks for a given option

    Parameters
    ----------
    symbol: str
        The ticker symbol value of the option
    div_cont: float
        The dividend continuous rate
    expire: str
        The date of expiration
    rf: float
        The risk-free rate
    opt_type: Union[1, -1]
        The option type 1 is for call and -1 is for put
    mini: float
        The minimum strike price to include in the table
    maxi: float
        The maximum strike price to include in the table
    show_all: bool
        Whether to show all greeks
    """

    s = get_price(symbol)
    chains = get_option_chain(symbol, expire)
    chain = chains.calls if opt_type == 1 else chains.puts

    if mini is None:
        mini = chain.strike.quantile(0.25)
    if maxi is None:
        maxi = chain.strike.quantile(0.75)

    chain = chain[chain["strike"] >= mini]
    chain = chain[chain["strike"] <= maxi]

    risk_free = rf if rf is not None else get_rf()
    expire_dt = datetime.strptime(expire, "%Y-%m-%d")
    dif = (expire_dt - datetime.now() + timedelta(hours=16)).total_seconds() / (
        60 * 60 * 24
    )
    strikes = []
    for _, row in chain.iterrows():
        vol = row["impliedVolatility"]
        opt = Option(s, row["strike"], risk_free, div_cont, dif, vol, opt_type)
        result = [
            row["strike"],
            row["impliedVolatility"],
            opt.Delta(),
            opt.Gamma(),
            opt.Vega(),
            opt.Theta(),
        ]
        if show_all:
            result += [
                opt.Rho(),
                opt.Phi(),
                opt.Charm(),
                opt.Vanna(0.01),
                opt.Vomma(0.01),
            ]
        strikes.append(result)

    columns = [
        "Strike",
        "Implied Vol",
        "Delta",
        "Gamma",
        "Vega",
        "Theta",
    ]
    if show_all:
        additional_columns = ["Rho", "Phi", "Charm", "Vanna", "Vomma"]
        columns += additional_columns

    df = pd.DataFrame(strikes, columns=columns)

    return df


@log_start_end(log=logger)
def get_vol(
    symbol: str,
    expiry: str,
) -> pd.DataFrame:
    """Plot volume

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    """
    options = get_option_chain(symbol, expiry)

    return options


@log_start_end(log=logger)
def get_volume_open_interest(
    symbol: str,
    expiry: str,
) -> pd.DataFrame:
    """Plot volume and open interest

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration
    """
    options = get_option_chain(symbol, expiry)

    return options
