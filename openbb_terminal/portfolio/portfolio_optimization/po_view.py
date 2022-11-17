"""Optimization View"""
__docformat__ = "numpy"

# pylint: disable=R0913, R0914, C0302, too-many-branches, too-many-statements, line-too-long
# flake8: noqa: E501

import logging
import math
import warnings
from typing import List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import riskfolio as rp
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.portfolio.portfolio_optimization.po_model import (
    validate_inputs,
    get_ef,
)
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

risk_choices = {
    "mv": "MV",
    "mad": "MAD",
    "gmd": "GMD",
    "msv": "MSV",
    "var": "VaR",
    "cvar": "CVaR",
    "tg": "TG",
    "evar": "EVaR",
    "rg": "RG",
    "cvrg": "CVRG",
    "tgrg": "TGRG",
    "wr": "WR",
    "flpm": "FLPM",
    "slpm": "SLPM",
    "mdd": "MDD",
    "add": "ADD",
    "dar": "DaR",
    "cdar": "CDaR",
    "edar": "EDaR",
    "uci": "UCI",
    "mdd_rel": "MDD_Rel",
    "add_rel": "ADD_Rel",
    "dar_rel": "DaR_Rel",
    "cdar_rel": "CDaR_Rel",
    "edar_rel": "EDaR_Rel",
    "uci_rel": "UCI_Rel",
}

time_factor = {
    "D": 252.0,
    "W": 52.0,
    "M": 12.0,
}


@log_start_end(log=logger)
def display_ef(symbols: List[str] = None, portfolio: PoEngine = None, **kwargs):
    """
    Display efficient frontier

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio : PoEngine, optional
        Portfolio optimization engine, by default None
    """

    symbols, portfolio, parameters = validate_inputs(symbols, portfolio, kwargs)

    n_portfolios: int = 100
    if n_portfolios in parameters:
        n_portfolios = parameters["n_portfolios"]

    freq: str = "D"
    if "freq" in parameters:
        freq = parameters["freq"]

    risk_measure: str = "MV"
    if "risk_measure" in parameters:
        risk_measure = parameters["risk_measure"]

    risk_free_rate: float = 0.0
    if "risk_free_rate" in parameters:
        risk_free_rate = parameters["risk_free_rate"]

    alpha: float = 0.05
    if "alpha" in parameters:
        alpha = parameters["alpha"]

    # Pop chart args
    tangency: bool = False
    if "tangency" in parameters:
        tangency = parameters.pop("tangency")

    plot_tickers: bool = False
    if "plot_tickers" in parameters:
        plot_tickers = parameters.pop("plot_tickers")

    external_axes: Optional[List[plt.Axes]] = None
    if "external_axes" in parameters:
        external_axes = parameters.pop("external_axes")

    frontier, mu, cov, stock_returns, weights, X1, Y1, port = get_ef(
        symbols,
        portfolio,
        **parameters,
    )

    risk_free_rate = risk_free_rate / time_factor[freq.upper()]

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    ax = rp.plot_frontier(
        w_frontier=frontier,
        mu=mu,
        cov=cov,
        returns=stock_returns,
        rm=risk_choices[risk_measure.lower()],
        rf=risk_free_rate,
        alpha=alpha,
        cmap="RdYlBu",
        w=weights,
        label="",
        marker="*",
        s=16,
        c="r",
        t_factor=time_factor[freq.upper()],
        ax=ax,
    )

    # Add risk free line
    if tangency:
        ret_sharpe = (mu @ weights).to_numpy().item() * time_factor[freq.upper()]
        risk_sharpe = rp.Sharpe_Risk(
            weights,
            cov=cov,
            returns=stock_returns,
            rm=risk_choices[risk_measure.lower()],
            rf=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=b_sim,
        )
        if risk_choices[risk_measure.lower()] not in [
            "ADD",
            "MDD",
            "CDaR",
            "EDaR",
            "UCI",
        ]:
            risk_sharpe = risk_sharpe * time_factor[freq.upper()] ** 0.5

        y = ret_sharpe * 1.5
        b = risk_free_rate * time_factor[freq.upper()]
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
                rm=risk_choices[risk_measure.lower()],
                rf=risk_free_rate,
                alpha=alpha,
            )

            if risk_choices[risk_measure.lower()] not in [
                "MDD",
                "ADD",
                "CDaR",
                "EDaR",
                "UCI",
            ]:
                risk = risk * time_factor[freq.upper()] ** 0.5

            ticker_plot = ticker_plot.append(
                {"ticker": ticker, "var": risk}, ignore_index=True
            )
        ticker_plot = ticker_plot.set_index("ticker")
        ticker_plot = ticker_plot.merge(
            port.mu.T * time_factor[freq.upper()], right_index=True, left_index=True
        )
        ticker_plot = ticker_plot.rename(columns={0: "ret"})
        ax.scatter(ticker_plot["var"], ticker_plot["ret"])
        for row in ticker_plot.iterrows():
            ax.annotate(row[0], (row[1]["var"], row[1]["ret"]))
    ax.set_title(f"Efficient Frontier simulating {n_portfolios} portfolios")
    ax.legend(loc="best", scatterpoints=1)
    theme.style_primary_axis(ax)
    l, b, w, h = ax.get_position().bounds
    ax.set_position([l, b, w * 0.9, h])
    ax1 = ax.get_figure().axes
    ll, bb, ww, hh = ax1[-1].get_position().bounds
    ax1[-1].set_position([ll * 1.02, bb, ww, hh])
    if external_axes is None:
        theme.visualize_output(force_tight_layout=False)


