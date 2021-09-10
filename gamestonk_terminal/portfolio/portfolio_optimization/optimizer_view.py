""" Portfolio Optimization Functions"""
__docformat__ = "numpy"

import argparse
import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, expected_returns, plotting, risk_models
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_model
from gamestonk_terminal.portfolio.portfolio_optimization.optimizer_model import (
    prepare_efficient_frontier,
    process_stocks,
)


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

d_period = {
    "1d": "[1 Day]",
    "5d": "[5 Days]",
    "1mo": "[1 Month]",
    "3mo": "[3 Months]",
    "6mo": "[6 Months]",
    "1y": "[1 Year]",
    "2y": "[2 Years]",
    "5y": "[5 Years]",
    "10y": "[10 Years]",
    "ytd": "[Year-to-Date]",
    "max": "[All-time]",
}


def display_weights(weights: dict):
    """Print weights in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    """
    if not weights:
        return
    weight_df = pd.DataFrame.from_dict(data=weights, orient="index", columns=["value"])
    if math.isclose(weight_df.sum()["value"], 1, rel_tol=0.1):
        weight_df["value"] = (weight_df["value"] * 100).astype(str).apply(
            lambda s: " " + s[:4] if s.find(".") == 1 else "" + s[:5]
        ) + " %"
    else:
        weight_df["value"] = (
            weight_df["value"]
            .astype(str)
            .apply(lambda s: " " + s[:4] if s.find(".") == 1 else "" + s[:5])
            + " $"
        )

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                weight_df, headers=["Value"], showindex=True, tablefmt="fancy_grid"
            )
        )
    else:
        print(weight_df.to_string(header=False))
    print("")


def display_equal_weight(stocks: List[str], value: float, pie: bool = False):
    """Equally weighted portfolio, where weight = 1/# of stocks

    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization
    value : float
        Amount of money to allocate. 1 indicates percentage of portfolio
    pie : bool, optional
        Display a pie chart of values
    """
    values = optimizer_model.get_equal_weights(stocks, value)
    if pie:
        pie_chart_weights(values, "Equally Weighted Portfolio")

    display_weights(values)


def display_property_weighting(
    stocks: List[str], s_property: str, value: float = 1.0, pie: bool = False
):
    """Display portfolio weighted by selected property

    Parameters
    ----------
    stocks : List[str]
        Stocks in portfolio
    s_property : str
        Property to get weighted portfolio of
    value : float, optional
        Amount to allocate.  Returns percentages if set to 1.
    pie : bool, optional
        Display weights as a pie chart
    """
    values = optimizer_model.get_property_weights(stocks, s_property, value)

    if pie:
        pie_chart_weights(values, "Weighted Portfolio based on " + s_property)
    else:
        display_weights(values)


def max_sharpe(stocks: List[str], other_args: List[str]):
    """Return a portfolio that maximises the Sharpe Ratio

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="maxsharpe",
        description="Maximise the Sharpe Ratio",
    )
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

    if other_args and "-" not in other_args[0]:
        other_args.insert(0, "-r")

    parser.add_argument(
        "-r",
        "--risk-free-rate",
        type=float,
        dest="risk_free_rate",
        default=0.02,
        help="""Risk-free rate of borrowing/lending. The period of the risk-free rate
                should correspond to the frequency of expected returns.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        sp = d_period[ns_parser.period]

        ef_opt = dict(ef.max_sharpe(ns_parser.risk_free_rate))
        s_title = f"{sp} Weights that maximize Sharpe ratio with risk free level of {ns_parser.risk_free_rate}"

        weights = {
            key: ns_parser.value * round(value, 5) for key, value in ef_opt.items()
        }

        if ns_parser.pie:
            pie_chart_weights(weights, s_title)
        else:
            print(s_title)
            display_weights(weights)
            print("")

        ef.portfolio_performance(verbose=True)
        print("")

    except Exception as e:
        print(e, "\n")


