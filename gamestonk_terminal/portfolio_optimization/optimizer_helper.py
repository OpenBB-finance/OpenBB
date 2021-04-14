""" Portfolio Optimization Helper Functions"""
__docformat__ = "numpy"

import argparse
from typing import List, Optional
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import plot_autoscale, parse_known_args_and_warn

title_maps = {
    "max_sharpe": "Maximum Sharpe Portfolio",
    "min_volatility": "Minimum Volatility Portfolio",
    "eff_risk": "Maximum Return Portfolio at Risk = {:1f} %",
    "eff_ret": "Minimum Volatility Portfolio at Target Return = {:.1f} %",
    "equal": "Equally Weighted Portfolio",
    "marketCap": "MarketCap Weighted Portfolio",
    "dividendYield": "Dividend Yield Weighted Portfolio",
}


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
    if math.isclose(weight_df.sum()["value"], 1, rel_tol=0.1):
        weight_df["weight"] = (weight_df["value"] * 100).astype(str).apply(
            lambda s: s[:6]
        ) + " %"
        print(pd.DataFrame(weight_df["weight"]))
    else:
        print(weight_df)


def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"
    else:
        return ""


def pie_chart_weights(weights: dict, optimizer: str, value: Optional[float]):
    """
    Show a pie chart of holdings
    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values if -v specified
    optimzer: str
        Optimization technique used for title
    """
    plt.close("all")
    if not weights:
        return

    stocks = np.array(list(weights.keys()))
    sizes = np.array(list(weights.values()))

    to_not_include = sizes == 0

    stocks, sizes = stocks[to_not_include == False], sizes[to_not_include == False]
    total_size = np.sum(sizes)

    leg_labels = [
        f"{str(a)}: {str(round(100*b/total_size,3))[:4]}%"
        for a, b in zip(stocks, sizes)
    ]

    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct=my_autopct,
            textprops=dict(color="k"),
            explode=[s / (5 * total_size) for s in sizes],
            normalize=True,
            shadow=True,
        )
    else:
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct="",
            textprops=dict(color="k"),
            explode=[s / (5 * total_size) for s in sizes],
            normalize=True,
            shadow=True,
        )
        for i, a in enumerate(autotexts):
            if sizes[i] / total_size > 0.05:
                a.set_text(f"{sizes[i]:.2f}")
            else:
                a.set_text("")

    plt.axis("equal")

    plt.legend(
        wedges,
        leg_labels,
        title="Stocks",
        loc="center left",
        bbox_to_anchor=(0.85, 0, 0.5, 1),
    )

    plt.setp(autotexts, size=8, weight="bold")

    if optimizer in ["eff_ret", "eff_risk"]:
        plt.title(title_maps[optimizer].format(100 * value))
    else:
        plt.title(title_maps[optimizer])

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