@log_start_end(log=logger)
def display_plot(portfolio: PoEngine = None, **kwargs):
    """
    Display efficient frontier

    Parameters
    ----------
    portfolio : PoEngine, optional
        Portfolio optimization engine, by default None
    """

    if portfolio is None:
        return

    _, portfolio, parameters = validate_inputs(portfolio=portfolio, kwargs=kwargs)

    # Choose chart
    pie: bool = False
    if "pie" in parameters:
        pie = parameters["pie"]

    hist: bool = False
    if "hist" in parameters:
        hist = parameters["hist"]

    dd: bool = False
    if "dd" in parameters:
        dd = parameters["dd"]

    rc_chart: bool = False
    if "rc_chart" in parameters:
        rc_chart = parameters["rc_chart"]

    heat: bool = False
    if "heat" in parameters:
        heat = parameters["heat"]

    # Chart arguments
    if "category" not in parameters:
        parameters["category"] = "SECTOR"

    if "title" not in parameters:
        parameters["title"] = ""

    if "freq" not in parameters:
        parameters["freq"] = "D"

    if "risk_measure" not in parameters:
        parameters["risk_measure"] = "MV"

    if "risk_free_rate" not in parameters:
        parameters["risk_free_rate"] = 0.0

    if "alpha" not in parameters:
        parameters["alpha"] = 0.05

    if "a_sim" not in parameters:
        parameters["a_sim"] = 100.0

    if "beta" not in parameters:
        parameters["beta"] = 0.0

    if "b_sim" not in parameters:
        parameters["b_sim"] = 0.0

    if "external_axes" not in parameters:
        parameters["external_axes"] = None

    weights: pd.DataFrame = portfolio.get_weights_df()
    data: pd.DataFrame = portfolio.get_returns()

    category = parameters["category"]

    if category:
        # weights = pd.DataFrame.from_dict(
        #     data=weights, orient="index", columns=["value"], dtype=float
        # )
        category_dict = portfolio.get_category(category)
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

        parameters["weights"] = weights
        parameters["data"] = data
        parameters["colors"] = theme.get_colors()

        if pie:
            display_pie(**parameters)

        if hist:
            display_hist(**parameters)

        if dd:
            display_dd(**parameters)

        if rc_chart:
            display_rc_chart(**parameters)

        if heat:
            display_heat(**parameters)