def min_volatility(stocks: List[str], other_args: List[str]):
    """Return a portfolio that optimizes for minimum volatility

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="min_volatility",
        description="Optimizes for minimum volatility",
    )
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        sp = d_period[ns_parser.period]

        ef_opt = dict(ef.min_volatility())
        s_title = f"{sp} Weights that minimize volatility"

        weights = {
            key: ns_parser.value * round(value, 5) for key, value in ef_opt.items()
        }

        if ns_parser.pie:
            pie_chart_weights(weights, s_title)
        else:
            print(s_title)
            display_weights(weights)
            print("")

        ef.portfolio_performance(verbose=True)
        print("")

    except Exception as e:
        print(e, "\n")


def max_quadratic_utility(stocks: List[str], other_args: List[str]):
    """Return a portfolio that maximises the quadratic utility, given some risk aversion

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="max_quadratic_utility",
        description="Maximises the quadratic utility, given some risk aversion",
    )
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
        "-n",
        "--market-neutral",
        action="store_true",
        default=False,
        dest="market_neutral",
        help="""whether the portfolio should be market neutral (weights sum to zero), defaults to False.
        Requires negative lower weight bound.""",
    )
    if "-n" not in other_args:
        parser.add_argument(
            "--pie",
            action="store_true",
            dest="pie",
            default=False,
            help="Display a pie chart for weights. Only if neutral flag is left False.",
        )

    if other_args and "-" not in other_args[0]:
        other_args.insert(0, "-r")

    parser.add_argument(
        "-r",
        "--risk-aversion",
        type=float,
        dest="risk_aversion",
        default=1,
        help="risk aversion parameter",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        sp = d_period[ns_parser.period]

        ef_opt = dict(
            ef.max_quadratic_utility(ns_parser.risk_aversion, ns_parser.market_neutral)
        )
        s_title = f"{sp} Weights that maximise the quadratic utility with risk aversion of {ns_parser.risk_aversion}"

        weights = {
            key: ns_parser.value * round(value, 5) for key, value in ef_opt.items()
        }

        if not ns_parser.market_neutral and ns_parser.pie:
            pie_chart_weights(weights, s_title)
            ef.portfolio_performance(verbose=True)
            print("")
            return

        print(s_title)
        display_weights(weights)
        print("")
        ef.portfolio_performance(verbose=True)
        print("")

    except Exception as e:
        print(e, "\n")
        return


def efficient_risk(stocks: List[str], other_args: List[str]):
    """Return a portfolio that maximises return for a target risk. The resulting portfolio will have
    a volatility less than the target (but not guaranteed to be equal)

    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="effrisk",
        description="""Maximise return for a target risk. The resulting portfolio will have
        a volatility less than the target (but not guaranteed to be equal)""",
    )
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
        "-n",
        "--market-neutral",
        action="store_true",
        default=False,
        dest="market_neutral",
        help="""whether the portfolio should be market neutral (weights sum to zero), defaults to False.
        Requires negative lower weight bound.""",
    )
    if "-n" not in other_args:
        parser.add_argument(
            "--pie",
            action="store_true",
            dest="pie",
            default=False,
            help="Display a pie chart for weights. Only if neutral flag is left False.",
        )

    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-t")
    parser.add_argument(
        "-t",
        "--target-volatility",
        type=float,
        dest="target_volatility",
        default=0.1,
        help="The desired maximum volatility of the resulting portfolio",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        sp = d_period[ns_parser.period]

        ef_opt = dict(
            ef.efficient_risk(ns_parser.target_volatility, ns_parser.market_neutral)
        )
        s_title = f"{sp} Weights that maximize return with a maximum volatility of {ns_parser.target_volatility}"

        weights = {
            key: ns_parser.value * round(value, 5) for key, value in ef_opt.items()
        }

        if not ns_parser.market_neutral:
            if ns_parser.pie:
                pie_chart_weights(weights, s_title)
                ef.portfolio_performance(verbose=True)
                return

        print(s_title)
        display_weights(weights)
        print("")
        ef.portfolio_performance(verbose=True)
        print("")

    except Exception as e:
        print(e, "\n")


def efficient_return(stocks: List[str], other_args: List[str]):
    """Displays a portfolio that minimises volatility for a given target return ('Markowitz portfolio')

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="effret",
        description="Calculate the 'Markowitz portfolio', minimising volatility for a given target return",
    )
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
        "-n",
        "--market-neutral",
        action="store_true",
        default=False,
        dest="market_neutral",
        help="""whether the portfolio should be market neutral (weights sum to zero), defaults to False.
        Requires negative lower weight bound.""",
    )
    if "-n" not in other_args:
        parser.add_argument(
            "--pie",
            action="store_true",
            dest="pie",
            default=False,
            help="Display a pie chart for weights. Only if neutral flag is left False.",
        )

    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-t")

    parser.add_argument(
        "-t",
        "--target-return",
        type=float,
        dest="target_return",
        default=0.1,
        help="the desired return of the resulting portfolio",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        period = ns_parser.period
        stock_prices = process_stocks(stocks, period)
        ef = prepare_efficient_frontier(stock_prices)

        sp = d_period[ns_parser.period]

        ef_opt = dict(
            ef.efficient_return(ns_parser.target_return, ns_parser.market_neutral)
        )
        s_title = f"{sp} Weights that minimise volatility for a given target return of {ns_parser.target_return}"

        weights = {
            key: ns_parser.value * round(value, 5) for key, value in ef_opt.items()
        }

        if not ns_parser.market_neutral:
            if ns_parser.pie:
                pie_chart_weights(weights, s_title)
                ef.portfolio_performance(verbose=True)
                print("")
                return

        print(s_title)
        display_weights(weights)
        print("")
        ef.portfolio_performance(verbose=True)
        print("")

    except Exception as e:
        print(e, "\n")


def show_ef(stocks: List[str], other_args: List[str]):
    """Display efficient frontier

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    other_args : List[str]
        argparse other args
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ef",
        description="""This function plots random portfolios based
                    on their risk and returns and shows the efficient frontier.""",
    )
    parser.add_argument(
        "-p",
        "--period",
        default="3mo",
        dest="period",
        help="period to get yfinance data from",
        choices=period_choices,
    )
    parser.add_argument(
        "-n",
        "--number-portfolios",
        default=300,
        type=check_non_negative,
        dest="n_port",
        help="number of portfolios to simulate",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")
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
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

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

        ax.set_title(f"Efficient Frontier simulating {ns_parser.n_port} portfolios")
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
        print(e, "\n")


def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""


def pie_chart_weights(weights: dict, title_opt: str):
    """Show a pie chart of holdings

    Parameters
    ----------
    weights: dict
        Weights to display, where keys are tickers, and values are either weights or values if -v specified
    title: str
        Title to be used on the plot title
    """
    if not weights:
        return

    init_stocks = list(weights.keys())
    init_sizes = list(weights.values())
    stocks = []
    sizes = []
    for stock, size in zip(init_stocks, init_sizes):
        if size > 0:
            stocks.append(stock)
            sizes.append(size)

    total_size = np.sum(sizes)

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct=my_autopct,
            textprops=dict(color="k"),
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
    else:
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct="",
            textprops=dict(color="k"),
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
        for i, a in enumerate(autotexts):
            if sizes[i] / total_size > 0.05:
                a.set_text(f"{sizes[i]:.2f}")
            else:
                a.set_text("")

    plt.axis("equal")

    leg1 = plt.legend(
        wedges,
        [str(s) for s in stocks],
        title="  Ticker",
        loc="upper left",
        bbox_to_anchor=(0.80, 0, 0.5, 1),
        frameon=False,
    )
    leg2 = plt.legend(
        wedges,
        [
            f"{' ' if ((100*s/total_size) < 10) else ''}{100*s/total_size:.2f}%"
            for s in sizes
        ],
        title=" ",
        loc="upper left",
        handlelength=0,
        bbox_to_anchor=(0.91, 0, 0.5, 1),
        frameon=False,
    )
    plt.gca().add_artist(leg1)
    plt.gca().add_artist(leg2)

    plt.setp(autotexts, size=8, weight="bold")

    plt.gca().set_title(title_opt, pad=20)

    if gtff.USE_ION:
        plt.ion()

    plt.tight_layout()

    plt.show()
    print("")
