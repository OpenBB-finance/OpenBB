"""Optimization View"""
__docformat__ = "numpy"

import copy
import logging
import math
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pypfopt import plotting

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_rf, plot_autoscale, print_rich_table
from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_model
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.config_terminal import theme

logger = logging.getLogger(__name__)

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

# pylint:disable=no-member


@log_start_end(log=logger)
def display_weights(weights: dict, market_neutral: bool = False):
    """Print weights in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    market_neutral : bool
        Flag indicating shorting allowed (negative weights)
    """
    if not weights:
        return
    weight_df = pd.DataFrame.from_dict(data=weights, orient="index", columns=["value"])
    if not market_neutral:
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

        print_rich_table(weight_df, headers=["Value"], show_index=True, title="Weights")

    else:
        tot_value = weight_df["value"].abs().mean()
        header = "Value ($)" if tot_value > 1.01 else "Value (%)"
        print_rich_table(weight_df, headers=[header], show_index=True, title="Weights")
    console.print("")


@log_start_end(log=logger)
def display_equal_weight(
    stocks: List[str],
    value: float,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Equally weighted portfolio, where weight = 1/# of stocks

    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization
    value : float
        Amount of money to allocate. 1 indicates percentage of portfolio
    pie : bool, optional
        Display a pie chart of values
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    values = optimizer_model.get_equal_weights(stocks, value)
    if pie:
        pie_chart_weights(values, "Equally Weighted Portfolio", external_axes)

    display_weights(values)


@log_start_end(log=logger)
def display_property_weighting(
    stocks: List[str],
    s_property: str,
    value: float = 1.0,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    values = optimizer_model.get_property_weights(stocks, s_property, value)

    if pie:
        pie_chart_weights(
            values, "Weighted Portfolio based on " + s_property, external_axes
        )
    else:
        display_weights(values)


@log_start_end(log=logger)
def display_max_sharpe(
    stocks: List[str],
    period: str,
    value: float,
    rfrate: float,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display portfolio that maximizes Sharpe Ratio over stocks

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str
        Period to look at returns from
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    rfrate : float, optional
        Risk Free Rate, by default current US T-Bill rate
    pie : bool, optional
        Boolean to show weights as a pie chart, by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    p = d_period[period]
    s_title = f"{p} Weights that maximize Sharpe ratio"
    ef_opt, ef = optimizer_model.get_maxsharpe_portfolio(stocks, period, rfrate)
    weights = {key: value * round(port_value, 5) for key, port_value in ef_opt.items()}
    if pie:
        pie_chart_weights(weights, s_title, external_axes)
    else:
        console.print("\n", s_title)
        display_weights(weights)
    ef.portfolio_performance(verbose=True, risk_free_rate=rfrate)
    console.print("")


@log_start_end(log=logger)
def display_min_volatility(
    stocks: List[str],
    period: str = "3mo",
    value: float = 1.0,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display portfolio with minimum volatility

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str
        Period to look at returns from
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    pie : bool, optional
        Boolean to show weights as a pie chart, by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    s_title = f"{d_period[period]} Weights that minimize volatility"
    ef_opt, ef = optimizer_model.get_minvol_portfolio(stocks, period)
    weights = {key: value * round(port_value, 5) for key, port_value in ef_opt.items()}
    if pie:
        pie_chart_weights(weights, s_title, external_axes)
    else:
        console.print("\n", s_title)
        display_weights(weights)
    ef.portfolio_performance(verbose=True)
    console.print("")


@log_start_end(log=logger)
def display_max_quadratic_utility(
    stocks: List[str],
    period: str = "3mo",
    value: float = 1.0,
    risk_aversion: float = 1.0,
    market_neutral: bool = False,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display portfolio weights that maximize utility function given some risk aversion

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str, optional
        Period to get data for, by default "3mo"
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    risk_aversion : float, optional
        Max risk aversion for optimization, by default 1.0
    market_neutral : bool, optional
        Boolean to allow for shorting, by default False
    pie : bool, optional
        Boolean to display weights as pie chart by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    s_title = f"{d_period[period]} Weights that maximise quadratic utility with risk aversion: {risk_aversion}"
    ef_opt, ef = optimizer_model.get_maxquadutil_portfolio(
        stocks, period, risk_aversion, market_neutral
    )
    weights = {key: value * round(port_value, 5) for key, port_value in ef_opt.items()}

    if not market_neutral and pie:
        pie_chart_weights(weights, s_title, external_axes)
        ef.portfolio_performance(verbose=True)
        console.print("")
        return

    console.print(s_title)
    display_weights(weights, market_neutral)
    ef.portfolio_performance(verbose=True)
    console.print("")


@log_start_end(log=logger)
def display_efficient_risk(
    stocks: List[str],
    period: str = "3mo",
    value: float = 1.0,
    target_volatility: float = 1.0,
    market_neutral: bool = False,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays portfolio that maximizes returns at given volatility

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str, optional
        Period to get data for, by default "3mo"
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    target_volatility : float, optional
        Target volatility level, by default 0.1
    market_neutral : bool, optional
        Boolean to allow for shorting, by default False
    pie : bool, optional
        Boolean to display weights as pie chart by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    s_title = f"{d_period[period]} Weights that maximise returns at target volatility: {target_volatility}"
    ef_opt, ef = optimizer_model.get_efficient_risk_portfolio(
        stocks, period, target_volatility, market_neutral
    )
    weights = {key: value * round(port_value, 5) for key, port_value in ef_opt.items()}

    if not market_neutral and pie:
        pie_chart_weights(weights, s_title, external_axes)
        ef.portfolio_performance(verbose=True)
        console.print("")
        return

    console.print(s_title)
    display_weights(weights, market_neutral)
    ef.portfolio_performance(verbose=True)
    console.print("")


@log_start_end(log=logger)
def display_efficient_return(
    stocks: List[str],
    period: str = "3mo",
    value: float = 1.0,
    target_return: float = 1.0,
    market_neutral: bool = False,
    pie: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays portfolio that minimizes volatility at given return

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str, optional
        Period to get data for, by default "3mo"
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    target_return : float, optional
        Target return level, by default 0.1
    market_neutral : bool, optional
        Boolean to allow for shorting, by default False
    pie : bool, optional
        Boolean to display weights as pie chart by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    """
    s_title = f"{d_period[period]} Weights that minimizes volatility at target return: {target_return}"
    ef_opt, ef = optimizer_model.get_efficient_return_portfolio(
        stocks, period, target_return, market_neutral
    )
    weights = {key: value * round(port_value, 5) for key, port_value in ef_opt.items()}

    if not market_neutral and pie:
        pie_chart_weights(weights, s_title, external_axes)
        ef.portfolio_performance(verbose=True)
        console.print("")
        return

    console.print(s_title)
    display_weights(weights, market_neutral)
    ef.portfolio_performance(verbose=True)
    console.print("")


@log_start_end(log=logger)
def display_ef(
    stocks: List[str],
    period: str = "3mo",
    n_portfolios: int = 300,
    risk_free: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display efficient frontier

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    period : str
        Time period to get returns for
    n_portfolios: int
        Number of portfolios to simulate
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot on
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]
    ef, rets, stds = optimizer_model.generate_random_portfolios(
        stocks, period, n_portfolios
    )
    # The ef needs to be deep-copied to avoid error in plotting sharpe
    ef2 = copy.deepcopy(ef)

    sharpes = rets / stds
    ax.scatter(stds, rets, marker=".", c=sharpes)
    plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
    for ticker, ret, std in zip(
        ef.tickers, ef.expected_returns, np.sqrt(np.diag(ef.cov_matrix))
    ):
        ax.scatter(std, ret, s=50, marker=".", c="w")
        ax.annotate(ticker, (std * 1.01, ret))
    # Find the tangency portfolio
    rfrate = get_rf()
    ef2.max_sharpe(risk_free_rate=rfrate)
    ret_sharpe, std_sharpe, _ = ef2.portfolio_performance(
        verbose=True, risk_free_rate=rfrate
    )
    ax.scatter(std_sharpe, ret_sharpe, marker="*", s=100, c="r", label="Max Sharpe")
    # Add risk free line
    if risk_free:
        y = ret_sharpe * 1.2
        b = get_rf()
        m = (ret_sharpe - b) / std_sharpe
        x2 = (y - b) / m
        x = [0, x2]
        y = [b, y]
        line = Line2D(x, y, label="Capital Allocation Line")
        ax.set_xlim(xmin=min(stds) * 0.8)
        ax.add_line(line)
    ax.set_title(f"Efficient Frontier simulating {n_portfolios} portfolios")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""


@log_start_end(log=logger)
def pie_chart_weights(
    weights: dict, title_opt: str, external_axes: Optional[List[plt.Axes]]
):
    """Show a pie chart of holdings

    Parameters
    ----------
    weights: dict
        Weights to display, where keys are tickers, and values are either weights or values if -v specified
    title: str
        Title to be used on the plot title
    external_axes:Optiona[List[plt.Axes]]
        Optional external axes to plot data on
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

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        wedges, _, autotexts = ax.pie(
            sizes,
            labels=stocks,
            autopct=my_autopct,
            textprops=dict(color="k"),
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
    else:
        wedges, _, autotexts = ax.pie(
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

    ax.axis("equal")

    leg1 = ax.legend(
        wedges,
        [str(s) for s in stocks],
        title="  Ticker",
        loc="upper left",
        bbox_to_anchor=(0.80, 0, 0.5, 1),
        frameon=False,
    )
    leg2 = ax.legend(
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
    ax.add_artist(leg1)
    ax.add_artist(leg2)

    plt.setp(autotexts, size=8, weight="bold")

    ax.set_title(title_opt, pad=20)

    if external_axes is None:
        theme.visualize_output()
