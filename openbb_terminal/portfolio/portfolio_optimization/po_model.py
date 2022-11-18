"""Optimization Model"""
__docformat__ = "numpy"

# pylint: disable=R0913, C0302, E1101, line-too-long
# flake8: noqa: E501

import logging
from typing import Dict, List, Optional, Tuple, Union
import warnings

import pandas as pd
from numpy.typing import NDArray
from numpy import floating
from riskfolio import rp

from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_model,
)
from openbb_terminal.portfolio.portfolio_optimization.statics import (
    RISK_NAMES,
    TIME_FACTOR,
    DRAWDOWNS,
    PARAM_TYPES,
)
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.rich_config import console

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def validate_parameters_type(parameters):
    """Validate parameters type

    Parameters
    ----------
    parameters : dict
        Keyword arguments
    """
    for key, value in parameters.items():
        if key in PARAM_TYPES:
            expected_type = PARAM_TYPES[key]
            if not isinstance(value, expected_type):
                if expected_type is str:
                    parameters.update({key: str(value)})
                elif expected_type is float:
                    parameters.update({key: float(value)})
                elif expected_type is bool:
                    parameters.update({key: bool(value)})
                else:
                    console.print(
                        f"[info]Parameter {key} should be of type {expected_type.__name__}. Casting failed, reverting to default.[/info]"
                    )
                    parameters.pop(key)


@log_start_end(log=logger)
def generate_portfolio(
    symbols: List[str] = None,
    symbols_file_path: str = None,
    parameters_file_path: str = None,
) -> Union[PoEngine, None]:
    """Load portfolio optimization engine

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    symbols_file_path : str, optional
        Symbols file path, by default None
    parameters_file_path : str, optional
        Parameters file path, by default None

    Returns
    -------
    PoEngine
        Portfolio optimization engine
    """

    if symbols:
        return PoEngine(
            symbols=symbols,
            parameters_file_path=parameters_file_path,
        )
    if symbols_file_path:
        return PoEngine(
            symbols_file_path=symbols_file_path,
            parameters_file_path=parameters_file_path,
        )
    console.print("No file or symbols provided")
    return None


@log_start_end(log=logger)
def load_parameters_file(
    parameters_file_path: str,
    portfolio_engine: PoEngine,
):
    """Load portfolio optimization engine from file

    Parameters
    ----------
    parameters_file_path : str
        Parameters file path, by default None
    portfolio_engine : PoEngine
        Portfolio optimization engine, by default None

    Returns
    -------
    Dict
        Parameters
    """

    portfolio_engine.set_params_from_file(parameters_file_path)


@log_start_end(log=logger)
def validate_inputs(
    symbols=None, portfolio_engine=None, kwargs=None
) -> Tuple[List[str], PoEngine, dict]:
    """Check valid inputs

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    kwargs : dict
        Keyword arguments, by default None

    Returns
    -------
    Tuple[List[str], PoEngine, dict]
        List of symbols, Portfolio optimization engine, Keyword arguments
    """

    if symbols:
        portfolio_engine = PoEngine(symbols=symbols)
        parameters = kwargs
    elif portfolio_engine:
        symbols = portfolio_engine.get_symbols()
        parameters = portfolio_engine.get_params().copy()
        parameters.update(kwargs)
    else:
        console.print("No 'symbols' or 'portfolio_engine' provided.")

    validate_parameters_type(parameters)

    return symbols, portfolio_engine, parameters


@log_start_end(log=logger)
def get_portfolio_performance(weights: Dict, data: pd.DataFrame, **kwargs) -> Dict:
    """Get portfolio performance

    Parameters
    ----------
    weights : Dict
        Portfolio weights
    data : pd.DataFrame
        Dataframe with returns

    Returns
    -------
    Dict
        Portfolio performance
    """

    freq = kwargs.get("freq", "D")
    risk_measure = kwargs.get("risk_measure", "MV")
    risk_free_rate = kwargs.get("risk_free_rate", 0.0)
    alpha = kwargs.get("alpha", 0.05)
    a_sim = kwargs.get("a_sim", 100)
    beta = kwargs.get("beta", None)
    b_sim = kwargs.get("b_sim", None)

    freq = freq.upper()
    weights = pd.Series(weights).to_frame()
    returns = data @ weights
    mu = returns.mean().item() * TIME_FACTOR[freq]
    sigma = returns.std().item() * TIME_FACTOR[freq] ** 0.5
    sharpe = (mu - risk_free_rate) / sigma

    performance_dict = {
        "Return": mu,
        "Volatility": sigma,
        "Sharpe ratio": sharpe,
    }

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

        if risk_measure in DRAWDOWNS:
            sharpe_2 = (mu - risk_free_rate) / risk
        else:
            risk = risk * TIME_FACTOR[freq] ** 0.5
            sharpe_2 = (mu - risk_free_rate) / risk

        performance_dict[RISK_NAMES[risk_measure.lower()]] = risk
        performance_dict.update({"Sharpe ratio (risk adjusted)": sharpe_2})

    return performance_dict


