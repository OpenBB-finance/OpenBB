"""Optimization View"""
__docformat__ = "numpy"

# pylint: disable=R0913, R0914, C0302, too-many-branches, too-many-statements, line-too-long
# flake8: noqa: E501

# IMPORTS STANDARD
import logging
import math
import warnings
from typing import Optional

# IMPORTATION THIRDPARTY
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import riskfolio as rp
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from openbb_terminal.config_terminal import theme

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.portfolio.portfolio_optimization.optimizer_helper import get_kwarg
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.portfolio.portfolio_optimization.po_model import (
    get_ef,
    validate_inputs,
)
from openbb_terminal.portfolio.portfolio_optimization.statics import (
    RISK_CHOICES,
    TIME_FACTOR,
)
from openbb_terminal.rich_config import console

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_ef(portfolio_engine: Optional[PoEngine] = None, **kwargs):
    """Display efficient frontier

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
        Use `portfolio.po.load` to load a portfolio engine
    interval : str, optional
        Interval to get data, by default '3y'
    start_date : str, optional
        If not using interval, start date string (YYYY-MM-DD), by default ""
    end_date : str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last weekday, by default ""
    log_returns : bool, optional
        If True use log returns, else arithmetic returns, by default False
    freq : str, optional
        Frequency of returns, by default 'D'. Options: 'D' for daily, 'W' for weekly, 'M' for monthly
    maxnan: float, optional
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float, optional
        Value used to replace outliers that are higher than threshold, by default 0.0
    method: str, optional
        Method used to fill nan values, by default 'time'
        For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    risk_measure: str, optional
        The risk measure used to optimize the portfolio, by default 'MV'
        Possible values are:

        - 'MV': Standard Deviation.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'CVaR': Conditional Value at Risk.
        - 'EVaR': Entropic Value at Risk.
        - 'WR': Worst Realization.
        - 'ADD': Average Drawdown of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'MDD': Maximum Drawdown of uncompounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    n_portfolios: int, optional
        Number of portfolios to simulate, by default 100
    seed: int, optional
        Seed used to generate random portfolios, by default 123

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> d = {
                "SECTOR": {
                    "AAPL": "INFORMATION TECHNOLOGY",
                    "MSFT": "INFORMATION TECHNOLOGY",
                    "AMZN": "CONSUMER DISCRETIONARY",
                },
                "CURRENT_INVESTED_AMOUNT": {
                    "AAPL": "100000.0",
                    "MSFT": "200000.0",
                    "AMZN": "300000.0",
                },
                "CURRENCY": {
                    "AAPL": "USD",
                    "MSFT": "USD",
                    "AMZN": "USD",
                },
            }
    >>> p = openbb.portfolio.po.load(symbols_categories=d)
    >>> openbb.portfolio.po.ef_chart(portfolio_engine=p)

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.ef_chart(portfolio_engine=p)
    """

    n_portfolios = get_kwarg("n_portfolios", kwargs)
    freq = get_kwarg("freq", kwargs)
    risk_measure = get_kwarg("risk_measure", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    alpha = get_kwarg("alpha", kwargs)

    # Pop chart args
    tangency = kwargs.pop("tangency", False)
    plot_tickers = kwargs.pop("plot_tickers", False)
    external_axes = kwargs.pop("external_axes", False)

    frontier, mu, cov, stock_returns, weights, X1, Y1, port = get_ef(
        portfolio_engine,
        **kwargs,
    )

    risk_free_rate = risk_free_rate / TIME_FACTOR[freq.upper()]

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    ax = rp.plot_frontier(
        w_frontier=frontier,
        mu=mu,
        cov=cov,
        returns=stock_returns,
        rm=RISK_CHOICES[risk_measure.lower()],
        rf=risk_free_rate,
        alpha=alpha,
        cmap="RdYlBu",
        w=weights,
        label="",
        marker="*",
        s=16,
        c="r",
        t_factor=TIME_FACTOR[freq.upper()],
        ax=ax,
    )

    # Add risk free line
    if tangency:
        ret_sharpe = (mu @ weights).to_numpy().item() * TIME_FACTOR[freq.upper()]
        risk_sharpe = rp.Sharpe_Risk(
            weights,
            cov=cov,
            returns=stock_returns,
            rm=RISK_CHOICES[risk_measure.lower()],
            rf=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=b_sim,
        )
        if RISK_CHOICES[risk_measure.lower()] not in [
            "ADD",
            "MDD",
            "CDaR",
            "EDaR",
            "UCI",
        ]:
            risk_sharpe = risk_sharpe * TIME_FACTOR[freq.upper()] ** 0.5

        y = ret_sharpe * 1.5
        b = risk_free_rate * TIME_FACTOR[freq.upper()]
        m = (ret_sharpe - b) / risk_sharpe
        x2 = (y - b) / m
        x = [0, x2]
        y = [b, y]
        line = Line2D(x, y, label="Capital Allocation Line")
        ax.set_xlim(xmin=min(X1) * 0.8)
        ax.add_line(line)

    ax.plot(X1, Y1, color="b")

    plot_tickers = True
    if plot_tickers:
        ticker_plot = pd.DataFrame(columns=["ticker", "var"])
        for ticker in port.cov.columns:
            weight_df = pd.DataFrame({"weights": 1}, index=[ticker])
            risk = rp.Sharpe_Risk(
                weight_df,
                cov=port.cov[ticker][ticker],
                returns=stock_returns.loc[:, [ticker]],
                rm=RISK_CHOICES[risk_measure.lower()],
                rf=risk_free_rate,
                alpha=alpha,
            )

            if RISK_CHOICES[risk_measure.lower()] not in [
                "MDD",
                "ADD",
                "CDaR",
                "EDaR",
                "UCI",
            ]:
                risk = risk * TIME_FACTOR[freq.upper()] ** 0.5

            ticker_plot = ticker_plot.append(
                {"ticker": ticker, "var": risk}, ignore_index=True
            )
        ticker_plot = ticker_plot.set_index("ticker")
        ticker_plot = ticker_plot.merge(
            port.mu.T * TIME_FACTOR[freq.upper()], right_index=True, left_index=True
        )
        ticker_plot = ticker_plot.rename(columns={0: "ret"})
        ax.scatter(ticker_plot["var"], ticker_plot["ret"])
        for row in ticker_plot.iterrows():
            ax.annotate(row[0], (row[1]["var"], row[1]["ret"]))
    ax.set_title(f"Efficient Frontier simulating {n_portfolios} portfolios")
    ax.legend(loc="best", scatterpoints=1)
    theme.style_primary_axis(ax)
    L, b, w, h = ax.get_position().bounds
    ax.set_position([L, b, w * 0.9, h])
    ax1 = ax.get_figure().axes
    ll, bb, ww, hh = ax1[-1].get_position().bounds
    ax1[-1].set_position([ll * 1.02, bb, ww, hh])

    return theme.visualize_output(force_tight_layout=False, external_axes=external_axes)


@log_start_end(log=logger)
def display_plot(
    portfolio_engine: Optional[PoEngine] = None, chart_type: str = "pie", **kwargs
):
    """
    Display efficient frontier

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
        Use `portfolio.po.load` to load a portfolio engine
    chart_type : str, optional
        Chart type, by default "pie"
        Options are "pie", "hist", "dd" or "rc"

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> d = {
                "SECTOR": {
                    "AAPL": "INFORMATION TECHNOLOGY",
                    "MSFT": "INFORMATION TECHNOLOGY",
                    "AMZN": "CONSUMER DISCRETIONARY",
                },
                "CURRENT_INVESTED_AMOUNT": {
                    "AAPL": "100000.0",
                    "MSFT": "200000.0",
                    "AMZN": "300000.0",
                },
                "CURRENCY": {
                    "AAPL": "USD",
                    "MSFT": "USD",
                    "AMZN": "USD",
                },
            }
    >>> p = openbb.portfolio.po.load(symbols_categories=d)
    >>> weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
    >>> p.get_available_categories()
    ['SECTOR', 'CURRENCY']
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="pie")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="dd")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="rc")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="heat")

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
    >>> p.get_available_categories()
    ['ASSET_CLASS',
     'SECTOR',
     'INDUSTRY',
     'COUNTRY',
     'CURRENCY']
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="pie")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="SECTOR", chart_type="hist")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="INDUSTRY", chart_type="dd")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="COUNTRY", chart_type="rc")
    >>> openbb.portfolio.po.plot(portfolio_engine=p, category="ASSET_CLASS", chart_type="heat")
    """

    if portfolio_engine is None:
        console.print("No portfolio engine found.")
        return

    available_categories = portfolio_engine.get_available_categories()

    if not available_categories:
        console.print("No categories found.")
        return
    msg = ", ".join(available_categories)
    if "category" not in kwargs:
        console.print(f"Please specify a category from the following: {msg}")
        return
    if kwargs["category"] not in available_categories:
        console.print(f"Please specify a category from the following: {msg}")
        return

    category = kwargs["category"]

    _, valid_portfolio_engine, valid_kwargs = validate_inputs(
        portfolio_engine=portfolio_engine, kwargs=kwargs
    )

    weights: pd.DataFrame = valid_portfolio_engine.get_weights_df()
    if weights.empty:
        return

    data: pd.DataFrame = valid_portfolio_engine.get_returns()
    if data.empty:
        return

    if category:
        category_dict = valid_portfolio_engine.get_category(category)
        category_df = pd.DataFrame.from_dict(
            data=category_dict, orient="index", columns=["category"]
        )
        weights = weights.join(category_df, how="inner")
        weights.sort_index(inplace=True)

        # Calculating classes returns
        classes = list(set(weights["category"]))
        weights_classes = weights.groupby(["category"]).sum()
        matrix_classes = np.zeros((len(weights), len(classes)))
        labels = weights["category"].tolist()

        j_value = 0
        for i in classes:
            matrix_classes[:, j_value] = np.array(
                [1 if x == i else 0 for x in labels], dtype=float
            )
            matrix_classes[:, j_value] = (
                matrix_classes[:, j_value]
                * weights["value"]
                / weights_classes.loc[i, "value"]
            )
            j_value += 1

        matrix_classes = pd.DataFrame(
            matrix_classes, columns=classes, index=weights.index
        )
        data = data @ matrix_classes
        weights = weights_classes["value"].copy()
        weights.replace(0, np.nan, inplace=True)
        weights.dropna(inplace=True)
        weights.sort_values(ascending=True, inplace=True)
        data = data[weights.index.tolist()]
        data.columns = [i.title() for i in data.columns]
        weights.index = [i.title() for i in weights.index]
        weights = weights.to_dict()

        valid_kwargs["weights"] = weights
        valid_kwargs["data"] = data
        valid_kwargs["colors"] = theme.get_colors()

        if chart_type == "pie":
            display_pie(**valid_kwargs)
        elif chart_type == "hist":
            display_hist(**valid_kwargs)
        elif chart_type == "dd":
            display_dd(**valid_kwargs)
        elif chart_type == "rc":
            display_rc(**valid_kwargs)
        elif chart_type == "heat":
            display_heat(**valid_kwargs)
        else:
            console.print(
                "Invalid chart type, please choose from the following: pie, hist, dd, rc, heat"
            )


@log_start_end(log=logger)
def display_heat(**kwargs):
    weights = kwargs.get("weights", None)
    data = kwargs.get("data", None)
    category = kwargs.get("category", None)
    title = kwargs.get("title", "")
    external_axes = kwargs.get("external_axes", False)

    if len(weights) == 1:
        single_key = list(weights.keys())[0].upper()
        console.print(
            f"[yellow]Heatmap needs at least two values for '{category}', only found '{single_key}'.[/yellow]"
        )
        return None

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    number_of_clusters = len(weights) if len(weights) <= 3 else None

    ax = rp.plot_clusters(
        returns=data,
        codependence="pearson",
        linkage="ward",
        k=number_of_clusters,
        max_k=10,
        leaf_order=True,
        dendrogram=True,
        cmap="RdYlBu",
        # linecolor='tab:purple',
        ax=ax,
    )

    ax = ax.get_figure().axes
    ax[0].grid(False)
    ax[0].axis("off")

    if category is None:
        # Vertical dendrogram
        L, b, w, h = ax[4].get_position().bounds
        l1 = L * 0.5
        w1 = w * 0.2
        b1 = h * 0.05
        ax[4].set_position([L - l1, b + b1, w * 0.8, h * 0.95])
        # Heatmap
        L, b, w, h = ax[1].get_position().bounds
        ax[1].set_position([L - l1 - w1, b + b1, w * 0.8, h * 0.95])
        w2 = w * 0.2
        # colorbar
        L, b, w, h = ax[2].get_position().bounds
        ax[2].set_position([L - l1 - w1 - w2, b, w, h])
        # Horizontal dendrogram
        L, b, w, h = ax[3].get_position().bounds
        ax[3].set_position([L - l1 - w1, b, w * 0.8, h])
    else:
        # Vertical dendrogram
        L, b, w, h = ax[4].get_position().bounds
        l1 = L * 0.5
        w1 = w * 0.4
        b1 = h * 0.2
        ax[4].set_position([L - l1, b + b1, w * 0.6, h * 0.8])
        # Heatmap
        L, b, w, h = ax[1].get_position().bounds
        ax[1].set_position([L - l1 - w1, b + b1, w * 0.6, h * 0.8])
        w2 = w * 0.05
        # colorbar
        L, b, w, h = ax[2].get_position().bounds
        ax[2].set_position([L - l1 - w1 - w2, b, w, h])
        # Horizontal dendrogram
        L, b, w, h = ax[3].get_position().bounds
        ax[3].set_position([L - l1 - w1, b, w * 0.6, h])

    title = "Portfolio - " + title + "\n"
    title += ax[3].get_title(loc="left")
    ax[3].set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def display_rc(**kwargs):
    weights = kwargs.get("weights", None)
    data = kwargs.get("data", None)
    colors = kwargs.get("colors", None)
    title = kwargs.get("title", "")
    external_axes = kwargs.get("external_axes", False)

    risk_measure = get_kwarg("risk_measure", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    alpha = get_kwarg("alpha", kwargs)
    a_sim = get_kwarg("a_sim", kwargs)
    beta = get_kwarg("beta", kwargs)
    b_sim = get_kwarg("b_sim", kwargs)
    freq = get_kwarg("freq", kwargs)

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    ax = rp.plot_risk_con(
        w=pd.Series(weights).to_frame(),
        cov=data.cov(),
        returns=data,
        rm=RISK_CHOICES[risk_measure.lower()],
        rf=risk_free_rate,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        color=colors[1],
        t_factor=TIME_FACTOR[freq.upper()],
        ax=ax,
    )

    # Changing colors
    for i in ax.get_children()[:-1]:
        if isinstance(i, matplotlib.patches.Rectangle):
            i.set_width(i.get_width())
            i.set_color(colors[0])

    title = "Portfolio - " + title + "\n"
    title += ax.get_title(loc="left")
    ax.set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def display_hist(**kwargs):
    weights = kwargs.get("weights", None)
    data = kwargs.get("data", None)
    colors = kwargs.get("colors", None)
    title = kwargs.get("title", "")
    external_axes = kwargs.get("external_axes", False)

    alpha = kwargs.get("alpha", 0.05)

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    ax = rp.plot_hist(data, w=pd.Series(weights).to_frame(), alpha=alpha, ax=ax)
    ax.legend(fontsize="x-small", loc="best")

    # Changing colors
    for i in ax.get_children()[:-1]:
        if isinstance(i, matplotlib.patches.Rectangle):
            i.set_color(colors[0])
            i.set_alpha(0.7)

    k = 1
    for i, j in zip(ax.get_legend().get_lines()[::-1], ax.get_lines()[::-1]):
        i.set_color(colors[k])
        j.set_color(colors[k])
        k += 1

    title = "Portfolio - " + title + "\n"
    title += ax.get_title(loc="left")
    ax.set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def display_dd(**kwargs):
    weights = kwargs.get("weights", None)
    data = kwargs.get("data", None)
    colors = kwargs.get("colors", None)
    title = kwargs.get("title", "")
    external_axes = kwargs.get("external_axes", False)

    alpha = get_kwarg("alpha", kwargs)

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    nav = data.cumsum()
    ax = rp.plot_drawdown(nav=nav, w=pd.Series(weights).to_frame(), alpha=alpha, ax=ax)

    ax[0].remove()
    ax = ax[1]
    fig = ax.get_figure()
    gs = GridSpec(1, 1, figure=fig)
    ax.set_position(gs[0].get_position(fig))
    ax.set_subplotspec(gs[0])

    # Changing colors
    ax.get_lines()[0].set_color(colors[0])
    k = 1
    for i, j in zip(ax.get_legend().get_lines()[::-1], ax.get_lines()[1:][::-1]):
        i.set_color(colors[k])
        j.set_color(colors[k])
        k += 1

    ax.get_children()[1].set_facecolor(colors[0])
    ax.get_children()[1].set_alpha(0.7)

    title = "Portfolio - " + title + "\n"
    title += ax.get_title(loc="left")
    ax.set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def display_pie(**kwargs):
    """Show a pie chart of holdings

    Parameters
    ----------
    weights: dict
        Weights to display, where keys are tickers, and values are either weights or values if -v specified
    title: str
        Title to be used on the plot title
    external_axes:Optional[List[plt.Axes]]
        Optional external axes to plot data on
    """

    weights = kwargs.get("weights", None)
    colors = kwargs.get("colors", None)
    title = kwargs.get("title", "")
    external_axes = kwargs.get("external_axes", False)

    if not weights:
        return None

    init_stocks = list(weights.keys())
    init_sizes = list(weights.values())
    symbols = []
    sizes = []
    for stock, size in zip(init_stocks, init_sizes):
        if size > 0:
            symbols.append(stock)
            sizes.append(size)

    total_size = np.sum(sizes)
    colors = theme.get_colors()

    _, ax = plt.subplots(
        figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
    )

    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        _, _, autotexts = ax.pie(
            sizes,
            labels=symbols,
            autopct=my_autopct,
            colors=colors,
            textprops=dict(color="white"),
            wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
            labeldistance=1.05,
            startangle=45,
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
    else:
        _, _, autotexts = ax.pie(
            sizes,
            labels=symbols,
            autopct="",
            colors=colors,
            textprops=dict(color="white"),
            wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
            labeldistance=1.05,
            startangle=45,
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
        for i, a in enumerate(autotexts):
            if sizes[i] / total_size > 0.05:
                a.set_text(f"{sizes[i]:.2f}")
            else:
                a.set_text("")

    ax.axis("equal")

    # leg1 = ax.legend(
    #     wedges,
    #     [str(s) for s in stocks],
    #     title="  Ticker",
    #     loc="upper left",
    #     bbox_to_anchor=(0.80, 0, 0.5, 1),
    #     frameon=False,
    # )
    # leg2 = ax.legend(
    #     wedges,
    #     [
    #         f"{' ' if ((100*s/total_size) < 10) else ''}{100*s/total_size:.2f}%"
    #         for s in sizes
    #     ],
    #     title=" ",
    #     loc="upper left",
    #     handlelength=0,
    #     bbox_to_anchor=(0.91, 0, 0.5, 1),
    #     frameon=False,
    # )
    # ax.add_artist(leg1)
    # ax.add_artist(leg2)

    plt.setp(autotexts, size=8, weight="bold")

    title = "Portfolio - " + title + "\n"
    title += "Portfolio Composition"
    ax.set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""
