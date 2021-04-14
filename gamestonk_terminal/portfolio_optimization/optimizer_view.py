""" Portfolio Optimization Functions"""
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from pypfopt import plotting
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale
from gamestonk_terminal.portfolio_optimization.optimizer_helper import (
    process_stocks,
    prepare_efficient_frontier,
    pie_chart_weights,
    display_weights,
    parse_from_port_type,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

period_choices = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max",
]


def equal_weight(stocks: List[str], other_args: List[str]):
    """
    Equally weighted portfolio, where weight = 1/# of stocks

    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization

    Returns
    -------
    weights : dict
        Dictionary of weights where keys are the tickers

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="equal_weight",
        description="Return equally weighted portfolio holdings",
    )

    parser.add_argument(
        "-v",
        "--value",
        default=1,
        type=float,
        dest="value",
        help="Amount to allocate to portfolio",
    )
    parser.add_argument(
        "--pie",
        action="store_true",
        dest="pie",
        default=False,
        help="Display a pie chart for weights",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        values = {}
        n_stocks = len(stocks)
        for stock in stocks:
            values[stock] = ns_parser.value * round(1 / n_stocks, 5)
        if ns_parser.pie:
            pie_chart_weights(values, "equal", 0)
        if n_stocks >= 1:
            print("Equal Weight Portfolio: ")
            display_weights(values)
            print("")

    except Exception as e:
        print(e)
        print("")


def property_weighting(stocks: List[str], property_type: str, other_args: List[str]):
    """
    Property weighted portfolio where each weight is the relative fraction.
    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization
    property_type: str
        Property to weight by.  Can be anything in yfinance.Ticker().info.  Examples:
            "marketCap", "dividendYield", etc

    Returns
    -------
    weights: dict
        Dictionary of weights where keys are the tickers
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="market_cap_weighted",
        description="Return portfolio weights/values that are weighted by marketcap",
    )

    parser.add_argument(
        "-v",
        "--value",
        default=1,
        type=float,
        dest="value",
        help="Amount to allocate to portfolio",
    )
    parser.add_argument(
        "--pie",
        action="store_true",
        dest="pie",
        default=False,
        help="Display a pie chart for weights",
    )
    weights = {}
    prop = {}
    prop_sum = 0

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        for stock in stocks:
            stock_prop = yf.Ticker(stock).info[property_type]
            if stock_prop is None:
                stock_prop = 0
            prop[stock] = stock_prop
            prop_sum += stock_prop
        for k, v in prop.items():
            weights[k] = round(v / prop_sum, 5) * ns_parser.value

        if ns_parser.pie:
            pie_chart_weights(weights, property_type, 0)

        if property_type == "marketCap":
            print("Market Cap Weighted Portfolio: ")

        elif property_type == "dividendYield":
            print("Dividend Yield Weighted Portfolio: ")

        if len(stocks) >= 1:
            display_weights(weights)
            print("")

    except Exception as e:
        print(e)
        print("")
        return


def ef_portfolio(stocks: List[str], port_type: str, other_args: List[str]):
    """
    Return a portfolio based on condition in port_type  Defaults to 3m of historical data
    Parameters
    ----------
    stocks: List[str]
        List of the stocks to be included in the weights
    port_type: str
        Method to be used on ef object (example: max_sharpe, min_volatility)
    Returns
    -------
    weights: dict
        Dictionary of weights where keys are the tickers.
    """

    parser = argparse.ArgumentParser(add_help=False, prog="port_type")

    parser.add_argument(
        "-p",
        "--period",
        default="3mo",
        dest="period",
        help="period to get yfinance data from",
        choices=period_choices,
    )

    parser.add_argument(
        "-v",
        "--value",
        dest="value",
        help="Amount to allocate to portfolio",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--pie",
        action="store_true",
        dest="pie",
        default=False,
        help="Display a pie chart for weights",
    )

    try:
        ns_parser = parse_from_port_type(parser, port_type, other_args)
        if not ns_parser:
            return
        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return
        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        if port_type == "max_sharpe":

            ef_sharpe = dict(ef.max_sharpe())
            weights = {
                key: ns_parser.value * round(value, 5)
                for key, value in ef_sharpe.items()
            }
            val = 0
            print("Weights that maximize Sharpe Ratio:")

        elif port_type == "min_volatility":

            ef_min_vol = dict(ef.min_volatility())
            weights = {
                key: ns_parser.value * round(value, 5)
                for key, value in ef_min_vol.items()
            }
            val = 0
            print("Weights that minimize volatility")

        elif port_type == "eff_risk":

            ef_eff_risk = dict(ef.efficient_risk(ns_parser.risk_level))
            weights = {
                key: ns_parser.value * round(value, 5)
                for key, value in ef_eff_risk.items()
            }
            val = ns_parser.risk_level
            print(f"Weights for maximizing returns at risk = {100*val:.1f} %")

        elif port_type == "eff_ret":

            ef_eff_risk = dict(ef.efficient_return(ns_parser.target_return))
            weights = {
                key: ns_parser.value * round(value, 5)
                for key, value in ef_eff_risk.items()
            }
            val = ns_parser.target_return
            print(f"Weights for minimizing risk at target return = {100*val:.1f} %")

        else:
            raise ValueError("EF Method not found")

        if ns_parser.pie:
            pie_chart_weights(weights, port_type, val)

        print("")
        ef.portfolio_performance(verbose=True)
        print("")
        display_weights(weights)
        print("")

    except Exception as e:
        print(e)
        print("")
        return


def show_ef(stocks: List[str], other_args: List[str]):
    parser = argparse.ArgumentParser(add_help=False, prog="ef")

    parser.add_argument(
        "-p",
        "--period",
        default="3mo",
        dest="period",
        help="period to get yfinance data from",
        choices=period_choices,
    )
    parser.add_argument(
        "-n", default=300, dest="n_port", help="number of portfolios to simulate"
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        stock_prices = process_stocks(stocks, ns_parser.period)
        mu = expected_returns.mean_historical_return(stock_prices)
        S = risk_models.sample_cov(stock_prices)
        ef = EfficientFrontier(mu, S)
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        # Generate random portfolios
        n_samples = ns_parser.n_port
        w = np.random.dirichlet(np.ones(len(mu)), n_samples)
        rets = w.dot(mu)
        stds = np.sqrt(np.diag(w @ S @ w.T))
        sharpes = rets / stds
        ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")

        plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
        # Find the tangency portfolio
        ef.max_sharpe()
        ret_sharpe, std_sharpe, _ = ef.portfolio_performance()
        ax.scatter(std_sharpe, ret_sharpe, marker="*", s=100, c="r", label="Max Sharpe")

        ax.set_title("Efficient Frontier")
        ax.legend()
        plt.tight_layout()
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e)
        print("")
