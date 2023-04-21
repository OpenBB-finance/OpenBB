"""Optimization View"""
__docformat__ = "numpy"

# pylint: disable=R0913, R0914, C0302, too-many-branches, too-many-statements, line-too-long
# flake8: noqa: E501

# IMPORTS STANDARD
import logging
import math
import warnings
from datetime import date
from typing import Any, Dict, List, Optional

# IMPORTS THIRD-PARTY
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import riskfolio as rp
from dateutil.relativedelta import FR, relativedelta
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


# IMPORTS INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale, print_rich_table
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_helper,
    optimizer_model,
)
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
def d_period(interval: str = "1y", start_date: str = "", end_date: str = ""):
    """
    Builds a date range string

    Parameters
    ----------
    interval : str
        interval starting today
    start_date: str
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    """
    extra_choices = {
        "ytd": "[Year-to-Date]",
        "max": "[All-time]",
    }

    if start_date == "":
        if interval in extra_choices:
            p = extra_choices[interval]
        else:
            if interval[-1] == "d":
                p = "[" + interval[:-1] + " Days]"
            elif interval[-1] == "w":
                p = "[" + interval[:-1] + " Weeks]"
            elif interval[-1] == "o":
                p = "[" + interval[:-2] + " Months]"
            elif interval[-1] == "y":
                p = "[" + interval[:-1] + " Years]"
        if p[1:3] == "1 ":
            p = p.replace("s", "")
    else:
        if end_date == "":
            end_ = date.today()
            if end_.weekday() >= 5:
                end_ = end_ + relativedelta(weekday=FR(-1))
            end_date = end_.strftime("%Y-%m-%d")
        p = "[From " + start_date + " to " + end_date + "]"

    return p


@log_start_end(log=logger)
def portfolio_performance(
    weights: dict,
    data: pd.DataFrame,
    freq: str = "D",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    a_sim: float = 100,
    beta: Optional[float] = None,
    b_sim: Optional[float] = None,
):
    """
    Prints portfolio performance indicators

    Parameters
    ----------
    weights: dict
        Portfolio weights
    data: pd.DataFrame
        Stock returns dataframe
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    risk_measure : str, optional
        The risk measure used. The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate : float, optional
        risk free rate.
    alpha : float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of
        losses. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default
        is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it
        duplicates alpha value. The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None
        it duplicates a_sim value. The default is None.
    """

    try:
        freq = freq.upper()
        weights = pd.Series(weights).to_frame()
        returns = data @ weights
        mu = returns.mean().item() * time_factor[freq]
        sigma = returns.std().item() * time_factor[freq] ** 0.5
        sharpe = (mu - risk_free_rate) / sigma

        factor_1 = str(int(time_factor[freq])) + ") "
        factor_2 = "√" + factor_1

        print("\nAnnual (by " + factor_1 + f"expected return: {100 * mu:.2f}%")
        print("Annual (by " + factor_2 + f"volatility: {100 * sigma:.2f}%")
        print(f"Sharpe ratio: {sharpe:.4f}")

        if risk_measure != "MV":
            risk = rp.Sharpe_Risk(
                weights,
                cov=data.cov(),
                returns=data,
                rm=risk_measure,
                rf=risk_free_rate,
                alpha=alpha,
                a_sim=a_sim,
                beta=beta,
                b_sim=b_sim,
            )

            drawdowns = [
                "MDD",
                "ADD",
                "DaR",
                "CDaR",
                "EDaR",
                "UCI",
                "MDD_Rel",
                "ADD_Rel",
                "DaR_Rel",
                "CDaR_Rel",
                "EDaR_Rel",
                "UCI_Rel",
            ]

            if risk_measure in drawdowns:
                sharpe_2 = (mu - risk_free_rate) / risk
                print(
                    risk_names[risk_measure.lower()].capitalize()
                    + " : "
                    + f"{100 * risk:.2f}%"
                )
            else:
                risk = risk * time_factor[freq] ** 0.5
                sharpe_2 = (mu - risk_free_rate) / risk
                print(
                    "Annual (by "
                    + factor_2
                    + risk_names[risk_measure.lower()]
                    + " : "
                    + f"{100 * risk:.2f}%"
                )

            print(
                "Return / "
                + risk_names[risk_measure.lower()]
                + f" ratio: {sharpe_2:.4f}"
            )
    except Exception as _:
        console.print(
            "[red]\nFailed to calculate portfolio performance indicators.[/red]"
        )


