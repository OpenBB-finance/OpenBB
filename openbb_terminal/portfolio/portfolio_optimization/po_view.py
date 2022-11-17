"""Optimization View"""
__docformat__ = "numpy"

# pylint: disable=R0913, R0914, C0302, too-many-branches, too-many-statements, line-too-long
# flake8: noqa: E501

import logging
import math
import warnings
from datetime import date
from typing import Any, Dict, List, Optional, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import riskfolio as rp
from dateutil.relativedelta import relativedelta, FR
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale, print_rich_table
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_helper,
    optimizer_model,
    po_model,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    pie_chart_weights,
)
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.rich_config import console

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
def display_ef(symbols: List[str] = None, engine: PoEngine = None, **kwargs):
    """
    Display efficient frontier

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None
    """

    symbols, engine, parameters = po_model.validate_inputs(symbols, engine, kwargs)

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

    frontier, mu, cov, stock_returns, weights, X1, Y1, port = po_model.get_ef(
        symbols,
        engine,
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
def display_plot(engine: PoEngine = None, **kwargs):
    """
    Display efficient frontier

    Parameters
    ----------
    engine : PoEngine, optional
        Portfolio optimization engine, by default None
    """

    if engine is None:
        return

    _, engine, parameters = po_model.validate_inputs(engine=engine, kwargs=kwargs)

    category: str = "SECTOR"
    if "category" in parameters:
        category = parameters["category"]

    title_opt: str = ""
    if "title" in parameters:
        title_opt = parameters["title"]

    freq: str = "D"
    if "freq" in parameters:
        freq = parameters["freq"]

    risk_measure: str = "MV"
    if "risk_measure" in parameters:
        risk_measure = parameters["risk_measure"]

    risk_free_rate: float = 0
    if "risk_free_rate" in parameters:
        risk_free_rate = parameters["risk_free_rate"]

    alpha: float = 0.05
    if "alpha" in parameters:
        alpha = parameters["alpha"]

    a_sim: float = 100
    if "a_sim" in parameters:
        a_sim = parameters["a_sim"]

    beta: float = 0
    if "beta" in parameters:
        beta = parameters["beta"]

    b_sim: float = 0
    if "b_sim" in parameters:
        b_sim = parameters["b_sim"]

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

    external_axes: Optional[List[plt.Axes]] = None
    if "external_axes" in parameters:
        external_axes = parameters["external_axes"]

    weights: pd.DataFrame = engine.get_weights_df()
    data: pd.DataFrame = engine.get_returns()

    if category:
        # weights = pd.DataFrame.from_dict(
        #     data=weights, orient="index", columns=["value"], dtype=float
        # )
        category_dict = engine.get_category(category)
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

    colors = theme.get_colors()
    if pie:
        pie_chart_weights(weights, title_opt, external_axes)

    if hist:
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

        title = "Portfolio - " + title_opt + "\n"
        title += ax.get_title(loc="left")
        ax.set_title(title)

        if external_axes is None:
            theme.visualize_output()

    if dd:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes[0]

        nav = data.cumsum()
        ax = rp.plot_drawdown(
            nav=nav, w=pd.Series(weights).to_frame(), alpha=alpha, ax=ax
        )

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

        title = "Portfolio - " + title_opt + "\n"
        title += ax.get_title(loc="left")
        ax.set_title(title)

        if external_axes is None:
            theme.visualize_output()

    if rc_chart:
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

        title = "Portfolio - " + title_opt + "\n"
        title += ax.get_title(loc="left")
        ax.set_title(title)

        if external_axes is None:
            theme.visualize_output()

    if heat:
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

        title = "Portfolio - " + title_opt + "\n"
        title += ax[3].get_title(loc="left")
        ax[3].set_title(title)

        if external_axes is None:
            theme.visualize_output(force_tight_layout=True)
