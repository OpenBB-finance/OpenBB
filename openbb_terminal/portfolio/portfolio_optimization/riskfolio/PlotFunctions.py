""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
from matplotlib import cm
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
import scipy.stats as st
import scipy.cluster.hierarchy as hr
from scipy.spatial.distance import squareform
import networkx as nx
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.RiskFunctions as rk
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.AuxFunctions as af
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.DBHT as db

__all__ = [
    "plot_series",
    "plot_frontier",
    "plot_pie",
    "plot_bar",
    "plot_frontier_area",
    "plot_risk_con",
    "plot_hist",
    "plot_range",
    "plot_drawdown",
    "plot_table",
    "plot_clusters",
    "plot_dendrogram",
    "plot_network",
]

rm_names = [
    "Standard Deviation",
    "Mean Absolute Deviation",
    "Semi Standard Deviation",
    "Value at Risk",
    "Conditional Value at Risk",
    "Entropic Value at Risk",
    "Worst Realization",
    "First Lower Partial Moment",
    "Second Lower Partial Moment",
    "Max Drawdown",
    "Average Drawdown",
    "Drawdown at Risk",
    "Conditional Drawdown at Risk",
    "Entropic Drawdown at Risk",
    "Ulcer Index",
    "Gini Mean Difference",
    "Tail Gini",
    "Range",
    "Conditional Value at Risk Range",
    "Tail Gini Range",
]

rmeasures = [
    "MV",
    "MAD",
    "MSV",
    "VaR",
    "CVaR",
    "EVaR",
    "WR",
    "FLPM",
    "SLPM",
    "MDD",
    "ADD",
    "DaR",
    "CDaR",
    "EDaR",
    "UCI",
    "GMD",
    "TG",
    "RG",
    "CVRG",
    "TGRG",
]


