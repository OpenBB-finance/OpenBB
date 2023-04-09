"""Optimization Model"""
__docformat__ = "numpy"

# pylint: disable=R0913, C0302, E1101, line-too-long
# flake8: noqa: E501

import logging
from datetime import date
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import riskfolio as rp
from dateutil.relativedelta import FR, relativedelta
from numpy import floating
from numpy.typing import NDArray
from scipy.interpolate import interp1d

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.fundamental_analysis import fmp_model
from openbb_terminal.portfolio.portfolio_optimization import yahoo_finance_model
from openbb_terminal.portfolio.portfolio_optimization.optimizer_helper import (
    get_kwarg,
    validate_risk_measure,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

upper_risk = {
    "MV": "upperdev",
    "MAD": "uppermad",
    "MSV": "uppersdev",
    "FLPM": "upperflpm",
    "SLPM": "upperslpm",
    "CVaR": "upperCVaR",
    "EVaR": "upperEVaR",
    "WR": "upperwr",
    "MDD": "uppermdd",
    "ADD": "upperadd",
    "CDaR": "upperCDaR",
    "EDaR": "upperEDaR",
    "UCI": "upperuci",
}

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
def get_equal_weights(
    symbols: List[str],
    **kwargs,
) -> Union[Tuple[Dict[str, float], pd.DataFrame], None]:
    """Equally weighted portfolio, where weight = 1/# of symbols

    Parameters
    ----------
    symbols : List[str]
        List of symbols to be included in the portfolio
    interval : str, optional
        Interval to get data, by default "3y"
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD), by default ""
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last weekday, by default ""
    log_returns: bool, optional
        If True use log returns, else arithmetic returns, by default False
    freq: str, optional
        Frequency of returns, by default "D". Options: "D" for daily, "W" for weekly, "M" for monthly
    maxnan: float
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float
        Value used to replace outliers that are higher than threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate.  Returns percentages if set to 1.

    Returns
    -------
    Union[Tuple[Dict[str, float], pd.DataFrame], None]
        Dictionary of weights where keys are the tickers, dataframe of stock returns
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    weights = {
        stock: value * round(1 / len(stock_returns.columns), 5)
        for stock in stock_returns.columns
    }

    return weights, stock_returns


@log_start_end(log=logger)
def get_property_weights(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[Dict[str, Any]], Optional[pd.DataFrame]]:
    """Calculate portfolio weights based on selected property, currently this is only market cap.

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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
    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount of money to allocate

    Returns
    -------
    Tuple[Dict[str, Any], pd.DataFrame]
        Dictionary of portfolio weights or allocations
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    prop = {}
    no_data = []
    prop_sum = 0
    for stock in symbols:
        stock_prop = get_market_cap(stock)
        prop[stock] = stock_prop
        prop_sum += stock_prop

        if not prop[stock]:
            no_data.append(stock)

    if prop_sum == 0:
        console.print(
            "No market cap data has been found for all selected tickers. Not able to optimize the portfolio.",
            "\n",
        )
        return None, None
    if no_data:
        console.print(
            "No market cap data has been found for the following tickers: "
            + ", ".join(no_data)
            + ". Therefore, these will be excluded from the optimization process.",
            "\n",
        )

    weights = {k: value * v / prop_sum for k, v in prop.items()}

    return weights, stock_returns


@log_start_end(log=logger)
def get_market_cap(symbol) -> float:
    """Get market cap from FinancialModelingPrep

    Parameters
    ----------
    symbol : str
        Stock ticker

    Returns
    -------
    updated_value : float
        value of market cap
    """
    market_cap = fmp_model.get_enterprise(symbol)

    if not market_cap.empty:
        latest_year = market_cap.index[-1]

        value = market_cap.loc[latest_year]["Market capitalization"]

        if "M" in value:
            updated_value = float(value.split(" M")[0]) * 1000000
        elif "B" in value:
            updated_value = float(value.split(" B")[0]) * 1000000000
        elif "T" in value:
            updated_value = float(value.split(" T")[0]) * 1000000000000
        else:
            updated_value = float(value)
    else:
        updated_value = 0

    return updated_value


@log_start_end(log=logger)
def get_mean_risk_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a mean risk optimal portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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

    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    objective: str
        Objective function of the optimization model.
        The default is 'Sharpe'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

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
        Risk free rate, must be in annual frequency. Used for
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
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)
    value_short = get_kwarg("value_short", kwargs)

    risk_measure = get_kwarg("risk_measure", kwargs)
    objective = get_kwarg("objective", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    risk_aversion = get_kwarg("risk_aversion", kwargs)
    alpha = get_kwarg("alpha", kwargs)
    target_return = get_kwarg("target_return", kwargs)
    target_risk = get_kwarg("target_risk", kwargs)
    mean = get_kwarg("mean", kwargs)
    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)

    risk_measure = validate_risk_measure(risk_measure)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )
    if stock_returns.empty:
        console.print(
            "[red]Not enough data points in range to run calculations.[/red]\n"
        )
        return {}, pd.DataFrame()

    if stock_returns.shape[1] < 2:
        console.print(
            f"[red]Given the parameters could only get data for '{stock_returns.columns[0]}'.[/red]\n"
            "[red]Optimization needs at least two assets.[/red]\n",
        )
        return {}, pd.DataFrame()

    first_day = stock_returns.index[0].strftime("%Y-%m-%d")
    console.print(
        f"[yellow]First day of data respecting parameters: {first_day}[/yellow]\n"
    )

    risk_free_rate = risk_free_rate / time_factor[freq.upper()]

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns, alpha=alpha)

        # Estimate input parameters:
        port.assets_stats(method_mu=mean, method_cov=covariance, d=d_ewma)

        # Budget constraints
        port.upperlng = value
        if value_short > 0:
            port.sht = True
            port.uppersht = value_short
            port.budget = value - value_short
        else:
            port.budget = value

        # Estimate optimal portfolio:
        model = "Classic"
        hist = True

        if target_return > -1:
            port.lowerret = float(target_return) / time_factor[freq.upper()]

        if target_risk > -1:
            if risk_measure not in ["ADD", "MDD", "CDaR", "EDaR", "UCI"]:
                setattr(
                    port,
                    upper_risk[risk_measure],
                    float(target_risk) / time_factor[freq.upper()] ** 0.5,
                )
            else:
                setattr(port, upper_risk[risk_measure], float(target_risk))

        weights = port.optimization(
            model=model,
            rm=risk_measure,
            obj=objective,
            rf=risk_free_rate,
            l=risk_aversion,
            hist=hist,
        )

    except Exception as _:
        weights = None

    if weights is not None:
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_max_sharpe(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    weights, stock_returns = get_mean_risk_portfolio(
        symbols=symbols,
        objective=objectives_choices["sharpe"],
        **kwargs,
    )

    return weights, stock_returns


@log_start_end(log=logger)
def get_min_risk(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    weights, stock_returns = get_mean_risk_portfolio(
        symbols=symbols,
        objective=objectives_choices["minrisk"],
        **kwargs,
    )

    return weights, stock_returns


@log_start_end(log=logger)
def get_max_util(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    weights, stock_returns = get_mean_risk_portfolio(
        symbols=symbols,
        objective=objectives_choices["utility"],
        **kwargs,
    )

    return weights, stock_returns


@log_start_end(log=logger)
def get_max_ret(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """
    weights, stock_returns = get_mean_risk_portfolio(
        symbols=symbols,
        objective=objectives_choices["maxret"],
        **kwargs,
    )

    return weights, stock_returns


@log_start_end(log=logger)
def get_max_diversification_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a maximal diversification portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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

    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
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
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)
    value_short = get_kwarg("value_short", kwargs)

    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns)

        # Estimate input parameters:
        port.assets_stats(method_mu="hist", method_cov=covariance, d=d_ewma)
        port.mu = stock_returns.std().to_frame().T

        # Budget constraints
        port.upperlng = value
        if value_short > 0:
            port.sht = True
            port.uppersht = value_short
            port.budget = value - value_short
        else:
            port.budget = value

        # Estimate optimal portfolio:
        weights = port.optimization(
            model="Classic", rm="MV", obj="Sharpe", rf=0, hist=True
        )
    except Exception as _:
        weights = None

    if weights is not None:
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_max_decorrelation_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a maximal decorrelation portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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

    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see s`interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
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
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)
    value_short = get_kwarg("value_short", kwargs)

    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns)

        # Estimate input parameters:
        port.assets_stats(method_mu="hist", method_cov=covariance, d=d_ewma)
        port.cov = rp.cov2corr(port.cov)

        # Budget constraints
        port.upperlng = value
        if value_short > 0:
            port.sht = True
            port.uppersht = value_short
            port.budget = value - value_short
        else:
            port.budget = value

        # Estimate optimal portfolio:
        weights = port.optimization(
            model="Classic", rm="MV", obj="MinRisk", rf=0, hist=True
        )
    except Exception as _:
        weights = None

    if weights is not None:
        weights = weights.round(5)

        if len(weights) > 1:
            weights = weights.squeeze().to_dict()
        else:
            weights = weights.to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_black_litterman_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a maximal diversification portfolio

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    benchmark : Dict
        Dict of portfolio weights
    p_views: List
        Matrix P of views that shows relationships among assets and returns.
        Default value to None.
    q_views: List
        Matrix Q of expected returns of views. Default value is None.
    interval : str, optional
        interval to get stock data, by default "3mo"
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

    maxnan: float
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float
        Value used to replace outliers that are higher to threshold.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)
    value_short = get_kwarg("value_short", kwargs)

    benchmark = get_kwarg("benchmark", kwargs)
    p_views = get_kwarg("p_views", kwargs)
    q_views = get_kwarg("q_views", kwargs)
    objective = get_kwarg("objective", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    risk_aversion = get_kwarg("risk_aversion", kwargs)
    delta = get_kwarg("delta", kwargs)
    equilibrium = get_kwarg("equilibrium", kwargs)
    optimize = get_kwarg("optimize", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    # By theory default benchmark is market capitalization portfolio
    if benchmark is None:
        benchmark, _ = get_property_weights(
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

    if benchmark is None:
        return None, stock_returns

    factor = time_factor[freq.upper()]
    risk_free_rate = risk_free_rate / factor

    mu, cov, weights = black_litterman(
        stock_returns=stock_returns,
        benchmark=benchmark,
        p_views=p_views,
        q_views=q_views,
        delta=delta,
        risk_free_rate=risk_free_rate,
        equilibrium=equilibrium,
        factor=factor,
    )
    weights = pd.DataFrame(weights)

    if optimize:
        try:
            # Building the portfolio object
            port = rp.Portfolio(returns=stock_returns)

            # Estimate input parameters:
            port.assets_stats(method_mu="hist", method_cov="hist")
            port.mu_bl = pd.DataFrame(mu).T
            port.cov_bl = pd.DataFrame(cov)

            # Budget constraints
            port.upperlng = value
            if value_short > 0:
                port.sht = True
                port.uppersht = value_short
                port.budget = value - value_short
            else:
                port.budget = value

            # Estimate optimal portfolio:
            weights = port.optimization(
                model="BL",
                rm="MV",
                obj=objective,
                rf=risk_free_rate,
                l=risk_aversion,
                hist=True,
            )
        except Exception as _:
            weights = None

    if weights is not None:
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_ef(
    symbols: List[str],
    **kwargs,
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    Optional[pd.DataFrame],
    NDArray[floating],
    NDArray[floating],
    rp.Portfolio,
]:
    """
    Get efficient frontier

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

    Returns
    -------
    Tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        Optional[pd.DataFrame],
        NDArray[floating],
        NDArray[floating],
        rp.Portfolio,
    ]
        Parameters to create efficient frontier:
        frontier, mu, cov, stock_returns, weights, X1, Y1, port
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)
    value_short = get_kwarg("value_short", kwargs)

    risk_measure = get_kwarg("risk_measure", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    alpha = get_kwarg("alpha", kwargs)
    n_portfolios = get_kwarg("n_portfolios", kwargs)
    seed = get_kwarg("seed", kwargs)

    risk_free_rate = risk_free_rate / time_factor[freq.upper()]
    risk_measure = validate_risk_measure(risk_measure)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns, alpha=alpha)

        # Estimate input parameters:
        port.assets_stats(method_mu="hist", method_cov="hist")

        # Budget constraints
        port.upperlng = value
        if value_short > 0:
            port.sht = True
            port.uppersht = value_short
            port.budget = value - value_short
        else:
            port.budget = value

        # Estimate tangency portfolio:
        weights: Optional[pd.DataFrame] = port.optimization(
            model="Classic",
            rm=risk_choices[risk_measure.lower()],
            obj="Sharpe",
            rf=risk_free_rate,
            hist=True,
        )
    except Exception as _:
        weights = None

    points = 20  # Number of points of the frontier
    frontier = port.efficient_frontier(
        model="Classic",
        rm=risk_choices[risk_measure.lower()],
        points=points,
        rf=risk_free_rate,
        hist=True,
    )

    random_weights = generate_random_portfolios(
        symbols=symbols,
        n_portfolios=n_portfolios,
        seed=seed,
    )

    mu = stock_returns.mean().to_frame().T
    cov = stock_returns.cov()
    Y = (mu @ frontier).to_numpy() * time_factor[freq.upper()]
    Y = np.ravel(Y)
    X = np.zeros_like(Y)

    for i in range(frontier.shape[1]):
        w = np.array(frontier.iloc[:, i], ndmin=2).T
        risk = rp.Sharpe_Risk(
            w,
            cov=cov,
            returns=stock_returns,
            rm=risk_choices[risk_measure.lower()],
            rf=risk_free_rate,
            alpha=alpha,
            # a_sim=a_sim,
            # beta=beta,
            # b_sim=b_sim,
        )
        X[i] = risk

    if risk_choices[risk_measure.lower()] not in ["ADD", "MDD", "CDaR", "EDaR", "UCI"]:
        X = X * time_factor[freq.upper()] ** 0.5
    f = interp1d(X, Y, kind="quadratic")
    X1 = np.linspace(X[0], X[-1], num=100)
    Y1 = f(X1)

    frontier = pd.concat([frontier, random_weights], axis=1)
    # to delete stocks with corrupted data
    frontier.drop(
        frontier.tail(len(random_weights.index) - len(stock_returns.columns)).index,
        inplace=True,
    )

    return frontier, mu, cov, stock_returns, weights, X1, Y1, port


@log_start_end(log=logger)
def get_risk_parity_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a risk parity portfolio using the risk budgeting approach

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.

    risk_cont: List[str], optional
        The vector of risk contribution per asset. If empty, the default is
        1/n (number of assets).
    risk_free_rate: float, optional
        Risk free rate, must be in annual frequency. Used for
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
        Amount of money to allocate. The default is 1.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)

    risk_measure = get_kwarg("risk_measure", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    alpha = get_kwarg("alpha", kwargs)
    target_return = get_kwarg("target_return", kwargs)
    mean = get_kwarg("mean", kwargs)
    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)
    risk_cont = get_kwarg("risk_cont", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    risk_free_rate = risk_free_rate / time_factor[freq.upper()]
    risk_measure = validate_risk_measure(risk_measure)

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns, alpha=alpha)

        # Calculating optimal portfolio
        port.assets_stats(method_mu=mean, method_cov=covariance, d=d_ewma)

        # Estimate optimal portfolio:
        model = "Classic"
        hist = True

        if risk_cont is None:
            risk_cont_ = None  # Risk contribution constraints vector
        else:
            risk_cont_ = np.array(risk_cont).reshape(1, -1)
            risk_cont_ = risk_cont_ / np.sum(risk_cont_)

        if target_return > -1:
            port.lowerret = float(target_return) / time_factor[freq.upper()]

        weights = port.rp_optimization(
            model=model, rm=risk_measure, rf=risk_free_rate, b=risk_cont_, hist=hist
        )
    except Exception as _:
        weights = None

    if weights is not None:
        if value > 0.0:
            weights = value * weights
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_rel_risk_parity_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds a relaxed risk parity portfolio using the least squares approach

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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
        Amount of money to allocate. The default is 1.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)

    target_return = get_kwarg("target_return", kwargs)
    mean = get_kwarg("mean", kwargs)
    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)
    risk_cont = get_kwarg("risk_cont", kwargs)
    version = get_kwarg("version", kwargs)
    penal_factor = get_kwarg("penal_factor", kwargs)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    try:
        # Building the portfolio object
        port = rp.Portfolio(returns=stock_returns)

        # Calculating optimal portfolio
        port.assets_stats(method_mu=mean, method_cov=covariance, d=d_ewma)

        # Estimate optimal portfolio:
        model = "Classic"
        hist = True

        if risk_cont is None:
            risk_cont_ = None  # Risk contribution constraints vector
        else:
            risk_cont_ = np.array(risk_cont).reshape(1, -1)
            risk_cont_ = risk_cont_ / np.sum(risk_cont_)

        if target_return > -1:
            port.lowerret = float(target_return) / time_factor[freq.upper()]

        weights = port.rrp_optimization(
            model=model, version=version, l=penal_factor, b=risk_cont_, hist=hist
        )
    except Exception as _:
        weights = None

    if weights is not None:
        if value > 0.0:
            weights = value * weights
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_hcp_portfolio(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
    """Builds hierarchical clustering based portfolios

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}
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
        Risk free rate, must be in annual frequency.
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
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.
        cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`__.
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
    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount of money to allocate. The default is 1.

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    interval = get_kwarg("interval", kwargs)
    start_date = get_kwarg("start_date", kwargs)
    end_date = get_kwarg("end_date", kwargs)
    log_returns = get_kwarg("log_returns", kwargs)
    freq = get_kwarg("freq", kwargs)
    maxnan = get_kwarg("maxnan", kwargs)
    threshold = get_kwarg("threshold", kwargs)
    method = get_kwarg("method", kwargs)
    value = get_kwarg("value", kwargs)

    objective = get_kwarg("objective", kwargs)
    risk_measure = get_kwarg("risk_measure", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    risk_aversion = get_kwarg("risk_aversion", kwargs)
    alpha = get_kwarg("alpha", kwargs)
    a_sim = get_kwarg("a_sim", kwargs)
    beta = get_kwarg("beta", kwargs)
    b_sim = get_kwarg("b_sim", kwargs)
    covariance = get_kwarg("covariance", kwargs)
    d_ewma = get_kwarg("d_ewma", kwargs)

    model = get_kwarg("model", kwargs, default="HRP")

    codependence = get_kwarg("codependence", kwargs)
    linkage = get_kwarg("linkage", kwargs)
    k = get_kwarg("k", kwargs)
    max_k = get_kwarg("max_k", kwargs)
    bins_info = get_kwarg("bins_info", kwargs)
    alpha_tail = get_kwarg("alpha_tail", kwargs)
    leaf_order = get_kwarg("leaf_order", kwargs)

    risk_measure = validate_risk_measure(risk_measure)

    stock_prices = yahoo_finance_model.process_stocks(
        symbols, interval, start_date, end_date
    )
    stock_returns = yahoo_finance_model.process_returns(
        stock_prices,
        log_returns=log_returns,
        freq=freq,
        maxnan=maxnan,
        threshold=threshold,
        method=method,
    )

    if linkage == "dbht":
        linkage = linkage.upper()

    risk_free_rate = risk_free_rate / time_factor[freq.upper()]

    try:
        # Building the portfolio object
        port = rp.HCPortfolio(
            returns=stock_returns,
            alpha=alpha,
            a_sim=a_sim,
            beta=beta,
            b_sim=b_sim,
        )

        weights = port.optimization(
            model=model,
            codependence=codependence,
            covariance=covariance,
            obj=objective,
            rm=risk_measure,
            rf=risk_free_rate,
            l=risk_aversion,
            linkage=linkage,
            k=k,
            max_k=max_k,
            bins_info=bins_info,
            alpha_tail=alpha_tail,
            leaf_order=leaf_order,
            d=d_ewma,
        )
    except Exception as _:
        weights = None

    if weights is not None:
        if value > 0.0:
            weights = value * weights
        weights = weights.round(5)
        weights = weights.squeeze().to_dict()

    return weights, stock_returns


@log_start_end(log=logger)
def get_hrp(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """

    weights, stock_returns = get_hcp_portfolio(
        symbols=symbols,
        model="HRP",
        **kwargs,
    )
    return weights, stock_returns


@log_start_end(log=logger)
def get_herc(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """
    weights, stock_returns = get_hcp_portfolio(
        symbols=symbols,
        model="HERC",
        **kwargs,
    )
    return weights, stock_returns


@log_start_end(log=logger)
def get_nco(
    symbols: List[str],
    **kwargs,
) -> Tuple[Optional[dict], pd.DataFrame]:
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
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{pearson}_{i,j})}
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{0.5(1-\\rho^{spearman}_{i,j})}
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{pearson}_{i,j}|)}
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-|\\rho^{spearman}_{i,j}|)}
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \\sqrt{(1-\\rho^{distance}_{i,j})}
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

    Returns
    -------
    Tuple[Optional[dict], pd.DataFrame]
        Dictionary of portfolio weights,
        DataFrame of stock returns.
    """
    weights, stock_returns = get_hcp_portfolio(
        symbols=symbols,
        model="NCO",
        **kwargs,
    )
    return weights, stock_returns


@log_start_end(log=logger)
def black_litterman(
    stock_returns: pd.DataFrame,
    benchmark,
    **kwargs,
) -> Tuple[dict, dict, dict]:
    """
    Calculates Black-Litterman estimates following He and Litterman (1999)

    Parameters
    ----------
    stock_returns: pd.DataFrame
        _description_
    benchmark: Dict
        Dict of portfolio weights
    p_views: List
        Matrix P of views that shows relationships among assets and returns.
        Default value to None.
    q_views: List
        Matrix Q of expected returns of views in annual frequency. Default value is None.
    delta: float
        Risk aversion factor. Default value is None.
    risk_free_rate: float, optional
        Risk free rate, must be in annual frequency. Default value is 0.
    equilibrium: bool, optional
        If True excess returns are based on equilibrium market portfolio, if False
        excess returns are calculated as historical returns minus risk free rate.
        Default value is True.
    factor: int
        The time factor

    Returns
    -------
    Tuple[dict, dict, dict]
        Black-Litterman model estimates of expected returns,
        Covariance matrix,
        Portfolio weights.
    """

    p_views = get_kwarg("p_views", kwargs)
    q_views = get_kwarg("q_views", kwargs)
    delta = get_kwarg("delta", kwargs)
    risk_free_rate = get_kwarg("risk_free_rate", kwargs)
    equilibrium = get_kwarg("equilibrium", kwargs)
    factor = get_kwarg("factor", kwargs, default=252)

    symbols = stock_returns.columns.tolist()
    benchmark = pd.Series(benchmark).to_numpy().reshape(-1, 1)

    mu = stock_returns.mean().to_numpy().reshape(-1, 1)
    S = stock_returns.cov().to_numpy()

    if delta is None:
        a = mu.T @ benchmark
        delta = (a - risk_free_rate) / (benchmark.T @ S @ benchmark)
        delta = delta.item()

    if equilibrium:
        PI_eq = delta * (S @ benchmark)
    else:
        PI_eq = mu - risk_free_rate

    flag = False
    if p_views is None or q_views is None:
        p_views = np.identity(S.shape[0])
        q_views = PI_eq
        flag = True
    else:
        p_views = np.array(p_views, dtype=float)
        q_views = np.array(q_views, dtype=float).reshape(-1, 1) / factor

    tau = 1 / stock_returns.shape[0]
    Omega = np.diag(np.diag(p_views @ (tau * S) @ p_views.T))

    PI = np.linalg.inv(
        np.linalg.inv(tau * S) + p_views.T @ np.linalg.inv(Omega) @ p_views
    ) @ (np.linalg.inv(tau * S) @ PI_eq + p_views.T @ np.linalg.inv(Omega) @ q_views)

    if flag:
        n, m = S.shape
        M = np.zeros([n, m])
    else:
        M = np.linalg.inv(
            np.linalg.inv(tau * S) + p_views.T @ np.linalg.inv(Omega) @ p_views
        )

    mu = PI + risk_free_rate
    cov = S + M
    weights = np.linalg.inv(delta * cov) @ PI

    mu = pd.DataFrame(mu, index=symbols).to_dict()
    cov = pd.DataFrame(cov, index=symbols, columns=symbols).to_dict()
    weights = pd.DataFrame(weights, index=symbols).to_dict()

    return mu, cov, weights


@log_start_end(log=logger)
def generate_random_portfolios(
    symbols: List[str],
    n_portfolios: int = 100,
    seed: int = 123,
    value: float = 1.0,
) -> pd.DataFrame:
    """Build random portfolios

    Parameters
    ----------
    symbols : List[str]
        List of portfolio stocks
    n_portfolios: int, optional
        "Number of portfolios to simulate. The default value is 100.
    seed: int, optional
        Seed used to generate random portfolios. The default value is 123.
    value : float, optional
        Amount of money to allocate. The default is 1.
    """
    assets = symbols.copy()

    # Generate random portfolios
    n_samples = int(n_portfolios / 3)
    rs = np.random.RandomState(seed=seed)

    # Equal probability for each asset
    w1 = rs.dirichlet(np.ones(len(assets)), n_samples)

    # More concentrated
    w2 = rs.dirichlet(np.ones(len(assets)) * 0.65, n_samples)

    # More diversified
    w3 = rs.dirichlet(np.ones(len(assets)) * 2, n_samples)

    # Each individual asset
    w4 = np.identity(len(assets))
    w = np.concatenate((w1, w2, w3, w4), axis=0)
    w = pd.DataFrame(w, columns=assets).T

    if value > 0.0:
        w = value * w

    return w


@log_start_end(log=logger)
def get_categories(
    weights: dict, categories: dict, column: str = "ASSET_CLASS"
) -> pd.DataFrame:
    """Get categories from dictionary

    Parameters
    ----------
    weights : dict
        Dictionary with weights
    categories: dict
        Dictionary with categories
    column : str, optional
        Column name to use on categories, by default "ASSET_CLASS"

    Returns
    -------
    pd.DataFrame
        DataFrame with weights
    """

    if not weights:
        return pd.DataFrame()

    if column == "CURRENT_INVESTED_AMOUNT":
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(
        data=weights, orient="index", columns=["value"], dtype=float
    )
    categories_df = pd.DataFrame.from_dict(data=categories, dtype=float)

    categories_df = df.join(categories_df)
    categories_df.set_index(column, inplace=True)
    categories_df.groupby(level=0).sum()

    df = pd.pivot_table(
        categories_df,
        values=["value", "CURRENT_INVESTED_AMOUNT"],
        index=["CURRENCY", column],
        aggfunc=np.sum,
    )
    df["CURRENT_WEIGHTS"] = (
        df["CURRENT_INVESTED_AMOUNT"].groupby(level=0).transform(lambda x: x / sum(x))
    )
    df["value"] = df["value"].groupby(level=0).transform(lambda x: x / sum(x))
    df = pd.concat(
        [d.append(d.sum().rename((k, "TOTAL " + k))) for k, d in df.groupby(level=0)]
    )
    df = df.iloc[:, [0, 2, 1]]

    return df
