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
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.rich_config import console

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

objectives_choices = {
    "minrisk": "MinRisk",
    "sharpe": "Sharpe",
    "utility": "Utility",
    "maxret": "MaxRet",
    "erc": "ERC",
}

risk_names = {
    "mv": "volatility",
    "mad": "mean absolute deviation",
    "gmd": "gini mean difference",
    "msv": "semi standard deviation",
    "var": "value at risk (VaR)",
    "cvar": "conditional value at risk (CVaR)",
    "tg": "tail gini",
    "evar": "entropic value at risk (EVaR)",
    "rg": "range",
    "cvrg": "CVaR range",
    "tgrg": "tail gini range",
    "wr": "worst realization",
    "flpm": "first lower partial moment",
    "slpm": "second lower partial moment",
    "mdd": "maximum drawdown uncompounded",
    "add": "average drawdown uncompounded",
    "dar": "drawdown at risk (DaR) uncompounded",
    "cdar": "conditional drawdown at risk (CDaR) uncompounded",
    "edar": "entropic drawdown at risk (EDaR) uncompounded",
    "uci": "ulcer index uncompounded",
    "mdd_rel": "maximum drawdown compounded",
    "add_rel": "average drawdown compounded",
    "dar_rel": "drawdown at risk (DaR) compounded",
    "cdar_rel": "conditional drawdown at risk (CDaR) compounded",
    "edar_rel": "entropic drawdown at risk (EDaR) compounded",
    "uci_rel": "ulcer index compounded",
}

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

dict_conversion = {"period": "historic_period", "start": "start_period"}


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

    n_portfolios: int = 100
    if n_portfolios in kwargs:
        n_portfolios = kwargs["n_portfolios"]

    freq: str = "D"
    if "freq" in kwargs:
        freq = kwargs["freq"]

    risk_measure: str = "MV"
    if "risk_measure" in kwargs:
        risk_measure = kwargs["risk_measure"]

    risk_free_rate: float = 0.0
    if "risk_free_rate" in kwargs:
        risk_free_rate = kwargs["risk_free_rate"]

    alpha: float = 0.05
    if "alpha" in kwargs:
        alpha = kwargs["alpha"]

    # Pop chart args
    tangency: bool = False
    if "tangency" in kwargs:
        tangency = kwargs.pop("tangency")

    plot_tickers: bool = False
    if "plot_tickers" in kwargs:
        plot_tickers = kwargs.pop("plot_tickers")

    external_axes: Optional[List[plt.Axes]] = None
    if "external_axes" in kwargs:
        external_axes = kwargs.pop("external_axes")

    frontier, mu, cov, stock_returns, weights, X1, Y1, port = po_model.get_ef(
        symbols,
        engine,
        **kwargs,
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
