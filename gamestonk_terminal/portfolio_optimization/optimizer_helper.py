""" Portfolio Optimization Helper Functions"""
__docformat__ = "numpy"

import argparse
from typing import List
import math
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import plot_autoscale, parse_known_args_and_warn

title_maps = {}


def process_stocks(list_of_stocks: List[str], period: str = "3mo") -> pd.DataFrame:
    """

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to get historical data for
    period: str
        Period to get data from yfinance

    Returns
    -------
    stock_closes: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """
    stock_prices = yf.download(
        list_of_stocks, period=period, progress=False, group_by="ticker"
    )
    stock_closes = pd.DataFrame(index=stock_prices.index)
    for stock in list_of_stocks:
        stock_closes[stock] = stock_prices[stock]["Adj Close"]
    return stock_closes


def prepare_efficient_frontier(stock_prices: pd.DataFrame):
    """
    Take in a dataframe of prices and return an efficient frontier object
    Parameters
    ----------
    stock_prices : DataFrame
        DataFrame where indices are DateTime and columns are stocks

    Returns
    -------
    ef: EfficientFrontier
        EfficientFrontier object
    """
    mu = expected_returns.mean_historical_return(stock_prices)
    S = risk_models.sample_cov(stock_prices)
    ef = EfficientFrontier(mu, S)
    return ef


def display_weights(weights: dict):
    """
    Print weights in a nice format
    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values if -v specified
    """
    if not weights:
        return
    weight_df = pd.DataFrame.from_dict(data=weights, orient="index", columns=["value"])
    weight_df["weight"] = (weight_df["value"] * 100).astype(str) + " %"
    print(weight_df["weight"])


def pie_chart_weights(weights: dict, optimizer: str):
    """
    Show a pie chart of holdings
    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values if -v specified
    optimzer: str
        Optmization technique used
    """

    if not weights:
        return

    stocks = list(weights.keys())
    sizes = list(weights.values())
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        wedges, _, autotexts = ax.pie(
            sizes,
            labels=stocks,
            autopct="%1.1f%%",
            textprops=dict(color="k"),
            labeldistance=5,
        )
    else:
        wedges, _, autotexts = ax.pie(
            sizes, labels=stocks, autopct="", textprops=dict(color="k"), labeldistance=5
        )
        for i, a in enumerate(autotexts):
            a.set_text(f"{sizes[i]}")

    ax.axis("equal")
    ax.legend(
        wedges,
        stocks,
        title="Stocks",
        loc="center left",
        bbox_to_anchor=(0.85, 0, 0.5, 1),
    )

    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title("Portfolio Holdings")
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print("")


def parse_from_port_type(
    parser_in: argparse.ArgumentParser, port_type: str, other_args: List[str]
):
    """

    Parameters
    ----------
    parser_in: ArgumentParser
        parser to get data from
    port_type: str
        Type of optimization that will be done.  One of ["max_sharpe","min_vol", "eff_risk", "eff_ret"]
    other_args: List[str]
        Arguments passed to function
    Returns
    -------

    ns_parser:
        Parsed arguments
    """

    if port_type in ["max_sharpe", "min_volatility"]:
        ns_parser = parse_known_args_and_warn(parser_in, other_args)
        if not ns_parser:
            return None
        return ns_parser

    elif port_type == "eff_risk":
        parser_in.add_argument(
            "-r", "--risk", type=float, dest="risk_level", default=0.1
        )
        ns_parser = parse_known_args_and_warn(parser_in, other_args)
        if not ns_parser:
            return None
        return ns_parser

    elif port_type == "eff_ret":
        parser_in.add_argument(
            "-r", "--return", type=float, dest="target_return", default=0.1
        )

        ns_parser = parse_known_args_and_warn(parser_in, other_args)
        if not ns_parser:
            return None
        return ns_parser
    else:
        print("Incorrect portfolio optimizer type\n")
        return None