@log_start_end(log=logger)
def display_weights(weights: dict, market_neutral: bool = False):
    """
    Prints weights in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    market_neutral : bool
        Flag indicating shorting allowed (negative weights)
    """

    df = optimizer_helper.dict_to_df(weights)

    if df.empty:
        return

    if math.isclose(df.sum()["value"], 1, rel_tol=0.5):
        df["value"] = (df["value"] * 100).apply(lambda s: f"{s:.2f}") + " %"
        df["value"] = (
            df["value"]
            .astype(str)
            .apply(lambda s: " " * (8 - len(s)) + s if len(s) < 8 else "" + s)
        )
    else:
        df["value"] = (df["value"] * 100).apply(lambda s: f"{s:.0f}") + " $"
        df["value"] = (
            df["value"]
            .astype(str)
            .apply(lambda s: " " * (16 - len(s)) + s if len(s) < 16 else "" + s)
        )

    if market_neutral:
        tot_value = df["value"].abs().mean()
        header = "Value ($)" if tot_value > 1.01 else "Value (%)"
        print_rich_table(df, headers=[header], show_index=True, title="Weights")
    else:
        print_rich_table(df, headers=["Value"], show_index=True, title="Weights")


@log_start_end(log=logger)
def display_weights_sa(weights: dict, weights_sa: dict):
    """
    Prints weights in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    weights_sa: dict
        weights of sensitivity analysis to display.  Keys are stocks.
        Values are either weights or values
    """
    if not weights or not weights_sa:
        return
    weight_df = pd.DataFrame.from_dict(
        data=weights, orient="index", columns=["value"], dtype=float
    )
    weight_sa_df = pd.DataFrame.from_dict(
        data=weights_sa, orient="index", columns=["value s.a."], dtype=float
    )
    weight_df = weight_df.join(weight_sa_df, how="inner")
    weight_df["value vs value s.a."] = weight_df["value"] - weight_df["value s.a."]

    weight_df["value"] = (weight_df["value"] * 100).apply(lambda s: f"{s:.2f}") + " %"
    weight_df["value"] = (
        weight_df["value"]
        .astype(str)
        .apply(lambda s: " " * (8 - len(s)) + s if len(s) < 8 else "" + s)
    )
    weight_df["value s.a."] = (weight_df["value s.a."] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    weight_df["value s.a."] = (
        weight_df["value s.a."]
        .astype(str)
        .apply(
            lambda s: " " * (len("value s.a.") - len(s)) + s
            if len(s) < len("value s.a.")
            else "" + s
        )
    )
    weight_df["value vs value s.a."] = (weight_df["value vs value s.a."] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    weight_df["value vs value s.a."] = (
        weight_df["value vs value s.a."]
        .astype(str)
        .apply(
            lambda s: " " * (len("value vs value s.a.") - len(s)) + s
            if len(s) < len("value vs value s.a.")
            else "" + s
        )
    )

    headers = list(weight_df.columns)
    headers = [s.title() for s in headers]
    print_rich_table(
        weight_df, headers=headers, show_index=True, title="Weights Comparison"
    )


@log_start_end(log=logger)
def display_categories(
    weights: dict, categories: dict, column: str = "ASSET_CLASS", title: str = ""
):
    """
    Prints categories in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    categories: dict
        categories to display. Keys are stocks.  Values are either weights or values
    column: str
        column selected to show table
        - ASSET_CLASS
        - SECTOR
        - INDUSTRY
        - COUNTRY
    title: str
        title to display
    """

    if column == "CURRENT_INVESTED_AMOUNT":
        console.print(f"[yellow]'{column}' cannot be displayed as a category.[/yellow]")
        return

    df = optimizer_model.get_categories(weights, categories, column)

    if df.empty:
        return

    df["value"] = (df["value"] * 100).apply(lambda s: f"{s:.2f}") + " %"
    df["value"] = (
        df["value"]
        .astype(str)
        .apply(lambda s: " " * (8 - len(s)) + s if len(s) < 8 else "" + s)
    )
    df["CURRENT_WEIGHTS"] = (df["CURRENT_WEIGHTS"] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    df["CURRENT_WEIGHTS"] = (
        df["CURRENT_WEIGHTS"]
        .astype(str)
        .apply(
            lambda s: " " * (len("CURRENT_WEIGHTS") - len(s)) + s
            if len(s) < len("CURRENT_WEIGHTS")
            else "" + s
        )
    )
    df["CURRENT_INVESTED_AMOUNT"] = (
        df["CURRENT_INVESTED_AMOUNT"].apply(lambda s: f"{s:,.0f}") + " $"
    )
    df["CURRENT_INVESTED_AMOUNT"] = (
        df["CURRENT_INVESTED_AMOUNT"]
        .astype(str)
        .apply(
            lambda s: " " * (len("CURRENT_INVESTED_AMOUNT") - len(s)) + s
            if len(s) < len("CURRENT_INVESTED_AMOUNT")
            else "" + s
        )
    )

    df.reset_index(level=1, inplace=True)
    headers = [s.title() for s in list(df.columns)]
    show_index = True
    if column == "CURRENCY":
        show_index = False

    print_rich_table(df, headers=headers, show_index=show_index, title=title)


@log_start_end(log=logger)
def display_categories_sa(
    weights: dict, weights_sa: dict, categories: dict, column: str, title: str = ""
):
    """
    Prints categories in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values
    weights_sa: dict
        weights of sensitivity analysis to display.  Keys are stocks.  Values are either weights or values
    categories: dict
        categories to display. Keys are stocks.  Values are either weights or values
    column: int.
        column selected to show table
        - ASSET_CLASS
        - SECTOR
        - INDUSTRY
        - COUNTRY
    """
    if not weights or not weights_sa:
        return
    weight_df = pd.DataFrame.from_dict(
        data=weights, orient="index", columns=["value"], dtype=float
    )
    weight_sa_df = pd.DataFrame.from_dict(
        data=weights_sa, orient="index", columns=["value s.a."], dtype=float
    )
    categories_df = pd.DataFrame.from_dict(data=categories, dtype=float)

    col = list(categories_df.columns).index(column)
    categories_df = weight_df.join(categories_df.iloc[:, [col, 4, 5]], how="inner")
    categories_df = categories_df.join(weight_sa_df, how="inner")
    categories_df.set_index(column, inplace=True)
    categories_df.groupby(level=0).sum()

    table_df = pd.pivot_table(
        categories_df,
        values=["value", "value s.a.", "CURRENT_INVESTED_AMOUNT"],
        index=["CURRENCY", column],
        aggfunc=np.sum,
    )
    table_df["CURRENT_WEIGHTS"] = (
        table_df["CURRENT_INVESTED_AMOUNT"]
        .groupby(level=0)
        .transform(lambda x: x / sum(x))
    )
    table_df["value"] = (
        table_df["value"].groupby(level=0).transform(lambda x: x / sum(x))
    )
    table_df["value s.a."] = (
        table_df["value s.a."].groupby(level=0).transform(lambda x: x / sum(x))
    )
    table_df = pd.concat(
        [
            d.append(d.sum().rename((k, "TOTAL " + k)))
            for k, d in table_df.groupby(level=0)
        ]
    )
    table_df["value vs value s.a."] = table_df["value"] - table_df["value s.a."]

    table_df = table_df.iloc[:, [0, 3, 1, 2, 4]]

    table_df["value"] = (table_df["value"] * 100).apply(lambda s: f"{s:.2f}") + " %"
    table_df["value"] = (
        table_df["value"]
        .astype(str)
        .apply(lambda s: " " * (8 - len(s)) + s if len(s) < 8 else "" + s)
    )
    table_df["value s.a."] = (table_df["value s.a."] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    table_df["value s.a."] = (
        table_df["value s.a."]
        .astype(str)
        .apply(
            lambda s: " " * (len("value s.a.") - len(s)) + s
            if len(s) < len("value s.a.")
            else "" + s
        )
    )
    table_df["value vs value s.a."] = (table_df["value vs value s.a."] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    table_df["value vs value s.a."] = (
        table_df["value vs value s.a."]
        .astype(str)
        .apply(
            lambda s: " " * (len("value vs value s.a.") - len(s)) + s
            if len(s) < len("value vs value s.a.")
            else "" + s
        )
    )
    table_df["CURRENT_WEIGHTS"] = (table_df["CURRENT_WEIGHTS"] * 100).apply(
        lambda s: f"{s:.2f}"
    ) + " %"
    table_df["CURRENT_WEIGHTS"] = (
        table_df["CURRENT_WEIGHTS"]
        .astype(str)
        .apply(
            lambda s: " " * (len("CURRENT_WEIGHTS") - len(s)) + s
            if len(s) < len("CURRENT_WEIGHTS")
            else "" + s
        )
    )
    table_df["CURRENT_INVESTED_AMOUNT"] = (
        table_df["CURRENT_INVESTED_AMOUNT"].apply(lambda s: f"{s:,.0f}") + " $"
    )
    table_df["CURRENT_INVESTED_AMOUNT"] = (
        table_df["CURRENT_INVESTED_AMOUNT"]
        .astype(str)
        .apply(
            lambda s: " " * (len("CURRENT_INVESTED_AMOUNT") - len(s)) + s
            if len(s) < len("CURRENT_INVESTED_AMOUNT")
            else "" + s
        )
    )

    table_df.reset_index(inplace=True)
    table_df.set_index("CURRENCY", inplace=True)

    headers = list(table_df.columns)
    headers = [s.title() for s in headers]
    print_rich_table(table_df, headers=headers, show_index=True, title=title)


@log_start_end(log=logger)
def display_equal_weight(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure="mv",
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    value: float = 1,
    table: bool = False,
) -> Dict:
    """
    Equally weighted portfolio, where weight = 1/# of symbols
    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False.
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.
    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:
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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR.
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Equally Weighted Portfolio\n"

    weights, stock_returns = optimizer_model.get_equal_weights(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        value=value,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_property_weighting(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "mv",
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    value: float = 1,
    table: bool = False,
) -> Dict[str, float]:
    """
    Builds a portfolio weighted by selected property

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    s_property : str
        Property to get weighted portfolio of
    risk_measure: str, optional
        The risk measure used to compute indicators.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR.
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Weighted Portfolio based on Market Cap \n"

    weights, stock_returns = optimizer_model.get_property_weights(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        value=value,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_mean_risk(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "mv",
    objective: str = "sharpe",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    alpha: float = 0.05,
    target_return: float = -1,
    target_risk: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a mean risk optimal portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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

    objective: str
        Objective function of the optimization model.
        The default is 'Sharpe'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    if objective == "sharpe":
        s_title = f"{p} Maximal return/risk ratio portfolio using "
    elif objective == "minrisk":
        s_title = f"{p} Minimum risk portfolio using "
    elif objective == "maxret":
        s_title = f"{p} Maximal return portfolio using "
    elif objective == "utility":
        s_title = f"{p} Maximal risk averse utility function portfolio using "
    s_title += risk_names[risk_measure] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_mean_risk_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_choices[risk_measure],
        objective=objectives_choices[objective],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        target_return=target_return,
        target_risk=target_risk,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_max_sharpe(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    alpha: float = 0.05,
    target_return: float = -1,
    target_risk: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a maximal return/risk ratio portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """

    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Maximal return/risk ratio portfolio using "
    s_title += risk_names[risk_measure.lower()] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_max_sharpe(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_measure,
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        target_return=target_return,
        target_risk=target_risk,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_min_risk(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    alpha: float = 0.05,
    target_return: float = -1,
    target_risk: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a minimum risk portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Minimum risk portfolio using "
    s_title += risk_names[risk_measure.lower()] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_min_risk(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_measure,
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        target_return=target_return,
        target_risk=target_risk,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_max_util(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    alpha: float = 0.05,
    target_return: float = -1,
    target_risk: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a maximal risk averse utility portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Maximal risk averse utility function portfolio using "
    s_title += risk_names[risk_measure.lower()] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_max_util(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_measure,
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        target_return=target_return,
        target_risk=target_risk,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_max_ret(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    alpha: float = 0.05,
    target_return: float = -1,
    target_risk: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a maximal return portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Maximal risk averse utility function portfolio using "
    s_title += risk_names[risk_measure.lower()] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_max_ret(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_measure,
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        target_return=target_return,
        target_risk=target_risk,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=beta_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_max_div(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a maximal diversification portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Maximal diversification portfolio\n"

    weights, stock_returns = optimizer_model.get_max_diversification_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with these parameters.")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure="MV",
            risk_free_rate=0,
            # alpha=0.05,
            # a_sim=100,
            # beta=None,
            # b_sim=None,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_max_decorr(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0.0,
    table: bool = False,
) -> Dict:
    """
    Builds a maximal decorrelation portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Maximal decorrelation portfolio\n"

    weights, stock_returns = optimizer_model.get_max_decorrelation_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure="MV",
            risk_free_rate=0,
            # alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_simb_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_black_litterman(
    symbols: List[str],
    p_views: Optional[List] = None,
    q_views: Optional[List] = None,
    benchmark: Optional[Dict] = None,
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    objective: str = "Sharpe",
    risk_free_rate: float = 0,
    risk_aversion: float = 1,
    delta: Optional[float] = None,
    equilibrium: bool = True,
    optimize: bool = True,
    value: float = 1.0,
    value_short: float = 0,
    table: bool = False,
) -> Dict:
    """
    Builds a black litterman portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    p_views: List
        Matrix P of views that shows relationships among assets and returns.
        Default value to None.
    q_views: List
        Matrix Q of expected returns of views. Default value is None.
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    benchmark : Dict
        Dict of portfolio weights
    objective: str
        Objective function of the optimization model.
        The default is 'Sharpe'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_free_rate: float, optional
        Risk free rate, must be in annual frequency. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    delta: float, optional
        Risk aversion factor of Black Litterman model. Default value is None.
    equilibrium: bool, optional
        If True excess returns are based on equilibrium market portfolio, if False
        excess returns are calculated as historical returns minus risk free rate.
        Default value is True.
    optimize: bool, optional
        If True Black Litterman estimates are used as inputs of mean variance model,
        if False returns equilibrium weights from Black Litterman model
        Default value is True.
    value : float, optional
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Black Litterman portfolio\n"
    weights, stock_returns = optimizer_model.get_black_litterman_portfolio(
        symbols=symbols,
        benchmark=benchmark,
        p_views=p_views,
        q_views=q_views,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        objective=objectives_choices[objective],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        delta=delta,
        equilibrium=equilibrium,
        optimize=optimize,
        value=value,
        value_short=value_short,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure="MV",
            risk_free_rate=0,
            # alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_simb_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_ef(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    value: float = 1.0,
    value_short: float = 0.0,
    n_portfolios: int = 100,
    seed: int = 123,
    tangency: bool = False,
    plot_tickers: bool = True,
    external_axes: bool = False,
):
    """
    Display efficient frontier

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

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
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
        The default is 0.05.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    n_portfolios: int, optional
        "Number of portfolios to simulate. The default value is 100.
    seed: int, optional
        Seed used to generate random portfolios. The default value is 123.
    tangency: bool, optional
        Adds the optimal line with the risk-free asset.
    external_axes: bool
        Optional axes to plot data on
    plot_tickers: bool
        Whether to plot the tickers for the assets
    """

    frontier, mu, cov, stock_returns, weights, X1, Y1, port = optimizer_model.get_ef(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_measure,
        risk_free_rate=risk_free_rate,
        alpha=alpha,
        value=value,
        value_short=value_short,
        n_portfolios=n_portfolios,
        seed=seed,
    )

    try:
        risk_free_rate = risk_free_rate / time_factor[freq.upper()]

        _, ax = plt.subplots(
            figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
        )

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

        return theme.visualize_output(
            force_tight_layout=False, external_axes=external_axes
        )
    except Exception as _:
        console.print("[red]Error plotting efficient frontier.[/red]")
        return None


@log_start_end(log=logger)
def display_risk_parity(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    risk_measure: str = "mv",
    risk_cont: Optional[List[str]] = None,
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    target_return: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a risk parity portfolio using the risk budgeting approach

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.
        - X (integer days) for returns calculated every X days.

    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    risk_measure: str
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

        - 'MV': Standard Deviation.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'CVaR': Conditional Value at Risk.
        - 'EVaR': Entropic Value at Risk.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.

    risk_cont: List[str], optional
        The vector of risk contribution per asset. If empty, the default is
        1/n (number of assets).
    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Risk parity portfolio based on risk budgeting approach\n"
    s_title += "using " + risk_names[risk_measure] + " as risk measure\n"
    weights, stock_returns = optimizer_model.get_risk_parity_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        risk_measure=risk_choices[risk_measure],
        risk_cont=risk_cont,
        risk_free_rate=risk_free_rate,
        alpha=alpha,
        target_return=target_return,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_rel_risk_parity(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    version: str = "A",
    risk_cont: Optional[List[str]] = None,
    penal_factor: float = 1,
    target_return: float = -1,
    mean: str = "hist",
    covariance: str = "hist",
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a relaxed risk parity portfolio using the least squares approach

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.
        - X (integer days) for returns calculated every X days.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    version : str, optional
        Relaxed risk parity model version. The default is 'A'.
        Possible values are:

        - 'A': without regularization and penalization constraints.
        - 'B': with regularization constraint but without penalization constraint.
        - 'C': with regularization and penalization constraints.

    risk_cont: List[str], optional
        The vector of risk contribution per asset. If empty, the default is
        1/n (number of assets).
    penal_factor: float, optional
        The penalization factor of penalization constraints. Only used with
        version 'C'. The default is 1.
    target_return: float, optional
        Constraint on minimum level of portfolio's return.
    mean: str, optional
        The method used to estimate the expected returns.
        The default value is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)
    s_title = f"{p} Relaxed risk parity portfolio based on least squares approach\n"
    weights, stock_returns = optimizer_model.get_rel_risk_parity_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        version=version.upper(),
        risk_cont=risk_cont,
        penal_factor=penal_factor,
        target_return=target_return,
        mean=mean,
        covariance=covariance,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices["mv"],
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_hcp(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    model: str = "HRP",
    codependence: str = "pearson",
    covariance: str = "hist",
    objective: str = "minrisk",
    risk_measure: str = "mv",
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: Optional[float] = None,
    b_sim: Optional[int] = None,
    linkage: str = "ward",
    k: Optional[int] = None,
    max_k: int = 10,
    bins_info: str = "KN",
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a hierarchical clustering portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    model: str, optional
        The hierarchical cluster portfolio model used for optimize the
        portfolio. The default is 'HRP'. Possible values are:

        - 'HRP': Hierarchical Risk Parity.
        - 'HERC': Hierarchical Equal Risk Contribution.
        - 'NCO': Nested Clustered Optimization.

    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}.
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}.
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    objective: str, optional
        Objective function used by the NCO model.
        The default is 'MinRisk'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'ERC': Equally risk contribution portfolio of the selected risk measure.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio, by default 1.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)

    if model == "HRP":
        s_title = f"{p} Hierarchical risk parity portfolio"
        s_title += " using " + codependence + " codependence,\n" + linkage
    elif model == "HERC":
        s_title = f"{p} Hierarchical equal risk contribution portfolio"
        s_title += " using " + codependence + "\ncodependence," + linkage
    elif model == "NCO":
        s_title = f"{p} Nested clustered optimization"
        s_title += " using " + codependence + " codependence,\n" + linkage
    s_title += " linkage and " + risk_names[risk_measure] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_hcp_portfolio(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        model=model,
        codependence=codependence,
        covariance=covariance,
        objective=objectives_choices[objective],
        risk_measure=risk_choices[risk_measure],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        linkage=linkage,
        k=k,
        max_k=max_k,
        bins_info=bins_info,
        alpha_tail=alpha_tail,
        leaf_order=leaf_order,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_hrp(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    codependence: str = "pearson",
    covariance: str = "hist",
    risk_measure: str = "mv",
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: Optional[float] = None,
    b_sim: Optional[int] = None,
    linkage: str = "single",
    k: int = 0,
    max_k: int = 10,
    bins_info: str = "KN",
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a hierarchical risk parity portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}.
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}.
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)

    s_title = f"{p} Hierarchical risk parity portfolio"
    s_title += " using " + codependence + " codependence,\n" + linkage
    s_title += " linkage and " + risk_names[risk_measure] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_hrp(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        codependence=codependence,
        covariance=covariance,
        risk_measure=risk_choices[risk_measure],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        linkage=linkage,
        k=k,
        max_k=max_k,
        bins_info=bins_info,
        alpha_tail=alpha_tail,
        leaf_order=leaf_order,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_herc(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    codependence: str = "pearson",
    covariance: str = "hist",
    risk_measure: str = "mv",
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: Optional[float] = None,
    b_sim: Optional[int] = None,
    linkage: str = "ward",
    k: int = 0,
    max_k: int = 10,
    bins_info: str = "KN",
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a hierarchical equal risk contribution portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    model: str, optional
        The hierarchical cluster portfolio model used for optimize the
        portfolio. The default is 'HRP'. Possible values are:

        - 'HRP': Hierarchical Risk Parity.
        - 'HERC': Hierarchical Equal Risk Contribution.
        - 'NCO': Nested Clustered Optimization.

    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}.
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}.
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)

    s_title = f"{p} Hierarchical equal risk contribution portfolio"
    s_title += " using " + codependence + "\ncodependence," + linkage
    s_title += " linkage and " + risk_names[risk_measure] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_herc(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        codependence=codependence,
        covariance=covariance,
        risk_measure=risk_choices[risk_measure],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        linkage=linkage,
        k=k,
        max_k=max_k,
        bins_info=bins_info,
        alpha_tail=alpha_tail,
        leaf_order=leaf_order,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def display_nco(
    symbols: List[str],
    interval: str = "3y",
    start_date: str = "",
    end_date: str = "",
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
    codependence: str = "pearson",
    covariance: str = "hist",
    objective: str = "MinRisk",
    risk_measure: str = "mv",
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: Optional[float] = None,
    b_sim: Optional[int] = None,
    linkage: str = "ward",
    k: Optional[int] = None,
    max_k: int = 10,
    bins_info: str = "KN",
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
) -> Dict:
    """
    Builds a hierarchical equal risk contribution portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    model: str, optional
        The hierarchical cluster portfolio model used for optimize the
        portfolio. The default is 'HRP'. Possible values are:

        - 'HRP': Hierarchical Risk Parity.
        - 'HERC': Hierarchical Equal Risk Contribution.
        - 'NCO': Nested Clustered Optimization.

    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}.
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}.
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    objective: str, optional
        Objective function used by the NCO model.
        The default is 'MinRisk'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'ERC': Equally risk contribution portfolio of the selected risk measure.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    """
    p = d_period(interval, start_date, end_date)

    s_title = f"{p} Nested clustered optimization"
    s_title += " using " + codependence + " codependence,\n" + linkage
    s_title += " linkage and " + risk_names[risk_measure] + " as risk measure\n"

    weights, stock_returns = optimizer_model.get_nco(
        symbols=symbols,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
        codependence=codependence,
        covariance=covariance,
        objective=objectives_choices[objective.lower()],
        risk_measure=risk_choices[risk_measure],
        risk_free_rate=risk_free_rate,
        risk_aversion=risk_aversion,
        alpha=alpha,
        a_sim=a_sim,
        beta=beta,
        b_sim=b_sim,
        linkage=linkage,
        k=k,
        max_k=max_k,
        bins_info=bins_info,
        alpha_tail=alpha_tail,
        leaf_order=leaf_order,
        d_ewma=d_ewma,
        value=value,
    )

    if not weights:
        console.print("There is no solution with this parameters")
        return {}

    if table:
        console.print(s_title)
        display_weights(weights)
        portfolio_performance(
            weights=weights,
            data=stock_returns,
            risk_measure=risk_choices[risk_measure],
            risk_free_rate=risk_free_rate,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
            freq=freq,
        )

    return weights


@log_start_end(log=logger)
def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""


@log_start_end(log=logger)
def pie_chart_weights(
    weights: dict,
    title_opt: str,
    external_axes: bool = False,
):
    """Show a pie chart of holdings

    Parameters
    ----------
    weights: dict
        Weights to display, where keys are tickers, and values are either weights or values if -v specified
    title_opt: str
        Title to be used on the plot title
    external_axes: bool
        Optional external axes to plot data on
    """
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

    title = "Portfolio - " + title_opt + "\n"
    title += "Portfolio Composition"
    ax.set_title(title)

    return theme.visualize_output(force_tight_layout=True, external_axes=external_axes)


@log_start_end(log=logger)
def additional_plots(
    weights: Dict,
    data: pd.DataFrame,
    category_dict: Optional[Dict] = None,
    category: str = "",
    portfolio_name: str = "",
    freq: str = "D",
    risk_measure: str = "MV",
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    a_sim: float = 100,
    beta: Optional[float] = None,
    b_sim: Optional[float] = None,
    pie: bool = False,
    hist: bool = False,
    dd: bool = False,
    rc_chart: bool = False,
    heat: bool = False,
    external_axes: bool = False,
):
    """
    Plot additional charts

    Parameters
    ----------
    weights: Dict
        Dict of portfolio weights
    data: pd.DataFrame
        DataFrame of stock returns
    category_dict: Dict
        Dict of categories
    category: str
        Category to plot
    portfolio_name: str
        Portfolio name
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
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
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    pie : bool, optional
        Display a pie chart of values, by default False
    hist : bool, optional
        Display a histogram with risk measures, by default False
    dd : bool, optional
        Display a drawdown chart with risk measures, by default False
    rc-chart : float, optional
        Display a risk contribution chart for assets, by default False
    heat : float, optional
        Display a heatmap of correlation matrix with dendrogram, by default False
    external_axes: bool
        Optional axes to plot data on
    """

    title_opt = category if not portfolio_name else category + " - " + portfolio_name

    if category_dict is not None:
        weights_df = pd.DataFrame.from_dict(
            data=weights, orient="index", columns=["value"], dtype=float
        )
        category_df = pd.DataFrame.from_dict(
            data=category_dict, orient="index", columns=["category"]
        )
        weights_df = weights_df.join(category_df, how="inner")
        weights_df.sort_index(inplace=True)

        # Calculating classes returns
        classes = list(set(weights_df["category"]))
        weights_classes = weights_df.groupby(["category"]).sum()
        matrix_classes = np.zeros((len(weights_df), len(classes)))
        labels = weights_df["category"].tolist()

        j_value = 0
        for i in classes:
            matrix_classes[:, j_value] = np.array(
                [1 if x == i else 0 for x in labels], dtype=float
            )
            matrix_classes[:, j_value] = (
                matrix_classes[:, j_value]
                * weights_df["value"]
                / weights_classes.loc[i, "value"]
            )
            j_value += 1

        matrix_classes = pd.DataFrame(
            matrix_classes, columns=classes, index=weights_df.index
        )
        data = data @ matrix_classes
        weights_df = weights_classes["value"].copy()
        weights_df.replace(0, np.nan, inplace=True)
        weights_df.dropna(inplace=True)
        weights_df.sort_values(ascending=True, inplace=True)
        data = data[weights_df.index.tolist()]
        data.columns = [i.title() for i in data.columns]
        weights_df.index = [i.title() for i in weights_df.index]
        weights = weights_df.to_dict()

    colors = theme.get_colors()
    if pie:
        pie_chart_weights(weights, title_opt, external_axes)

    if hist:
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

        title = "Portfolio - " + title_opt + "\n"
        title += ax.get_title(loc="left")
        ax.set_title(title)

        return theme.visualize_output(
            force_tight_layout=False, external_axes=external_axes
        )

    if dd:
        _, ax = plt.subplots(
            figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
        )

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

        return theme.visualize_output(
            force_tight_layout=False, external_axes=external_axes
        )

    if rc_chart:
        _, ax = plt.subplots(
            figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
        )

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

        return theme.visualize_output(
            force_tight_layout=False, external_axes=external_axes
        )

    if heat:
        if len(weights) == 1:
            single_key = list(weights.keys())[0].upper()
            console.print(
                f"[yellow]Heatmap needs at least two values for '{category}', only found '{single_key}'.[/yellow]"
            )
            return None

        _, ax = plt.subplots(
            figsize=plot_autoscale(), dpi=get_current_user().preferences.PLOT_DPI
        )

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

        if category_dict is None:
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

        return theme.visualize_output(
            force_tight_layout=False, external_axes=external_axes
        )

    return None


def display_show(weights: Dict, tables: List[str], categories_dict: Dict[Any, Any]):
    """Display the results of the optimization.

    Parameters
    ----------
    weights : Dict
        Dictionary of weights.
    tables : List[str]
        List of tables to display.
    categories_dict : Dict[Any, Any]
        Dictionary of categories.
    """

    display_weights(weights)

    for t in tables:
        console.print("")
        display_categories(
            weights=weights,
            categories=categories_dict,
            column=t,
            title="Category - " + t.title(),
        )
