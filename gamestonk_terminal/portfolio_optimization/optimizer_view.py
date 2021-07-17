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
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_non_negative,
)
from gamestonk_terminal.portfolio_optimization.optimizer_helper import (
    process_stocks,
    prepare_efficient_frontier,
    pie_chart_weights,
    display_weights,
    check_valid_property_type,
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


def equal_weight(stocks: List[str], other_args: List[str]):
    """Equally weighted portfolio, where weight = 1/# of stocks

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
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="equal",
        description="Returns an equally weighted portfolio",
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

        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        values = {}
        for stock in stocks:
            values[stock] = ns_parser.value * round(1 / len(stocks), 5)
        if ns_parser.pie:
            pie_chart_weights(values, "Equally Weighted Portfolio")
        else:
            display_weights(values)
            print("")

    except Exception as e:
        print(e, "\n")


def property_weighting(stocks: List[str], other_args: List[str]):
    """Weighted portfolio where each weight is the relative fraction of a specified info property.

    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="property",
        description="Returns a portfolio that is weighted based on a selected property info",
    )
    parser.add_argument(
        "-p",
        "--property",
        required=bool("-h" not in other_args),
        type=check_valid_property_type,
        dest="property",
        help="""Property info to weigh. Use one of:
        previousClose, regularMarketOpen, twoHundredDayAverage, trailingAnnualDividendYield,
        payoutRatio, volume24Hr, regularMarketDayHigh, navPrice, averageDailyVolume10Day, totalAssets,
        regularMarketPreviousClose, fiftyDayAverage, trailingAnnualDividendRate, open, toCurrency, averageVolume10days,
        expireDate, yield, algorithm, dividendRate, exDividendDate, beta, circulatingSupply, regularMarketDayLow,
        priceHint, currency, trailingPE, regularMarketVolume, lastMarket, maxSupply, openInterest, marketCap,
        volumeAllCurrencies, strikePrice, averageVolume, priceToSalesTrailing12Months, dayLow, ask, ytdReturn, askSize,
        volume, fiftyTwoWeekHigh, forwardPE, fromCurrency, fiveYearAvgDividendYield, fiftyTwoWeekLow, bid, dividendYield,
        bidSize, dayHigh, annualHoldingsTurnover, enterpriseToRevenue, beta3Year, profitMargins, enterpriseToEbitda,
        52WeekChange, morningStarRiskRating, forwardEps, revenueQuarterlyGrowth, sharesOutstanding, fundInceptionDate,
        annualReportExpenseRatio, bookValue, sharesShort, sharesPercentSharesOut, fundFamily, lastFiscalYearEnd,
        heldPercentInstitutions, netIncomeToCommon, trailingEps, lastDividendValue, SandP52WeekChange, priceToBook,
        heldPercentInsiders, shortRatio, sharesShortPreviousMonthDate, floatShares, enterpriseValue,
        threeYearAverageReturn, lastSplitFactor, legalType, lastDividendDate, morningStarOverallRating,
        earningsQuarterlyGrowth, pegRatio, lastCapGain, shortPercentOfFloat, sharesShortPriorMonth,
        impliedSharesOutstanding, fiveYearAverageReturn, and regularMarketPrice.""",
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
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if len(stocks) < 2:
            print("Please have at least 2 loaded tickers to calculate weights.\n")
            return

        weights = {}
        prop = {}
        prop_sum = 0
        for stock in stocks:
            stock_prop = yf.Ticker(stock).info[ns_parser.property]
            if stock_prop is None:
                stock_prop = 0
            prop[stock] = stock_prop
            prop_sum += stock_prop

        if prop_sum == 0:
            print(
                f"No {ns_parser.property} was found on list of tickers provided", "\n"
            )
            return

        for k, v in prop.items():
            weights[k] = round(v / prop_sum, 5) * ns_parser.value

        if ns_parser.pie:
            pie_chart_weights(
                weights, "Weighted Portfolio based on " + ns_parser.property
            )
        else:
            display_weights(weights)
            print("")

    except Exception as e:
        print(e, "\n")


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

    if other_args:
        if "-" not in other_args[0]:
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

    if other_args:
        if "-" not in other_args[0]:
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
