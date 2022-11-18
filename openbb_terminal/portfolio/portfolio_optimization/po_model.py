"""Optimization Model"""
__docformat__ = "numpy"

# pylint: disable=R0913, C0302, E1101, line-too-long
# flake8: noqa: E501

import logging
from typing import List, Optional, Tuple, Union
import warnings

import pandas as pd
from numpy.typing import NDArray
from numpy import floating
from riskfolio import rp

from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_model,
)
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.rich_config import console

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

PARAM_TYPES = {
    "interval": str,
    "start_date": str,
    "end_date": str,
    "log_returns": bool,
    "freq": str,
    "maxnan": float,
    "threshold": float,
    "method": str,
    "risk_measure": str,
    "objective": str,
    "risk_free_rate": float,
    "risk_aversion": float,
    "alpha": float,
    "target_return": float,
    "target_risk": float,
    "mean": str,
    "covariance": str,
    "d_ewma": float,
    "value": float,
    "value_short": float,
}


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
def get_maxsharpe(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize Sharpe ratio weights

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_sharpe(symbols=symbols, **parameters)

    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_minrisk(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Minimize risk

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_min_risk(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_maxutil(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize utility

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_util(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_maxret(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize return

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_ret(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_maxdiv(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize diversification

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_diversification_portfolio(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_maxdecorr(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize decorrelation

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_decorrelation_portfolio(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_blacklitterman(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Black-Litterman

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_black_litterman_portfolio(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_ef(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
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
    """Optimize with Efficient Frontier

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

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

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    frontier, mu, cov, returns, weights, X1, Y1, port = optimizer_model.get_ef(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return frontier, mu, cov, returns, weights, X1, Y1, port


@log_start_end(log=logger)
def get_riskparity(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_risk_parity_portfolio(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_relriskparity(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Relative Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_rel_risk_parity_portfolio(
        symbols=symbols, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_hrp(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Hierarchical Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_hrp(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_herc(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Hierarchical Equal Risk Contribution

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_herc(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_nco(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Non-Convex Optimization

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_nco(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_equal(
    portfolio_engine: PoEngine = None, symbols: List[str] = None, **kwargs
) -> pd.DataFrame:
    """Equally weighted portfolio, where weight = 1/# of symbols

    Parameters
    ----------
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    symbols : List[str], optional
        List of symbols, by default None
    interval : str, optional
        Interval to get data, by default "3y"
    start_date : str, optional
        If not using interval, start date string (YYYY-MM-DD), by default ""
    end_date : str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last weekday, by default ""
    log_returns : bool, optional
        If True use log returns, else arithmetic returns, by default False
    freq : str, optional
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
    pd.DataFrame
        DataFrame with equal weights

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.portfolio.po.equal(symbols=["AAPL", "MSFT", "AMZN"])

    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.po.load(symbols_file_path="50_30_10_10_Portfolio.xlsx")
    >>> openbb.portfolio.po.equal(portfolio_engine=p)
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_equal_weights(symbols=symbols, **parameters)
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_mktcap(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to market cap

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property="marketCap", **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_dividend(
    symbols: List[str] = None, portfolio_engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to dividend yield

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property="dividendYield", **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def get_property(
    symbols: List[str] = None,
    portfolio_engine: PoEngine = None,
    prop: str = None,
    **kwargs,
) -> pd.DataFrame:
    """Optimize weighted according to dividend yield

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    portfolio_engine : PoEngine, optional
        Portfolio optimization engine, by default None
    prop : str, optional
        Property to optimize on, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    if prop is None:
        console.print("No property provided")
        return pd.DataFrame()

    symbols, portfolio_engine, parameters = validate_inputs(
        symbols, portfolio_engine, kwargs
    )
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property=prop, **parameters
    )
    portfolio_engine.set_weights(weights=weights)
    portfolio_engine.set_returns(returns=returns)

    return portfolio_engine.get_weights_df()


@log_start_end(log=logger)
def show(
    portfolio_engine: PoEngine,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Show portfolio optimization results

    Parameters
    ----------
    portfolio_engine : PoEngine
        Portfolio optimization engine

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Tuple of DataFrames with portfolio optimization results
    """

    weights = portfolio_engine.get_weights_df()
    asset_class = portfolio_engine.get_category_df(category="ASSET_CLASS")
    country = portfolio_engine.get_category_df(category="COUNTRY")
    sector = portfolio_engine.get_category_df(category="SECTOR")
    industry = portfolio_engine.get_category_df(category="INDUSTRY")

    if all(
        [weights.empty, asset_class.empty, country.empty, sector.empty, industry.empty]
    ):
        console.print("No portfolio optimization results to show")

    return weights, asset_class, country, sector, industry