@log_start_end(log=logger)
def display_heat(**kwargs):

    weights = kwargs["weights"]
    data: pd.DataFrame = kwargs["data"]
    category = kwargs["category"]
    title: str = kwargs["title"]
    external_axes: Optional[List[plt.Axes]] = kwargs["external_axes"]

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    if len(weights) <= 3:
        number_of_clusters = len(weights)
    else:
        number_of_clusters = None

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
        l, b, w, h = ax[4].get_position().bounds
        l1 = l * 0.5
        w1 = w * 0.2
        b1 = h * 0.05
        ax[4].set_position([l - l1, b + b1, w * 0.8, h * 0.95])
        # Heatmap
        l, b, w, h = ax[1].get_position().bounds
        ax[1].set_position([l - l1 - w1, b + b1, w * 0.8, h * 0.95])
        w2 = w * 0.2
        # colorbar
        l, b, w, h = ax[2].get_position().bounds
        ax[2].set_position([l - l1 - w1 - w2, b, w, h])
        # Horizontal dendrogram
        l, b, w, h = ax[3].get_position().bounds
        ax[3].set_position([l - l1 - w1, b, w * 0.8, h])
    else:
        # Vertical dendrogram
        l, b, w, h = ax[4].get_position().bounds
        l1 = l * 0.5
        w1 = w * 0.4
        b1 = h * 0.2
        ax[4].set_position([l - l1, b + b1, w * 0.6, h * 0.8])
        # Heatmap
        l, b, w, h = ax[1].get_position().bounds
        ax[1].set_position([l - l1 - w1, b + b1, w * 0.6, h * 0.8])
        w2 = w * 0.05
        # colorbar
        l, b, w, h = ax[2].get_position().bounds
        ax[2].set_position([l - l1 - w1 - w2, b, w, h])
        # Horizontal dendrogram
        l, b, w, h = ax[3].get_position().bounds
        ax[3].set_position([l - l1 - w1, b, w * 0.6, h])

    title = "Portfolio - " + title + "\n"
    title += ax[3].get_title(loc="left")
    ax[3].set_title(title)

    if external_axes is None:
        theme.visualize_output(force_tight_layout=True)


@log_start_end(log=logger)
def display_rc_chart(**kwargs):

    weights = kwargs["weights"]
    data: pd.DataFrame = kwargs["data"]
    colors = kwargs["colors"]
    risk_measure = kwargs["risk_measure"]
    risk_free_rate = kwargs["risk_free_rate"]
    title: str = kwargs["title"]
    alpha = kwargs["alpha"]
    a_sim = kwargs["a_sim"]
    beta = kwargs["beta"]
    b_sim = kwargs["b_sim"]
    freq = kwargs["freq"]
    external_axes: Optional[List[plt.Axes]] = kwargs["external_axes"]

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    ax = rp.plot_risk_con(
        w=pd.Series(weights).to_frame(),
        cov=data.cov(),
        returns=data,
        rm=risk_choices[risk_measure.lower()],
        rf=risk_free_rate,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        color=colors[1],
        t_factor=time_factor[freq.upper()],
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

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_hist(**kwargs):

    weights = kwargs["weights"]
    data: pd.DataFrame = kwargs["data"]
    colors = kwargs["colors"]
    title: str = kwargs["title"]
    alpha = kwargs["alpha"]
    external_axes: Optional[List[plt.Axes]] = kwargs["external_axes"]

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

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

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_dd(**kwargs):

    weights = kwargs["weights"]
    data: pd.DataFrame = kwargs["data"]
    colors = kwargs["colors"]
    title: str = kwargs["title"]
    alpha = kwargs["alpha"]
    external_axes: Optional[List[plt.Axes]] = kwargs["external_axes"]

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

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

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_pie(**kwargs):
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

    weights = kwargs["weights"]
    title: str = kwargs["title"]
    external_axes: Optional[List[plt.Axes]] = kwargs["external_axes"]

    if not weights:
        return

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

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

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

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""