def plot_series(returns, w, cmap="tab20", height=6, width=10, ax=None):
    r"""
    Create a chart with the compound cumulated of the portfolios.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    w : DataFrame of shape (n_assets, n_portfolios)
        Portfolio weights.
    cmap : cmap, optional
        Colorscale, represente the risk adjusted return ratio.
        The default is 'tab20'.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_series(returns=Y, w=ws, cmap='tab20', height=6, width=10,
                            ax=None)

    .. image:: images/Port_Series.png


    """
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if returns.shape[1] != w.shape[0]:
        a1 = str(returns.shape)
        a2 = str(w.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    ax.grid(linestyle=":")
    title = "Historical Compounded Cumulative Returns"
    ax.set_title(title)

    labels = w.columns.tolist()

    colormap = cm.get_cmap(cmap)
    colormap = colormap(np.linspace(0, 1, 20))

    if cmap == "gist_rainbow":
        colormap = colormap[::-1]

    cycle = plt.cycler("color", colormap)
    ax.set_prop_cycle(cycle)

    X = w.columns.tolist()
    index = returns.index.tolist()

    for i in range(len(X)):
        a = np.array(returns, ndmin=2) @ np.array(w[X[i]], ndmin=2).T
        prices = 1 + np.insert(a, 0, 0, axis=0)
        prices = np.cumprod(prices, axis=0)
        prices = np.ravel(prices).tolist()
        del prices[0]

        ax.plot_date(index, prices, "-", label=labels[i])

    ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=None, minticks=5, maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks().tolist())
    ax.set_yticklabels(["{:3.2f}".format(x) for x in ticks_loc])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_frontier(
    w_frontier,
    mu,
    cov=None,
    returns=None,
    rm="MV",
    kelly=False,
    rf=0,
    alpha=0.05,
    a_sim=100,
    beta=None,
    b_sim=None,
    cmap="viridis",
    w=None,
    label="Portfolio",
    marker="*",
    s=16,
    c="r",
    height=6,
    width=10,
    t_factor=252,
    ax=None,
):
    r"""
    Creates a plot of the efficient frontier for a risk measure specified by
    the user.

    Parameters
    ----------
    w_frontier : DataFrame
        Portfolio weights of some points in the efficient frontier.
    mu : DataFrame of shape (1, n_assets)
        Vector of expected returns, where n_assets is the number of assets.
    cov : DataFrame of shape (n_features, n_features)
        Covariance matrix, where n_features is the number of features.
    returns : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    rm : str, optional
        The risk measure used to estimate the frontier.
        The default is 'MV'. Posible values are:

        - 'MV': Standard Deviation.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'CVaR': Conditional Value at Risk.
        - 'TG': Tail Gini.
        - 'EVaR': Entropic Value at Risk.
        - 'WR': Worst Realization (Minimax).
        - 'RG': Range of returns.
        - 'CVRG': CVaR range of returns.
        - 'TGRG': Tail Gini range of returns.
        - 'MDD': Maximum Drawdown of uncompounded returns (Calmar Ratio).
        - 'ADD': Average Drawdown of uncompounded cumulative returns.
        - 'DaR': Drawdown at Risk of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.

    kelly : bool, optional
        Method used to calculate mean return. Posible values are False for
        arithmetic mean return and True for mean logarithmic return. The default
        is False.
    rf : float, optional
        Risk free rate or minimum aceptable return. The default is 0.
    alpha : float, optional
        Significante level of VaR, CVaR, Tail Gini, EVaR, CDaR and EDaR. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    cmap : cmap, optional
        Colorscale, represente the risk adjusted return ratio.
        The default is 'viridis'.
    w : DataFrame of shape (n_assets, 1), optional
        A portfolio specified by the user. The default is None.
    label : str, optional
        Name of portfolio that appear on plot legend.
        The default is 'Portfolio'.
    marker : str, optional
        Marker of w. The default is "*".
    s : float, optional
        Size of marker. The default is 16.
    c : str, optional
        Color of marker. The default is 'r'.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    t_factor : float, optional
        Factor used to annualize expected return and expected risks for
        risk measures based on returns (not drawdowns). The default is 252.
        
        .. math::
            
            \begin{align}
            \text{Annualized Return} & = \text{Return} \, \times \, \text{t_factor} \\
            \text{Annualized Risk} & = \text{Risk} \, \times \, \sqrt{\text{t_factor}}
            \end{align}
            
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib Axes
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        label = 'Max Risk Adjusted Return Portfolio'
        mu = port.mu
        cov = port.cov
        returns = port.returns

        ax = rp.plot_frontier(w_frontier=ws, mu=mu, cov=cov, returns=returns,
                               rm=rm, rf=0, alpha=0.05, cmap='viridis', w=w1,
                               label=label, marker='*', s=16, c='r',
                               height=6, width=10, t_factor=252, ax=None)

    .. image:: images/MSV_Frontier.png


    """

    if not isinstance(w_frontier, pd.DataFrame):
        raise ValueError("w_frontier must be a DataFrame")

    if not isinstance(mu, pd.DataFrame):
        raise ValueError("mu must be a DataFrame")

    if not isinstance(cov, pd.DataFrame):
        raise ValueError("cov must be a DataFrame")

    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if returns.shape[1] != w_frontier.shape[0]:
        a1 = str(returns.shape)
        a2 = str(w_frontier.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if w is not None:
        if not isinstance(w, pd.DataFrame):
            raise ValueError("w must be a DataFrame")

        if w.shape[1] > 1 and w.shape[0] == 0:
            w = w.T
        elif w.shape[1] > 1 and w.shape[0] > 0:
            raise ValueError("w must be a column DataFrame")

        if returns.shape[1] != w.shape[0]:
            a1 = str(returns.shape)
            a2 = str(w.shape)
            raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if beta is None:
        beta = alpha
    if b_sim is None:
        b_sim = a_sim

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    mu_ = np.array(mu, ndmin=2)

    if kelly == False:
        ax.set_ylabel("Expected Arithmetic Return")
    elif kelly == True:
        ax.set_ylabel("Expected Logarithmic Return")

    item = rmeasures.index(rm)
    x_label = rm_names[item] + " (" + rm + ")"
    ax.set_xlabel("Expected Risk - " + x_label)

    title = "Efficient Frontier Mean - " + x_label
    ax.set_title(title)

    X1 = []
    Y1 = []
    Z1 = []

    for i in range(w_frontier.shape[1]):
        weights = np.array(w_frontier.iloc[:, i], ndmin=2).T
        risk = rk.Sharpe_Risk(
            weights,
            cov=cov,
            returns=returns,
            rm=rm,
            rf=rf,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
        )

        if kelly == False:
            ret = mu_ @ weights
        elif kelly == True:
            ret = 1 / returns.shape[0] * np.sum(np.log(1 + returns @ weights))
        ret = ret.item() * t_factor

        if rm not in ["MDD", "ADD", "CDaR", "EDaR", "UCI"]:
            risk = risk * t_factor**0.5

        ratio = (ret - rf) / risk

        X1.append(risk)
        Y1.append(ret)
        Z1.append(ratio)

    ax1 = ax.scatter(X1, Y1, c=Z1, cmap=cmap)

    if w is not None:
        X2 = []
        Y2 = []
        for i in range(w.shape[1]):
            weights = np.array(w.iloc[:, i], ndmin=2).T
            risk = rk.Sharpe_Risk(
                weights,
                cov=cov,
                returns=returns,
                rm=rm,
                rf=rf,
                alpha=alpha,
                a_sim=a_sim,
                beta=beta,
                b_sim=b_sim,
            )
            if kelly == False:
                ret = mu_ @ weights
            elif kelly == True:
                ret = 1 / returns.shape[0] * np.sum(np.log(1 + returns @ weights))
            ret = ret.item() * t_factor

            if rm not in ["MDD", "ADD", "CDaR", "EDaR", "UCI"]:
                risk = risk * t_factor**0.5

            X2.append(risk)
            Y2.append(ret)

        ax.scatter(X2, Y2, marker=marker, s=s**2, c=c, label=label)
        ax.legend(loc="upper left")

    xmin = np.min(X1) - np.abs(np.max(X1) - np.min(X1)) * 0.1
    xmax = np.max(X1) + np.abs(np.max(X1) - np.min(X1)) * 0.1
    ymin = np.min(Y1) - np.abs(np.max(Y1) - np.min(Y1)) * 0.1
    ymax = np.max(Y1) + np.abs(np.max(Y1) - np.min(Y1)) * 0.1

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    ax.xaxis.set_major_locator(plt.AutoLocator())

    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks().tolist())
    ax.set_yticklabels(["{:.2%}".format(x) for x in ticks_loc])
    ticks_loc = ax.get_xticks().tolist()
    ax.set_xticks(ax.get_xticks().tolist())
    ax.set_xticklabels(["{:.2%}".format(x) for x in ticks_loc])

    ax.tick_params(axis="y", direction="in")
    ax.tick_params(axis="x", direction="in")

    ax.grid(linestyle=":")

    colorbar = ax.figure.colorbar(ax1)
    colorbar.set_label("Risk Adjusted Return Ratio")

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_pie(
    w, title="", others=0.05, nrow=25, cmap="tab20", height=6, width=8, ax=None
):
    r"""
    Create a pie chart with portfolio weights.

    Parameters
    ----------
    w : DataFrame of shape (n_assets, 1)
        Portfolio weights.
    title : str, optional
        Title of the chart. The default is "".
    others : float, optional
        Percentage of others section. The default is 0.05.
    nrow : int, optional
        Number of rows of the legend. The default is 25.
    cmap : cmap, optional
        Color scale used to plot each asset weight.
        The default is 'tab20'.
    height : float, optional
        Height of the image in inches. The default is 10.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax :  matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_pie(w=w1, title='Portafolio', height=6, width=10,
                         cmap="tab20", ax=None)

    .. image:: images/Pie_Chart.png


    """

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if w.shape[1] > 1 and w.shape[0] == 0:
        w = w.T
    elif w.shape[1] > 1 and w.shape[0] > 0:
        raise ValueError("w must be a column DataFrame")

    if ax is None:
        ax = plt.gca()
        fig = plt.gcf()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    labels = w.index.tolist()
    sizes = w.iloc[:, 0].tolist()
    abs_sizes = [np.absolute(s) for s in sizes]
    sizes2 = pd.DataFrame([labels, abs_sizes, sizes]).T
    sizes2.columns = ["labels", "abs_values", "values"]
    sizes2 = sizes2.sort_values(by=["abs_values"], ascending=False)
    sizes2.index = [i for i in range(0, len(labels))]
    sizes3 = sizes2.cumsum()
    sizes3["abs_values"] = sizes3["abs_values"] / sizes3["abs_values"].max()
    l = sizes3[sizes3["abs_values"] >= 1 - others].index.tolist()[0]

    a1 = sizes2["abs_values"].sum() - sizes2[sizes2.index <= l]["abs_values"].sum()
    a2 = sizes2["values"].sum() - sizes2[sizes2.index <= l]["values"].sum()
    item = pd.DataFrame(["Others", a1, a2]).T
    item.columns = ["labels", "abs_values", "values"]
    sizes2 = sizes2[sizes2.index <= l]
    sizes2 = sizes2.append(item)

    abs_sizes = sizes2["abs_values"].tolist()
    sizes = sizes2["values"].tolist()
    labels = sizes2["labels"].tolist()
    sizes2 = ["{0:.1%}".format(i) for i in sizes]

    if title == "":
        title = "Portfolio Composition"

    limit = np.round(np.min(sizes), 4)
    if limit < 0:
        title += " (Areas in Absolute Values)"

    ax.set_title(title)

    colormap = cm.get_cmap(cmap)
    colormap = colormap(np.linspace(0, 1, 20))

    if cmap == "gist_rainbow":
        colormap = colormap[::-1]

    cycle = plt.cycler("color", colormap)
    ax.set_prop_cycle(cycle)

    size = 0.4

    # set up style cycles

    wedges, texts = ax.pie(
        abs_sizes,
        radius=1,
        wedgeprops=dict(width=size, edgecolor="black"),
        startangle=-15,
        normalize=True,
    )

    # Equal aspect ratio ensures that pie is drawn as a circle.

    ax.axis("equal")

    n = int(np.ceil(l / nrow))

    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5), ncol=n)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(
        xycoords="data",
        textcoords="data",
        arrowprops=dict(arrowstyle="-"),
        bbox=bbox_props,
        zorder=0,
        va="center",
    )

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        name = str(labels[i]) + " " + str(sizes2[i])
        ax.annotate(
            name,
            xy=(x, y),
            xytext=(1.1 * np.sign(x), 1.1 * y),
            horizontalalignment=horizontalalignment,
            **kw
        )

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_bar(
    w,
    title="",
    kind="v",
    others=0.05,
    nrow=25,
    cpos="tab:green",
    cneg="darkorange",
    cothers="dodgerblue",
    height=6,
    width=10,
    ax=None,
):
    r"""
    Create a bar chart with portfolio weights.

    Parameters
    ----------
    w : DataFrame of shape (n_assets, 1)
        Portfolio weights.
    title : str, optional
        Title of the chart. The default is "".
    kind : str, optional
        Kind of bar plot, "v" for vertical bars and "h" for horizontal bars.
        The default is "v".
    others : float, optional
        Percentage of others section. The default is 0.05.
    nrow : int, optional
        Max number of bars that be plotted. The default is 25.
    cpos : str, optional
        Color for positives weights. The default is 'tab:green'.
    cneg : str, optional
        Color for negatives weights. The default is 'darkorange'.
    cothers : str, optional
        Color for others bar. The default is 'dodgerblue'.
    height : float, optional
        Height of the image in inches. The default is 10.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax :  matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_bar(w, title='Portafolio', kind="v", others=0.05,
                         nrow=25, height=6, width=10, ax=None)

    .. image:: images/Bar_Chart.png


    """

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if w.shape[1] > 1 and w.shape[0] == 0:
        w = w.T
    elif w.shape[1] > 1 and w.shape[0] > 0:
        raise ValueError("w must be a column DataFrame")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    labels = w.index.tolist()
    sizes = w.iloc[:, 0].tolist()
    abs_sizes = [np.absolute(s) for s in sizes]
    sizes2 = pd.DataFrame([labels, abs_sizes, sizes]).T
    sizes2.columns = ["labels", "abs_values", "values"]
    sizes2 = sizes2.sort_values(by=["abs_values"], ascending=False)
    sizes2.index = [i for i in range(0, len(labels))]
    sizes3 = sizes2.cumsum()
    sizes3["abs_values"] = sizes3["abs_values"] / sizes3["abs_values"].max()

    l1 = sizes3[sizes3["abs_values"] >= 1 - others].index.tolist()
    if len(l1) > 0:
        l1 = l1[0]
    else:
        l1 = -1

    l2 = sizes2[sizes2["abs_values"] < 0.01].index.tolist()
    if len(l2) > 0:
        l2 = l2[0]
    else:
        l2 = -1

    if l1 > nrow:
        a1 = sizes2["abs_values"].sum() - sizes2[sizes2.index <= l1]["abs_values"].sum()
        a2 = sizes2["values"].sum() - sizes2[sizes2.index <= l1]["values"].sum()
        item = pd.DataFrame(["Others", a1, a2]).T
        item.columns = ["labels", "abs_values", "values"]
        sizes2 = sizes2[sizes2.index <= l1]
        sizes2 = sizes2.sort_values(by=["values"], ascending=False)
        sizes2 = sizes2.append(item)
    elif l2 > 0:
        a1 = sizes2["abs_values"].sum() - sizes2[sizes2.index <= l2]["abs_values"].sum()
        a2 = sizes2["values"].sum() - sizes2[sizes2.index <= l2]["values"].sum()
        item = pd.DataFrame(["Others", a1, a2]).T
        item.columns = ["labels", "abs_values", "values"]
        sizes2 = sizes2[sizes2.index <= l2]
        sizes2 = sizes2.sort_values(by=["values"], ascending=False)
        sizes2 = sizes2.append(item)
    else:
        sizes2 = sizes2.sort_values(by=["values"], ascending=False)

    sizes = sizes2["values"].tolist()
    labels = sizes2["labels"].tolist()
    sizes2 = ["{0:.1%}".format(i) for i in sizes]

    if title == "":
        title = "Portfolio Composition"

    ax.set_title(title)

    if kind == "v":
        sizes = np.array(sizes)
        labels = np.array(labels)
        ax.bar(labels, np.where(sizes >= 0, sizes, 0), color=cpos, width=0.5)
        ax.bar(labels, np.where(sizes < 0, sizes, 0), color=cneg, width=0.5)

        if l1 > nrow:
            ax.bar(
                labels, np.where(labels == "Others", sizes, 0), color=cothers, width=0.5
            )
            b = "Others (Sum Abs < " + "{:.1%}".format(others) + ")"
        elif l2 > 0:
            ax.bar(
                labels, np.where(labels == "Others", sizes, 0), color=cothers, width=0.5
            )
            b = "Others (Abs < " + "{:.1%}".format(0.01) + ")"

        ticks_loc = ax.get_yticks().tolist()
        ax.set_yticks(ax.get_yticks().tolist())
        ax.set_yticklabels(["{:.2%}".format(x) for x in ticks_loc])
        ax.set_xlim(-0.5, len(sizes) - 0.5)

        r = plt.gcf().canvas.get_renderer()
        transf = ax.transData.inverted()

        for i, v in enumerate(sizes):
            t = ax.text(i, v, sizes2[i], color="black")
            bb = t.get_window_extent(renderer=r)
            bb = bb.transformed(transf)
            h_text = bb.height
            x_text = bb.x0 - (bb.x1 - bb.x0) * 0.4
            y_text = bb.y0
            if v >= 0:
                t.set_position((x_text, y_text + h_text * 0.8))
            else:
                t.set_position((x_text, y_text - h_text))

    elif kind == "h":
        sizes.reverse()
        labels.reverse()
        sizes2.reverse()
        sizes = np.array(sizes)
        labels = np.array(labels)
        ax.barh(labels, np.where(sizes >= 0, sizes, 0), color=cpos, height=0.5)
        ax.barh(labels, np.where(sizes < 0, sizes, 0), color=cneg, height=0.5)

        if l1 > nrow:
            ax.barh(
                labels,
                np.where(labels == "Others", sizes, 0),
                color=cothers,
                height=0.5,
            )
            b = "Others (Sum Abs < " + "{:.1%}".format(others) + ")"
        elif l2 > 0:
            ax.barh(
                labels,
                np.where(labels == "Others", sizes, 0),
                color=cothers,
                height=0.5,
            )
            b = "Others (Abs < " + "{:.1%}".format(0.01) + ")"
        else:
            b = None

        ticks_loc = ax.get_xticks().tolist()
        ax.set_xticks(ax.get_xticks().tolist())
        ax.set_xticklabels(["{:.2%}".format(x) for x in ticks_loc])
        ax.set_ylim(-0.5, len(sizes) - 0.5)

        r = plt.gcf().canvas.get_renderer()
        transf = ax.transData.inverted()

        for i, v in enumerate(sizes):
            t = ax.text(v, i, sizes2[i], color="black")
            bb = t.get_window_extent(renderer=r)
            bb = bb.transformed(transf)
            w_text = bb.width
            x_text = bb.x0
            y_text = bb.y0
            if v >= 0:
                t.set_position((x_text + w_text * 0.15, y_text))
            else:
                t.set_position((x_text - w_text, y_text))

    ax.grid(linestyle=":")

    if b is None:
        ax.legend(["Positive Weights", "Negative Weights"])
    else:
        ax.legend(["Positive Weights", "Negative Weights", b])

    if kind == "v":
        ax.axhline(y=0, xmin=0, xmax=1, color="gray", label=False)
    elif kind == "h":
        ax.axvline(x=0, ymin=0, ymax=1, color="gray", label=False)

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_frontier_area(w_frontier, nrow=25, cmap="tab20", height=6, width=10, ax=None):
    r"""
    Create a chart with the asset composition of the efficient frontier.

    Parameters
    ----------
    w_frontier : DataFrame
        Weights of portfolios in the efficient frontier.
    nrow : int, optional
        Number of rows of the legend. The default is 25.
    cmap : cmap, optional
        Color scale used to plot each asset weight.
        The default is 'tab20'.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax :  matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_frontier_area(w_frontier=ws, cmap="tab20", height=6,
                                   width=10, ax=None)

    .. image:: images/Area_Frontier.png


    """

    if not isinstance(w_frontier, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    ax.set_title("Efficient Frontier's Assets Structure")
    labels = w_frontier.index.tolist()

    colormap = cm.get_cmap(cmap)
    colormap = colormap(np.linspace(0, 1, 20))

    if cmap == "gist_rainbow":
        colormap = colormap[::-1]

    cycle = plt.cycler("color", colormap)
    ax.set_prop_cycle(cycle)

    X = w_frontier.columns.tolist()

    ax.stackplot(X, w_frontier, labels=labels, alpha=0.7, edgecolor="black")

    ax.set_ylim(0, 1)
    ax.set_xlim(0, len(X) - 1)

    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks().tolist())
    ax.set_yticklabels(["{:3.2%}".format(x) for x in ticks_loc])
    ax.grid(linestyle=":")

    n = int(np.ceil(len(labels) / nrow))

    ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5), ncol=n)

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_risk_con(
    w,
    cov=None,
    returns=None,
    rm="MV",
    rf=0,
    alpha=0.05,
    a_sim=100,
    beta=None,
    b_sim=None,
    color="tab:blue",
    height=6,
    width=10,
    t_factor=252,
    ax=None,
):
    r"""
    Create a chart with the risk contribution per asset of the portfolio.

    Parameters
    ----------
    w : DataFrame of shape (n_assets, 1)
        Portfolio weights.
    cov : DataFrame of shape (n_features, n_features)
        Covariance matrix, where n_features is the number of features.
    returns : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    rm : str, optional
        Risk measure used to estimate risk contribution.
        The default is 'MV'. Posible values are:

        - 'MV': Standard Deviation.
        - 'MAD': Mean Absolute Deviation.
        - 'GMD': Gini Mean Difference.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'CVaR': Conditional Value at Risk.
        - 'TG': Tail Gini.
        - 'EVaR': Entropic Value at Risk.
        - 'WR': Worst Realization (Minimax).
        - 'RG': Range of returns.
        - 'CVRG': CVaR range of returns.
        - 'TGRG': Tail Gini range of returns.
        - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
        - 'ADD': Average Drawdown of uncompounded cumulative returns.
        - 'DaR': Drawdown at Risk of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.

    rf : float, optional
        Risk free rate or minimum aceptable return. The default is 0.
    alpha : float, optional
        Significante level of VaR, CVaR, Tail Gini, EVaR, CDaR and EDaR. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    color : str, optional
        Color used to plot each asset risk contribution.
        The default is 'tab:blue'.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    t_factor : float, optional
        Factor used to annualize expected return and expected risks for
        risk measures based on returns (not drawdowns). The default is 252.
        
        .. math::
            
            \begin{align}
            \text{Annualized Return} & = \text{Return} \, \times \, \text{t_factor} \\
            \text{Annualized Risk} & = \text{Risk} \, \times \, \sqrt{\text{t_factor}}
            \end{align}
            
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax :  matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_risk_con(w=w2, cov=cov, returns=returns, rm=rm,
                              rf=0, alpha=0.05, color="tab:blue", height=6,
                              width=10, t_factor=252, ax=None)

    .. image:: images/Risk_Con.png


    """

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if beta is None:
        beta = alpha
    if b_sim is None:
        b_sim = a_sim

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    item = rmeasures.index(rm)
    title = "Risk (" + rm_names[item] + ") Contribution per Asset"
    ax.set_title(title)

    X = w.index.tolist()

    RC = rk.Risk_Contribution(
        w,
        cov=cov,
        returns=returns,
        rm=rm,
        rf=rf,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
    )

    if rm not in ["MDD", "ADD", "CDaR", "EDaR", "UCI"]:
        RC = RC * t_factor**0.5

    ax.bar(X, RC, alpha=0.7, color=color, edgecolor="black")

    ax.set_xlim(-0.5, len(X) - 0.5)
    ax.tick_params(axis="x", labelrotation=90)

    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(["{:3.4%}".format(x) for x in ticks_loc])
    ax.grid(linestyle=":")

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_hist(returns, w, alpha=0.05, a_sim=100, bins=50, height=6, width=10, ax=None):
    r"""
    Create a histogram of portfolio returns with the risk measures.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    w : DataFrame of shape (n_assets, 1)
        Portfolio weights.
    alpha : float, optional
        Significante level of VaR, CVaR, Tail Gini and EVaR. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    bins : float, optional
        Number of bins of the histogram. The default is 50.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_hist(returns=Y, w=w1, alpha=0.05, bins=50, height=6,
                          width=10, ax=None)

    .. image:: images/Histogram.png


    """

    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if w.shape[1] > 1 and w.shape[0] == 0:
        w = w.T
    elif w.shape[1] > 1 and w.shape[0] > 0:
        raise ValueError("w must be a  DataFrame")

    if returns.shape[1] != w.shape[0]:
        a1 = str(returns.shape)
        a2 = str(w.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    a = np.array(returns, ndmin=2) @ np.array(w, ndmin=2)
    ax.set_title("Portfolio Returns Histogram")
    n, bins1, patches = ax.hist(
        a, bins, density=1, edgecolor="skyblue", color="skyblue", alpha=0.5
    )
    mu = np.mean(a)
    sigma = np.std(a, axis=0, ddof=1).item()
    risk = [
        mu,
        mu - sigma,
        mu - rk.MAD(a),
        mu - rk.GMD(a),
        -rk.VaR_Hist(a, alpha),
        -rk.CVaR_Hist(a, alpha),
        -rk.TG(a, alpha),
        -rk.EVaR_Hist(a, alpha)[0],
        -rk.WR(a),
    ]
    label = [
        "Mean: " + "{0:.2%}".format(risk[0]),
        "Mean - Std. Dev.("
        + "{0:.2%}".format(-risk[1] + mu)
        + "): "
        + "{0:.2%}".format(risk[1]),
        "Mean - MAD("
        + "{0:.2%}".format(-risk[2] + mu)
        + "): "
        + "{0:.2%}".format(risk[2]),
        "Mean - GMD("
        + "{0:.2%}".format(-risk[3] + mu)
        + "): "
        + "{0:.2%}".format(risk[3]),
        "{0:.2%}".format((1 - alpha)) + " Confidence VaR: " + "{0:.2%}".format(risk[4]),
        "{0:.2%}".format((1 - alpha))
        + " Confidence CVaR: "
        + "{0:.2%}".format(risk[5]),
        "{0:.2%}".format((1 - alpha))
        + " Confidence Tail Gini: "
        + "{0:.2%}".format(risk[6]),
        "{0:.2%}".format((1 - alpha))
        + " Confidence EVaR: "
        + "{0:.2%}".format(risk[7]),
        "Worst Realization: " + "{0:.2%}".format(risk[8]),
    ]
    color = [
        "b",
        "r",
        "fuchsia",
        "navy",
        "darkorange",
        "limegreen",
        "mediumvioletred",
        "dodgerblue",
        "darkgrey",
    ]

    for i, j, k in zip(risk, label, color):
        ax.axvline(x=i, color=k, linestyle="-", label=j)

    # add a 'best fit' line
    y = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(
        -0.5 * (1 / sigma * (bins1 - mu)) ** 2
    )
    ax.plot(
        bins1,
        y,
        "--",
        color="orange",
        label="Normal: $\mu="
        + "{0:.2%}".format(mu)
        + "$%, $\sigma="
        + "{0:.2%}".format(sigma)
        + "$%",
    )

    factor = (np.max(a) - np.min(a)) / bins

    ax.xaxis.set_major_locator(plt.AutoLocator())
    ticks_loc = ax.get_xticks().tolist()
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(["{:3.2%}".format(x) for x in ticks_loc])
    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(["{:3.2%}".format(x * factor) for x in ticks_loc])
    ax.legend(loc="upper right")  # , fontsize = 'x-small')
    ax.grid(linestyle=":")
    ax.set_ylabel("Probability Density")

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_range(
    returns,
    w,
    alpha=0.05,
    a_sim=100,
    beta=None,
    b_sim=None,
    bins=50,
    height=6,
    width=10,
    ax=None,
):
    r"""
    Create a histogram of portfolio returns with the range risk measures.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    w : DataFrame of shape (n_assets, 1)
        Portfolio weights.
    alpha : float, optional
        Significance level of CVaR and Tail Gini of losses.
        The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    bins : float, optional
        Number of bins of the histogram. The default is 50.
    height : float, optional
        Height of the image in inches. The default is 6.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis.
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = plot_range(returns=Y, w=w1, alpha=0.05, a_sim=100, beta=None,
                        b_sim=None, bins=50, height=6, width=10, ax=None)

    .. image:: images/Range.png


    """

    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if w.shape[1] > 1 and w.shape[0] == 0:
        w = w.T
    elif w.shape[1] > 1 and w.shape[0] > 0:
        raise ValueError("w must be a  DataFrame")

    if returns.shape[1] != w.shape[0]:
        a1 = str(returns.shape)
        a2 = str(w.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if beta is None:
        beta = alpha
    if b_sim is None:
        b_sim = a_sim

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    a = np.array(returns, ndmin=2) @ np.array(w, ndmin=2)
    ax.set_title("Portfolio Returns Range")

    df = dict(
        risk=["Range", "Tail Gini Range", "CVaR Range"],
        lower=[],
        upper=[],
    )

    df["lower"].append(np.min(a))
    df["lower"].append(-rk.TG(a, alpha=alpha, a_sim=a_sim))
    df["lower"].append(-rk.CVaR_Hist(a, alpha=alpha))
    df["upper"].append(-np.min(-a))
    df["upper"].append(rk.TG(-a, alpha=beta, a_sim=b_sim))
    df["upper"].append(rk.CVaR_Hist(-a, alpha=beta))
    df = pd.DataFrame(df)
    df.set_index("risk", inplace=True)

    # Func to draw line segment
    def newline(p1, p2, color="black"):
        ax = fig.gca()
        l = mlines.Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=color)
        ax.add_line(l)
        return l

    n, _, _ = ax.hist(a, bins=bins, density=True, color="darkgrey", alpha=0.3)

    risk = [
        rk.RG(a),
        rk.CVRG(a, alpha=alpha, beta=beta),
        rk.TGRG(a, alpha=alpha, a_sim=a_sim, beta=beta, b_sim=b_sim),
    ]

    label = [
        "Range :" + "{0:.2%}".format(risk[0]),
        "Tail Gini Range ("
        + "{0:.1%}".format((1 - alpha))
        + ", "
        + "{0:.1%}".format((1 - beta))
        + "): "
        + "{0:.2%}".format(risk[1]),
        "CVaR Range ("
        + "{0:.1%}".format((1 - alpha))
        + ", "
        + "{0:.1%}".format((1 - beta))
        + "): "
        + "{0:.2%}".format(risk[2]),
    ]

    colors = ["dodgerblue", "fuchsia", "limegreen"]

    y_max = np.ceil(n.max())

    j = 1
    for i in df.index:
        x1 = df.loc[i, "lower"]
        x2 = df.loc[i, "upper"]
        y1 = j * y_max / 4
        ax.vlines(
            x=x1,
            ymin=0,
            ymax=y1,
            color=colors[j - 1],
            alpha=1,
            linewidth=1,
            linestyles="dashed",
        )
        ax.vlines(
            x=x2,
            ymin=0,
            ymax=y1,
            color=colors[j - 1],
            alpha=1,
            linewidth=1,
            linestyles="dashed",
        )
        ax.scatter(y=y1, x=x1, s=50, color=colors[j - 1], alpha=1, label=label[j - 1])
        ax.scatter(y=y1, x=x2, s=50, color=colors[j - 1], alpha=1)
        newline([x1, y1], [x2, y1], color=colors[j - 1])
        j += 1

    ax.set(ylim=(0, y_max))

    factor = (np.max(a) - np.min(a)) / bins
    ax.xaxis.set_major_locator(plt.AutoLocator())
    ticks_loc = ax.get_xticks().tolist()
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(["{:3.2%}".format(x) for x in ticks_loc])
    ticks_loc = ax.get_yticks().tolist()
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(["{:3.2%}".format(x * factor) for x in ticks_loc])
    ax.legend(loc="upper right")  # , fontsize = 'x-small')
    ax.grid(linestyle=":")
    ax.set_ylabel("Probability Density")

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_drawdown(nav, w, alpha=0.05, height=8, width=10, ax=None):
    r"""
    Create a chart with the evolution of portfolio prices and drawdown.

    Parameters
    ----------
    nav : DataFrame
        Cumulative assets returns.
    w : DataFrame, optional
        A portfolio specified by the user to compare with the efficient
        frontier. The default is None.
    alpha : float, optional
        Significante level of DaR and CDaR. The default is 0.05.
    height : float, optional
        Height of the image in inches. The default is 8.
    width : float, optional
        Width of the image in inches. The default is 10.
    ax : matplotlib axis of size (2,1), optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : np.array
        Returns the a np.array with Axes objects with plots for further tweaking.

    Example
    -------
    ::

        nav=port.nav

        ax = rp.plot_drawdown(nav=nav, w=w1, alpha=0.05, height=8, width=10, ax=None)

    .. image:: images/Drawdown.png


    """

    if not isinstance(nav, pd.DataFrame):
        raise ValueError("nav must be a DataFrame")

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if w.shape[1] > 1 and w.shape[0] == 0:
        w = w.T
    elif w.shape[1] > 1 and w.shape[0] > 0:
        raise ValueError("w must be a  DataFrame")

    if nav.shape[1] != w.shape[0]:
        a1 = str(nav.shape)
        a2 = str(w.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if ax is None:
        fig = plt.gcf()
        ax = fig.subplots(nrows=2, ncols=1)
        ax = np.ravel(ax)
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        if isinstance(ax, plt.Axes):
            fig = ax.get_figure()
            gs = GridSpec(2, 1, figure=fig)
            ax.set_position(gs[0].get_position(fig))
            ax.set_subplotspec(gs[0])
            fig.add_subplot(gs[1])
            ax = fig.axes
        elif (
            len(np.ravel(ax)) > 2
            or not isinstance(ax[0], plt.Axes)
            or not isinstance(ax[1], plt.Axes)
        ):
            print("ax must be an array with two Axes or a subplot with 2 rows")
            return
        ax = np.ravel(ax)
        fig = ax[0].get_figure()

    index = nav.index.tolist()
    a = nav.to_numpy()
    a = np.insert(a, 0, 0, axis=0)
    a = np.diff(a, axis=0)
    a = a @ w.to_numpy()
    prices = 1 + np.insert(a, 0, 0, axis=0)
    prices = np.cumprod(prices, axis=0)
    prices = np.ravel(prices).tolist()
    prices2 = 1 + np.array(np.cumsum(a, axis=0))
    prices2 = np.ravel(prices2).tolist()
    del prices[0]

    DD = []
    peak = -99999
    for i in range(0, len(prices)):
        if prices2[i] > peak:
            peak = prices2[i]
        DD.append((peak - prices2[i]))
    DD = -np.array(DD)
    titles = [
        "Historical Compounded Cumulative Returns",
        "Historical Uncompounded Drawdown",
    ]
    data = [prices, DD]
    color1 = ["b", "orange"]
    risk = [
        -rk.UCI_Abs(a),
        -rk.ADD_Abs(a),
        -rk.DaR_Abs(a, alpha),
        -rk.CDaR_Abs(a, alpha),
        -rk.EDaR_Abs(a, alpha)[0],
        -rk.MDD_Abs(a),
    ]
    label = [
        "Ulcer Index: " + "{0:.2%}".format(risk[0]),
        "Average Drawdown: " + "{0:.2%}".format(risk[1]),
        "{0:.2%}".format((1 - alpha)) + " Confidence DaR: " + "{0:.2%}".format(risk[2]),
        "{0:.2%}".format((1 - alpha))
        + " Confidence CDaR: "
        + "{0:.2%}".format(risk[3]),
        "{0:.2%}".format((1 - alpha))
        + " Confidence EDaR: "
        + "{0:.2%}".format(risk[4]),
        "Maximum Drawdown: " + "{0:.2%}".format(risk[5]),
    ]
    color2 = ["b", "r", "fuchsia", "limegreen", "dodgerblue", "darkgrey"]

    j = 0

    ymin = np.min(DD) * 1.5

    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    formatter = mdates.DateFormatter("%Y-%m")
    for i in ax:
        i.clear()
        i.plot_date(index, data[j], "-", color=color1[j])
        if j == 1:
            i.fill_between(index, 0, data[j], facecolor=color1[j], alpha=0.3)
            for k in range(0, len(risk)):
                i.axhline(y=risk[k], color=color2[k], linestyle="-", label=label[k])
            i.set_ylim(ymin, 0)
            i.legend(loc="lower right")  # , fontsize = 'x-small')
        i.set_title(titles[j])
        i.xaxis.set_major_locator(locator)
        i.xaxis.set_major_formatter(formatter)
        ticks_loc = i.get_yticks().tolist()
        i.set_yticks(i.get_yticks())
        i.set_yticklabels(["{:3.2%}".format(x) for x in ticks_loc])
        i.grid(linestyle=":")
        j = j + 1

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_table(
    returns,
    w,
    MAR=0,
    alpha=0.05,
    height=9,
    width=12,
    t_factor=252,
    ini_days=1,
    days_per_year=252,
    ax=None,
):
    r"""
    Create a table with information about risk measures and risk adjusted
    return ratios.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    w : DataFrame
        Portfolio weights.
    MAR: float, optional
        Minimum acceptable return.
    alpha: float, optional
        Significance level for VaR, CVaR, EVaR, DaR and CDaR.
    height : float, optional
        Height of the image in inches. The default is 9.
    width : float, optional
        Width of the image in inches. The default is 12.
    t_factor : float, optional
        Factor used to annualize expected return and expected risks for
        risk measures based on returns (not drawdowns). The default is 252.
        
        .. math::
            
            \begin{align}
            \text{Annualized Return} & = \text{Return} \, \times \, \text{t_factor} \\
            \text{Annualized Risk} & = \text{Risk} \, \times \, \sqrt{\text{t_factor}}
            \end{align}
        
    ini_days : float, optional
        If provided, it is the number of days of compounding for first return.
        It is used to calculate Compound Annual Growth Rate (CAGR). This value
        depend on assumptions used in t_factor, for example if data is monthly
        you can use 21 (252 days per year) or 30 (360 days per year). The
        default is 1 for daily returns.
    days_per_year: float, optional
        Days per year assumption. It is used to calculate Compound Annual
        Growth Rate (CAGR). Default value is 252 trading days per year.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_table(returns=Y, w=w1, MAR=0, alpha=0.05, ax=None)

    .. image:: images/Port_Table.png


    """
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if not isinstance(w, pd.DataFrame):
        raise ValueError("w must be a DataFrame")

    if returns.shape[1] != w.shape[0]:
        a1 = str(returns.shape)
        a2 = str(w.shape)
        raise ValueError("shapes " + a1 + " and " + a2 + " not aligned")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    mu = returns.mean()
    cov = returns.cov()
    days = (returns.index[-1] - returns.index[0]).days + ini_days

    X = returns @ w
    X = X.to_numpy().ravel()

    rowLabels = [
        "Profitability and Other Inputs",
        "Mean Return (1)",
        "Compound Annual Growth Rate (CAGR)",
        "Minimum Acceptable Return (MAR) (1)",
        "Significance Level",
        "",
        "Risk Measures based on Returns",
        "Standard Deviation (2)",
        "Mean Absolute Deviation (MAD) (2)",
        "Semi Standard Deviation (2)",
        "First Lower Partial Moment (FLPM) (2)",
        "Second Lower Partial Moment (SLPM) (2)",
        "Value at Risk (VaR) (2)",
        "Conditional Value at Risk (CVaR) (2)",
        "Entropic Value at Risk (EVaR) (2)",
        "Worst Realization (2)",
        "Skewness",
        "Kurtosis",
        "",
        "Risk Measures based on Drawdowns (3)",
        "Ulcer Index (UCI)",
        "Average Drawdown (ADD)",
        "Drawdown at Risk (DaR)",
        "Conditional Drawdown at Risk (CDaR)",
        "Entropic Drawdown at Risk (EDaR)",
        "Max Drawdown (MDD)",
        "(1) Annualized, multiplied by " + str(t_factor),
        "(2) Annualized, multiplied by √" + str(t_factor),
        "(3) Based on uncompounded cumulated returns",
    ]

    indicators = [
        "",
        (mu @ w).to_numpy().item() * t_factor,
        np.power(np.prod(1 + X), days_per_year / days) - 1,
        MAR,
        alpha,
        "",
        "",
        np.sqrt(w.T @ cov @ w).to_numpy().item() * t_factor**0.5,
        rk.MAD(X) * t_factor**0.5,
        rk.SemiDeviation(X) * t_factor**0.5,
        rk.LPM(X, MAR=MAR, p=1) * t_factor**0.5,
        rk.LPM(X, MAR=MAR, p=2) * t_factor**0.5,
        rk.VaR_Hist(X, alpha=alpha) * t_factor**0.5,
        rk.CVaR_Hist(X, alpha=alpha) * t_factor**0.5,
        rk.EVaR_Hist(X, alpha=alpha)[0] * t_factor**0.5,
        rk.WR(X) * t_factor**0.5,
        st.skew(X, bias=False),
        st.kurtosis(X, bias=False),
        "",
        "",
        rk.UCI_Abs(X),
        rk.ADD_Abs(X),
        rk.DaR_Abs(X),
        rk.CDaR_Abs(X, alpha=alpha),
        rk.EDaR_Abs(X, alpha=alpha)[0],
        rk.MDD_Abs(X),
        "",
        "",
        "",
    ]

    ratios = []
    for i in range(len(indicators)):
        if i < 6 or indicators[i] == "" or rowLabels[i] in ["Skewness", "Kurtosis"]:
            ratios.append("")
        else:
            if indicators[i] == 0:
                ratios.append("")
            else:
                ratio = (indicators[1] - MAR) / indicators[i]
                ratios.append(ratio)

    for i in range(len(indicators)):
        if indicators[i] != "":
            if rowLabels[i] in ["Skewness", "Kurtosis"]:
                indicators[i] = "{:.5f}".format(indicators[i])
            else:
                indicators[i] = "{:.4%}".format(indicators[i])
        if ratios[i] != "":
            ratios[i] = "{:.6f}".format(ratios[i])

    data = pd.DataFrame({"A": rowLabels, "B": indicators, "C": ratios}).to_numpy()

    ax.set_axis_off()
    ax.axis("tight")
    ax.axis("off")

    colLabels = ["", "Values", "(Return - MAR)/Risk"]
    colWidths = [0.45, 0.275, 0.275]
    rowHeight = 0.07

    table = ax.table(
        cellText=data,
        colLabels=colLabels,
        colWidths=colWidths,
        cellLoc="center",
        loc="upper left",
        bbox=[-0.03, 0, 1, 1],
    )

    table.auto_set_font_size(False)

    cellDict = table.get_celld()
    k = 1

    rowHeight = 1 / len(rowLabels)
    ncols = len(colLabels)
    nrows = len(rowLabels)

    for i in range(0, ncols):
        cellDict[(0, i)].set_text_props(weight="bold", color="white", size="x-large")
        cellDict[(0, i)].set_facecolor("darkblue")
        cellDict[(0, i)].set_edgecolor("white")
        cellDict[(0, i)].set_height(rowHeight)
        for j in range(1, nrows + 1):
            cellDict[(j, 0)].set_text_props(
                weight="bold", color="black", size="x-large", ha="left"
            )
            cellDict[(j, i)].set_text_props(color="black", size="x-large")
            cellDict[(j, 0)].set_edgecolor("white")
            cellDict[(j, i)].set_edgecolor("white")
            if k % 2 != 0:
                cellDict[(j, 0)].set_facecolor("whitesmoke")
                cellDict[(j, i)].set_facecolor("whitesmoke")
            if j in [6, 19]:
                cellDict[(j, 0)].set_facecolor("white")
                cellDict[(j, i)].set_facecolor("white")
            if j in [1, 7, 20]:
                cellDict[(j, 0)].set_text_props(color="white")
                cellDict[(j, 0)].set_facecolor("orange")
                cellDict[(j, i)].set_facecolor("orange")
                k = 1
            k += 1

            cellDict[(j, i)].set_height(rowHeight)

    for i in range(0, ncols):
        for j in range(nrows - 2, nrows + 1):
            cellDict[(j, i)].set_text_props(
                weight="normal", color="black", size="large"
            )
            cellDict[(j, i)].set_facecolor("white")

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_clusters(
    returns,
    custom_cov=None,
    codependence="pearson",
    linkage="ward",
    k=None,
    max_k=10,
    bins_info="KN",
    alpha_tail=0.05,
    leaf_order=True,
    dendrogram=True,
    cmap="viridis",
    linecolor="fuchsia",
    title="",
    height=12,
    width=12,
    ax=None,
):
    r"""
    Create a clustermap plot based on the selected codependence measure.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    custom_cov : DataFrame or None, optional
        Custom covariance matrix, used when codependence parameter has value
        'custom_cov'. The default is None.
    codependence : str, can be {'pearson', 'spearman', 'abs_pearson', 'abs_spearman', 'distance', 'mutual_info', 'tail' or 'custom_cov'}
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Posible values are:

        - 'pearson': pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho_{i,j})}`.
        - 'spearman': spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho_{i,j})}`.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'distance': distance correlation matrix. Distance formula :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula :math:`D_{i,j} = -\log{\lambda_{i,j}}`.
        - 'custom_cov': use custom correlation matrix based on the custom_cov parameter. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.

    linkage : string, optional
        Linkage method of hierarchical clustering, see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`_ for more details.
        The default is 'ward'. Posible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'DBHT': Direct Bubble Hierarchical Tree.

    k : int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k : int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: int or str
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Posible values are:

        - 'KN': Knuth's choice method. See more in `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`_.
        - 'FD': Freedman–Diaconis' choice method. See more in `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`_.
        - 'SC': Scotts' choice method. See more in `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`_.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.
        - int: integer value choice by user.

    alpha_tail : float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order : bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    dendrogram : bool, optional
        Indicates if the plot has or not a dendrogram. The default is True.
    cmap : str or cmap, optional
        Colormap used to plot the pcolormesh plot. The default is 'viridis'.
    linecolor : str, optional
        Color used to identify the clusters in the pcolormesh plot.
        The default is fuchsia'.
    title : str, optional
        Title of the chart. The default is "".
    height : float, optional
        Height of the image in inches. The default is 12.
    width : float, optional
        Width of the image in inches. The default is 12.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_clusters(returns=Y, correlation='spearman',
                              linkage='ward', k=None, max_k=10,
                              leaf_order=True, dendrogram=True, ax=None)

    .. image:: images/Assets_Clusters.png


    """

    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if ax is None:
        fig = plt.gcf()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()
        ax.grid(False)
        ax.axis("off")

    labels = np.array(returns.columns.tolist())

    vmin, vmax = 0, 1
    # Calculating codependence matrix and distance metric
    if codependence in {"pearson", "spearman"}:
        codep = returns.corr(method=codependence)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))
        vmin, vmax = -1, 1
    elif codependence in {"abs_pearson", "abs_spearman"}:
        codep = np.abs(returns.corr(method=codependence[4:]))
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"distance"}:
        codep = af.dcorr_matrix(returns).astype(float)
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"mutual_info"}:
        codep = af.mutual_info_matrix(returns, bins_info).astype(float)
        dist = af.var_info_matrix(returns, bins_info).astype(float)
    elif codependence in {"tail"}:
        codep = af.ltdi_matrix(returns, alpha_tail).astype(float)
        dist = -np.log(codep)
    elif codependence in {"custom_cov"}:
        codep = af.cov2corr(custom_cov).astype(float)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))

    # Hierarchcial clustering
    dist = dist.to_numpy()
    dist = pd.DataFrame(dist, columns=codep.columns, index=codep.index)
    dim = len(dist)
    if linkage == "DBHT":
        # different choices for D, S give different outputs!
        D = dist.to_numpy()  # dissimilatity matrix
        if codependence in {"pearson", "spearman", "custom_cov"}:
            S = (1 - dist**2).to_numpy()
        else:
            S = codep.to_numpy()  # similarity matrix
        (_, _, _, _, _, clustering) = db.DBHTs(
            D, S, leaf_order=leaf_order
        )  # DBHT clustering
    else:
        p_dist = squareform(dist, checks=False)
        clustering = hr.linkage(p_dist, method=linkage, optimal_ordering=leaf_order)

    # Ordering clusterings
    permutation = hr.leaves_list(clustering)
    permutation = permutation.tolist()
    ordered_codep = codep.to_numpy()[permutation, :][:, permutation]

    # optimal number of clusters
    if k is None:
        k = af.two_diff_gap_stat(codep, dist, clustering, max_k)

    clustering_inds = hr.fcluster(clustering, k, criterion="maxclust")
    clusters = {i: [] for i in range(min(clustering_inds), max(clustering_inds) + 1)}
    for i, v in enumerate(clustering_inds):
        clusters[v].append(i)

    ax = fig.add_axes([0.3, 0.1, 0.6, 0.6])

    im = ax.pcolormesh(ordered_codep, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(np.arange(codep.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(codep.shape[0]) + 0.5, minor=False)
    ax.set_xticklabels(labels[permutation], rotation=90, ha="center")
    ax.set_yticklabels(labels[permutation], va="center")
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()

    if linecolor is not None:
        for cluster_id, cluster in clusters.items():

            amin = permutation.index(cluster[0])
            xmin, xmax = amin, amin + len(cluster)
            ymin, ymax = amin, amin + len(cluster)

            for i in cluster:
                a = permutation.index(i)
                if a < amin:
                    xmin, xmax = a, a + len(cluster)
                    ymin, ymax = a, a + len(cluster)
                    amin = a

            ax.axvline(
                x=xmin, ymin=ymin / dim, ymax=(ymax) / dim, linewidth=4, color=linecolor
            )
            ax.axvline(
                x=xmax, ymin=ymin / dim, ymax=(ymax) / dim, linewidth=4, color=linecolor
            )
            ax.axhline(
                y=ymin, xmin=xmin / dim, xmax=(xmax) / dim, linewidth=4, color=linecolor
            )
            ax.axhline(
                y=ymax, xmin=xmin / dim, xmax=(xmax) / dim, linewidth=4, color=linecolor
            )

    axcolor = fig.add_axes([1.02, 0.1, 0.02, 0.6])
    plt.colorbar(im, cax=axcolor)

    if dendrogram == True:

        ax1 = fig.add_axes([0.3, 0.71, 0.6, 0.2])

        root, nodes = hr.to_tree(clustering, rd=True)
        nodes = [i.dist for i in nodes]
        nodes.sort()
        nodes = nodes[::-1][: k - 1]
        color_threshold = np.min(nodes)

        colors = af.color_list(k)

        hr.set_link_color_palette(colors)
        hr.dendrogram(
            clustering,
            color_threshold=color_threshold,
            above_threshold_color="grey",
            ax=ax1,
        )
        hr.set_link_color_palette(None)
        ax1.xaxis.set_major_locator(mticker.FixedLocator(np.arange(codep.shape[0])))
        ax1.set_xticklabels(labels[permutation], rotation=90, ha="center")

        i = 0
        for coll in ax1.collections[:-1]:  # the last collection is the ungrouped level
            xmin, xmax = np.inf, -np.inf
            ymax = -np.inf
            for p in coll.get_paths():
                (x0, _), (x1, y1) = p.get_extents().get_points()
                xmin = min(xmin, x0)
                xmax = max(xmax, x1)
                ymax = max(ymax, y1)
            rec = plt.Rectangle(
                (xmin - 4, 0),
                xmax - xmin + 8,
                ymax * 1.05,
                facecolor=colors[i],  # coll.get_color()[0],
                alpha=0.2,
                edgecolor="none",
            )
            ax1.add_patch(rec)
            i += 1

        ax1.set_xticks([])
        ax1.set_yticks([])

        for i in {"right", "left", "top", "bottom"}:
            side = ax1.spines[i]
            side.set_visible(False)

        ax2 = fig.add_axes([0.09, 0.1, 0.2, 0.6])

        hr.set_link_color_palette(colors)
        hr.dendrogram(
            clustering,
            color_threshold=color_threshold,
            above_threshold_color="grey",
            orientation="left",
            ax=ax2,
        )
        hr.set_link_color_palette(None)

        ax2.xaxis.set_major_locator(mticker.FixedLocator(np.arange(codep.shape[0])))
        ax2.set_xticklabels(labels[permutation], rotation=90, ha="center")

        i = 0
        for coll in ax2.collections[:-1]:  # the last collection is the ungrouped level
            ymin, ymax = np.inf, -np.inf
            xmax = -np.inf
            for p in coll.get_paths():
                (_, y0), (x1, y1) = p.get_extents().get_points()
                ymin = min(ymin, y0)
                ymax = max(ymax, y1)
                xmax = max(xmax, x1)
            rec = plt.Rectangle(
                (0, ymin - 4),
                xmax * 1.05,
                ymax - ymin + 8,
                facecolor=colors[i],  # coll.get_color()[0],
                alpha=0.2,
                edgecolor="none",
            )
            ax2.add_patch(rec)
            i += 1

        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.set_yticklabels([])
        for i in {"right", "left", "top", "bottom"}:
            side = ax2.spines[i]
            side.set_visible(False)

    if title == "":
        title = (
            "Assets Clustermap ("
            + codependence.capitalize()
            + " & "
            + linkage
            + " linkage)"
        )

    if dendrogram == True:
        ax1.set_title(title)
    elif dendrogram == False:
        ax.set_title(title)

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_dendrogram(
    returns,
    custom_cov=None,
    codependence="pearson",
    linkage="ward",
    k=None,
    max_k=10,
    bins_info="KN",
    alpha_tail=0.05,
    leaf_order=True,
    title="",
    height=5,
    width=12,
    ax=None,
):
    r"""
    Create a dendrogram based on the selected codependence measure.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    custom_cov : DataFrame or None, optional
        Custom covariance matrix, used when codependence parameter has value
        'custom_cov'. The default is None.
    codependence : str, can be {'pearson', 'spearman', 'abs_pearson', 'abs_spearman', 'distance', 'mutual_info', 'tail' or 'custom_cov'}
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Posible values are:

        - 'pearson': pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho_{i,j})}`.
        - 'spearman': spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho_{i,j})}`.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'distance': distance correlation matrix. Distance formula :math:`D_{i,j} = \sqrt{(1-|\rho_{i,j}|)}`.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula :math:`D_{i,j} = -\log{\lambda_{i,j}}`.
        - 'custom_cov': use custom correlation matrix based on the custom_cov parameter. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.

    linkage : string, optional
        Linkage method of hierarchical clustering, see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`_ for more details.
        The default is 'ward'. Posible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'DBHT': Direct Bubble Hierarchical Tree.

    k : int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k : int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: int or str
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Posible values are:

        - 'KN': Knuth's choice method. See more in `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`_.
        - 'FD': Freedman–Diaconis' choice method. See more in `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`_.
        - 'SC': Scotts' choice method. See more in `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`_.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.
        - int: integer value choice by user.

    alpha_tail : float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order : bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    title : str, optional
        Title of the chart. The default is "".
    height : float, optional
        Height of the image in inches. The default is 5.
    width : float, optional
        Width of the image in inches. The default is 12.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_dendrogram(returns=Y, correlation='spearman',
                                linkage='ward', k=None, max_k=10,
                                leaf_order=True, ax=None)

    .. image:: images/Assets_Dendrogram.png


    """
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    labels = np.array(returns.columns.tolist())

    # Calculating codependence matrix and distance metric
    if codependence in {"pearson", "spearman"}:
        codep = returns.corr(method=codependence)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))
    elif codependence in {"abs_pearson", "abs_spearman"}:
        codep = np.abs(returns.corr(method=codependence[4:]))
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"distance"}:
        codep = af.dcorr_matrix(returns).astype(float)
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"mutual_info"}:
        codep = af.mutual_info_matrix(returns, bins_info).astype(float)
        dist = af.var_info_matrix(returns, bins_info).astype(float)
    elif codependence in {"tail"}:
        codep = af.ltdi_matrix(returns, alpha_tail).astype(float)
        dist = -np.log(codep)
    elif codependence in {"custom_cov"}:
        codep = af.cov2corr(custom_cov).astype(float)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))

    # Hierarchcial clustering
    dist = dist.to_numpy()
    dist = pd.DataFrame(dist, columns=codep.columns, index=codep.index)
    if linkage == "DBHT":
        # different choices for D, S give different outputs!
        D = dist.to_numpy()  # dissimilatity matrix
        if codependence in {"pearson", "spearman", "custom_cov"}:
            S = (1 - dist**2).to_numpy()
        else:
            S = codep.copy().to_numpy()  # similarity matrix
        (_, _, _, _, _, clustering) = db.DBHTs(
            D, S, leaf_order=leaf_order
        )  # DBHT clustering
    else:
        p_dist = squareform(dist, checks=False)
        clustering = hr.linkage(p_dist, method=linkage, optimal_ordering=leaf_order)

    # Ordering clusterings
    permutation = hr.leaves_list(clustering)
    permutation = permutation.tolist()

    # optimal number of clusters
    if k is None:
        k = af.two_diff_gap_stat(codep, dist, clustering, max_k)

    root, nodes = hr.to_tree(clustering, rd=True)
    nodes = [i.dist for i in nodes]
    nodes.sort()
    nodes = nodes[::-1][: k - 1]
    color_threshold = np.min(nodes)

    colors = af.color_list(k)  # color list

    hr.set_link_color_palette(colors)
    hr.dendrogram(
        clustering, color_threshold=color_threshold, above_threshold_color="grey", ax=ax
    )
    hr.set_link_color_palette(None)

    ax.xaxis.set_major_locator(mticker.FixedLocator(np.arange(codep.shape[0])))
    ax.set_xticklabels(labels[permutation], rotation=90, ha="center")

    i = 0
    for coll in ax.collections[:-1]:  # the last collection is the ungrouped level
        xmin, xmax = np.inf, -np.inf
        ymax = -np.inf
        for p in coll.get_paths():
            (x0, _), (x1, y1) = p.get_extents().get_points()
            xmin = min(xmin, x0)
            xmax = max(xmax, x1)
            ymax = max(ymax, y1)
        rec = plt.Rectangle(
            (xmin - 4, 0),
            xmax - xmin + 8,
            ymax * 1.05,
            facecolor=colors[i],  # coll.get_color()[0],
            alpha=0.2,
            edgecolor="none",
        )
        ax.add_patch(rec)
        i += 1

    ax.set_yticks([])
    ax.set_yticklabels([])
    for i in {"right", "left", "top", "bottom"}:
        side = ax.spines[i]
        side.set_visible(False)

    if title == "":
        title = (
            "Assets Dendrogram ("
            + codependence.capitalize()
            + " & "
            + linkage
            + " linkage)"
        )

    ax.set_title(title)

    try:
        fig.tight_layout()
    except:
        pass

    return ax