@log_start_end(log=logger)
def get_maxsharpe(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize Sharpe ratio weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'Sharpe'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

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
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.maxsharpe(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.maxsharpe(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_sharpe(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_minrisk(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize minimum risk weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'Sharpe'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

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
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.minrisk(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.minrisk(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_min_risk(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_maxutil(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize maximum utility weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'Sharpe'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

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
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.maxutil(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.maxutil(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_util(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_maxret(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize maximum return weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'Sharpe'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

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
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    target_risk: float, optional
        Constraint on maximum level of portfolio's risk, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.maxret(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.maxret(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_ret(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_maxdiv(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize diversification weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
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

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.maxdiv(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.maxdiv(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_diversification_portfolio(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_maxdecorr(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize decorrelation weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.maxdecorr(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.maxdecorr(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_decorrelation_portfolio(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_blacklitterman(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize decorrelation weights

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    benchmark : Dict
        Dict of portfolio weights, by default None
    p_views: List
        Matrix P of views that shows relationships among assets and returns, by default None
    q_views: List
        Matrix Q of expected returns of views, by default None
    objective: str, optional
        Objective function of the optimization model, by default 'Sharpe'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_free_rate: float, optional
        Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    delta: float, optional
        Risk aversion factor of Black Litterman model, by default None
    equilibrium: bool, optional
        If True excess returns are based on equilibrium market portfolio, if False
        excess returns are calculated as historical returns minus risk free rate, by default True
    optimize: bool, optional
        If True Black Litterman estimates are used as inputs of mean variance model,
        if False returns equilibrium weights from Black Litterman model, by default True

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.blacklitterman(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.blacklitterman(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_black_litterman_portfolio(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_ef(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
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
    """Get Efficient Frontier

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    frontier, mu, cov, returns, weights, X1, Y1, port = optimizer_model.get_ef(
        symbols=valid_symbols, **valid_kwargs
    )
    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return frontier, mu, cov, returns, weights, X1, Y1, port


@log_start_end(log=logger)
def get_riskparity(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize with Risk Parity using the risk budgeting approach

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
    risk_cont: List[str], optional
        The vector of risk contribution per asset, by default 1/n (number of assets)

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_risk_parity_portfolio(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_relriskparity(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize with Relaxed Risk Parity using the least squares approach

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    target_return: float, optional
        Constraint on minimum level of portfolio's return, by default -1.0
    mean: str, optional
        The method used to estimate the expected returns, by default 'hist'
        Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.

    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
    risk_cont: List[str], optional
        The vector of risk contribution per asset, by default 1/n (number of assets)
    version : str, optional
        Relaxed risk parity model version, by default 'A'
        Possible values are:

        - 'A': without regularization and penalization constraints.
        - 'B': with regularization constraint but without penalization constraint.
        - 'C': with regularization and penalization constraints.

    penal_factor: float, optional
        The penalization factor of penalization constraints. Only used with
        version 'C', by default 1.0

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_rel_risk_parity_portfolio(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_hrp(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize with Hierarchical Risk Parity

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'MinRisk'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio, by default 'MV'
        If model is 'NCO', the risk measures available depends on the objective function.
        Possible values are:

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
        Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses, by default 100
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value, by default None
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value, by default None
    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
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
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}

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
        of clusters calculated with the two difference gap statistic, by default None
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters, by default 10
    bins_info: str, optional
        Number of bins used to calculate variation of information, by default 'KN'.
        Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index, by default 0.05
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal, by default True

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_hrp(symbols=valid_symbols, **valid_kwargs)
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_herc(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize with Hierarchical Equal Risk Contribution (HERC) method.

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'MinRisk'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio, by default 'MV'
        If model is 'NCO', the risk measures available depends on the objective function.
        Possible values are:

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
        Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses, by default 100
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value, by default None
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value, by default None
    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
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
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}

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
        of clusters calculated with the two difference gap statistic, by default None
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters, by default 10
    bins_info: str, optional
        Number of bins used to calculate variation of information, by default 'KN'.
        Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index, by default 0.05
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal, by default True

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_herc(symbols=valid_symbols, **valid_kwargs)
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_nco(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Optimize with Non-Convex Optimization (NCO) model.

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    objective: str, optional
        Objective function of the optimization model, by default 'MinRisk'
        Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'MaxRet': Maximize the expected return of the portfolio.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio, by default 'MV'
        If model is 'NCO', the risk measures available depends on the objective function.
        Possible values are:

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
        Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function, by default 1.0
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses, by default 100
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value, by default None
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value, by default None
    covariance: str, optional
        The method used to estimate the covariance matrix, by default 'hist'
        Possible values are:

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
        The smoothing factor of ewma methods, by default 0.94
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
            .. math:: D_{i,j} = -\\log{\\lambda_{i,j}}

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
        of clusters calculated with the two difference gap statistic, by default None
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters, by default 10
    bins_info: str, optional
        Number of bins used to calculate variation of information, by default 'KN'.
        Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index, by default 0.05
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal, by default True

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_nco(symbols=valid_symbols, **valid_kwargs)
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_equal(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> Tuple[pd.DataFrame, Dict]:
    """Equally weighted portfolio, where weight = 1/# of symbols

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    maxnan: float
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float
        Value used to replace outliers that are higher than threshold, by default 0.0
    method: str
        Method used to fill nan values, by default 'time'
        For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.equal(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
    >>> openbb.portfolio.po.equal(portfolio_engine=p)
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_equal_weights(
        symbols=valid_symbols, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_mktcap(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to market capitalization

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    maxnan: float
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float
        Value used to replace outliers that are higher than threshold, by default 0.0
    method: str
        Method used to fill nan values, by default 'time'
        For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=valid_symbols, s_property="marketCap", **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_dividend(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to dividend yield

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
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
    maxnan: float
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float
        Value used to replace outliers that are higher than threshold, by default 0.0
    method: str
        Method used to fill nan values, by default 'time'
        For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=valid_symbols, s_property="dividendYield", **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def get_property(
    symbols: List[str] = None,
    portfolio_engine: PoEngine = None,
    prop: str = "marketCap",
    **kwargs,
) -> pd.DataFrame:
    """Optimize weighted according to property

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
    prop : str, optional
        Property to use for optimization, by default 'marketCap'
        Use `portfolio.po.get_properties() to get a list of available properties
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
    maxnan: float
        Maximum percentage of NaNs allowed in the data, by default 0.05
    threshold: float
        Value used to replace outliers that are higher than threshold, by default 0.0
    method: str
        Method used to fill nan values, by default 'time'
        For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0

    Returns
    -------
    Tuple[pd.DataFrame, Dict]
        Tuple with weights and performance dictionary
    """

    if prop is None:
        console.print("No property provided")
        return pd.DataFrame()

    valid_symbols, valid_portfolio_engine, valid_kwargs = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not valid_symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=valid_symbols, s_property=prop, **valid_kwargs
    )
    performance_dict = get_portfolio_performance(weights, returns, **valid_kwargs)

    valid_portfolio_engine.set_weights(weights=weights)
    valid_portfolio_engine.set_returns(returns=returns)

    return valid_portfolio_engine.get_weights_df(), performance_dict


@log_start_end(log=logger)
def show(
    portfolio_engine: PoEngine,
    category: str = None,
) -> Union[pd.DataFrame, pd.DataFrame]:
    """Show portfolio optimization results

    Parameters
    ----------
    portfolio_engine : PoEngine
        Portfolio optimization engine

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
        Portfolio weights and categories
    """

    weights = portfolio_engine.get_weights_df()

    if weights.empty:
        return pd.DataFrame()

    if category is not None:
        available_categories = portfolio_engine.get_available_categories()
        if not available_categories:
            console.print("No categories found.")
            return weights, pd.DataFrame()

        msg = ", ".join(available_categories)
        if category not in available_categories:
            console.print(f"Please specify a category from the following: {msg}")
            return weights, pd.DataFrame()

        category_df = portfolio_engine.get_category_df(category=category)
        return weights, category_df

    return weights, pd.DataFrame()