def plot_network(
    returns,
    custom_cov=None,
    codependence="pearson",
    linkage="ward",
    k=None,
    max_k=10,
    bins_info="KN",
    alpha_tail=0.05,
    leaf_order=True,
    kind="spring",
    seed=0,
    node_labels=True,
    node_size=1400,
    node_alpha=0.7,
    font_size=10,
    title="",
    height=8,
    width=10,
    ax=None,
):
    r"""
    Create a network plot. The Planar Maximally Filtered Graph (PMFG) for DBHT
    linkage and Minimum Spanning Tree (MST) for other linkage methods.

    Parameters
    ----------
    returns : DataFrame
        Assets returns.
    custom_cov : DataFrame or None, optional
        Custom covariance matrix, used when codependence parameter has value
        'custom_cov'. The default is None.
    codependence : str, can be {'pearson', 'spearman', 'abs_pearson', 'abs_spearman', 'distance', 'mutual_info', 'tail' or 'custom_cov'}
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Posible values are:

        - 'pearson': pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.
        - 'spearman': spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}`.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}`.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}`.
        - 'distance': distance correlation matrix. Distance formula :math:`D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}`.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula :math:`D_{i,j} = -\log{\lambda_{i,j}}`.
        - 'custom_cov': use custom correlation matrix based on the custom_cov parameter. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.

    linkage : string, optional
        Linkage method of hierarchical clustering, see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`_ for more details.
        The default is 'ward'. Posible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'DBHT': Direct Bubble Hierarchical Tree.

    k : int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k : int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: int or str
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Posible values are:

        - 'KN': Knuth's choice method. See more in `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`_.
        - 'FD': Freedman–Diaconis' choice method. See more in `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`_.
        - 'SC': Scotts' choice method. See more in `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`_.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.
        - int: integer value choice by user.

    alpha_tail : float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order : bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    kind : str, optional
        Kind of networkx layout. The default value is 'spring'. Posible values
        are:

        - 'spring': networkx spring_layout.
        - 'planar'. networkx planar_layout.
        - 'circular'. networkx circular_layout.
        - 'kamada'. networkx kamada_kawai_layout. Only available for positive codependence metrics. Not pearson or spearman except when linkage is DBHT.

    seed : int, optional
        Seed for networkx spring layout. The default value is 0.
    node_labels : bool, optional
        Specify if node lables are visible. The default value is True.
    node_size : float, optional
        Size of the nodes. The default value is 1600.
    node_alpha : float, optional
        Alpha parameter or transparency of nodes. The default value is 0.7.
    font_size : float, optional
        Font size of node labels. The default value is 12.
    title : str, optional
        Title of the chart. The default is "".
    height : float, optional
        Height of the image in inches. The default is 5.
    width : float, optional
        Width of the image in inches. The default is 12.
    ax : matplotlib axis, optional
        If provided, plot on this axis. The default is None.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    ax : matplotlib axis
        Returns the Axes object with the plot for further tweaking.

    Example
    -------
    ::

        ax = rp.plot_network(returns=Y, codependence="pearson",
                             linkage="ward", k=None, max_k=10,
                             alpha_tail=0.05, leaf_order=True,
                             kind='spring', ax=None)


    .. image:: images/Assets_Network.png


    """
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    labels = np.array(returns.columns.tolist())

    # Calculating codependence matrix and distance metric
    if codependence in {"pearson", "spearman"}:
        codep = returns.corr(method=codependence)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))
    elif codependence in {"abs_pearson", "abs_spearman"}:
        codep = np.abs(returns.corr(method=codependence[4:]))
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"distance"}:
        codep = af.dcorr_matrix(returns).astype(float)
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"mutual_info"}:
        codep = af.mutual_info_matrix(returns, bins_info).astype(float)
        dist = af.var_info_matrix(returns, bins_info).astype(float)
    elif codependence in {"tail"}:
        codep = af.ltdi_matrix(returns, alpha_tail).astype(float)
        dist = -np.log(codep)
    elif codependence in {"custom_cov"}:
        codep = af.cov2corr(custom_cov).astype(float)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))

    # Hierarchcial clustering
    dist = dist.to_numpy()
    dist = pd.DataFrame(dist, columns=codep.columns, index=codep.index)
    if linkage == "DBHT":
        # different choices for D, S give different outputs!
        D = dist.to_numpy()  # dissimilatity matrix
        if codependence in {"pearson", "spearman", "custom_cov"}:
            S = (1 - dist**2).to_numpy()
        else:
            S = codep.copy().to_numpy()  # similarity matrix
        (_, Rpm, _, _, _, clustering) = db.DBHTs(
            D, S, leaf_order=leaf_order
        )  # DBHT clustering
        MAdj = pd.DataFrame(Rpm, index=labels, columns=labels)
        G = nx.from_pandas_adjacency(MAdj)
    else:
        p_dist = squareform(dist, checks=False)
        clustering = hr.linkage(p_dist, method=linkage, optimal_ordering=leaf_order)
        T = nx.from_pandas_adjacency(codep)  # create a graph G from a numpy matrix
        G = nx.minimum_spanning_tree(T)

    # optimal number of clusters
    if k is None:
        k = af.two_diff_gap_stat(codep, dist, clustering, max_k)

    clustering_inds = hr.fcluster(clustering, k, criterion="maxclust")
    clusters = {i: [] for i in range(min(clustering_inds), max(clustering_inds) + 1)}
    for i, v in enumerate(clustering_inds):
        clusters[v].append(labels[i])

    # Layout options
    node_options = {
        "node_size": node_size,
        "alpha": node_alpha,
    }
    font_options = {
        "font_size": font_size,
        "font_color": "k",
    }

    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}

    if kind == "spring":
        pos = nx.spring_layout(G, seed=seed)
    elif kind == "planar":
        pos = nx.planar_layout(G)
    elif kind == "circular":
        pos = nx.circular_layout(G)
    elif kind == "kamada":
        if codependence in {"pearson", "spearman"} and linkage != "DBHT":
            raise NameError(
                "kamada layout only works with positive codependence measures except when linkage is DBHT."
            )
        pos = nx.kamada_kawai_layout(G)

    # Plotting
    nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color="grey")

    if node_labels == True:
        nx.draw_networkx_labels(G, pos=pos, ax=ax, bbox=label_options, **font_options)

    colors = af.color_list(k)

    for i, color in zip(clusters.keys(), colors):
        nx.draw_networkx_nodes(
            G, pos=pos, nodelist=clusters[i], node_color=color, ax=ax, **node_options
        )

    ax.set_yticks([])
    ax.set_yticklabels([])
    for i in {"right", "left", "top", "bottom"}:
        side = ax.spines[i]
        side.set_visible(False)

    if title == "":
        if linkage == "DBHT":
            title = (
                "Planar Maximally Filtered Graph ("
                + codependence.capitalize()
                + ", "
                + linkage
                + " linkage & "
                + kind
                + " layout)"
            )
        else:
            title = (
                "Minimun Spanning Tree ("
                + codependence.capitalize()
                + ", "
                + linkage
                + " linkage & "
                + kind
                + " layout)"
            )

    ax.set_title(title)

    try:
        fig.tight_layout()
    except:
        pass

    return ax
