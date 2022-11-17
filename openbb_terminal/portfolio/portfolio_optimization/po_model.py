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
from openbb_terminal.portfolio.portfolio_optimization.po_engine import PoEngine
from openbb_terminal.rich_config import console

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(
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
def file(
    parameters_file_path: str,
    engine: PoEngine,
):
    """Load portfolio optimization engine from file

    Parameters
    ----------
    parameters_file_path : str
        Parameters file path, by default None
    engine : PoEngine
        Portfolio optimization engine, by default None

    Returns
    -------
    Dict
        Parameters
    """

    engine.set_params_from_file(parameters_file_path)


def validate_inputs(
    symbols=None, engine=None, kwargs=None
) -> Tuple[List[str], PoEngine, dict]:
    """Check valid inputs

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None
    kwargs : dict
        Keyword arguments, by default None

    Returns
    -------
    Tuple[List[str], PoEngine, dict]
        List of symbols, Portfolio optimization engine, Keyword arguments
    """

    if symbols:
        engine = PoEngine(symbols=symbols)
        parameters = kwargs
    elif engine:
        symbols = engine.get_symbols()
        parameters = engine.get_params().copy()
        parameters.update(kwargs)
    else:
        console.print("No symbols or engine provided")

    return symbols, engine, parameters


@log_start_end(log=logger)
def get_maxsharpe(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize Sharpe ratio weights

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_sharpe(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_minrisk(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Minimize risk

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_min_risk(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_maxutil(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize utility

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_util(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_maxret(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize return

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_ret(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_maxdiv(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize diversification

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_diversification_portfolio(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_maxdecorr(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize decorrelation

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_max_decorrelation_portfolio(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_blacklitterman(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Black-Litterman

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_black_litterman_portfolio(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_ef(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
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
    engine : PoEngine, optional
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

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    frontier, mu, cov, returns, weights, X1, Y1, port = optimizer_model.get_ef(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return frontier, mu, cov, returns, weights, X1, Y1, port


@log_start_end(log=logger)
def get_riskparity(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_risk_parity_portfolio(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_relriskparity(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Relative Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_rel_risk_parity_portfolio(
        symbols=symbols, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_hrp(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Hierarchical Risk Parity

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_hrp(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_herc(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Hierarchical Equal Risk Contribution

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_herc(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_nco(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize with Non-Convex Optimization

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_nco(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_equal(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize equally weighted

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_equal_weights(symbols=symbols, **parameters)
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_mktcap(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to market cap

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property="marketCap", **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_dividend(
    symbols: List[str] = None, engine: PoEngine = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to dividend yield

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
        Portfolio optimization engine, by default None

    Returns
    -------
    pd.DataFrame
        DataFrame with equal weights
    """

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property="dividendYield", **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def get_property(
    symbols: List[str] = None, engine: PoEngine = None, prop: str = None, **kwargs
) -> pd.DataFrame:
    """Optimize weighted according to dividend yield

    Parameters
    ----------
    symbols : List[str], optional
        List of symbols, by default None
    engine : PoEngine, optional
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

    symbols, engine, parameters = validate_inputs(symbols, engine, kwargs)
    if not symbols:
        return pd.DataFrame()

    weights, returns = optimizer_model.get_property_weights(
        symbols=symbols, s_property=prop, **parameters
    )
    engine.set_weights(weights=weights)
    engine.set_returns(returns=returns)

    return engine.get_weights_df()


@log_start_end(log=logger)
def show(
    engine: PoEngine,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Show portfolio optimization results

    Parameters
    ----------
    engine : PoEngine
        Portfolio optimization engine

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Tuple of DataFrames with portfolio optimization results
    """

    weights = engine.get_weights_df()
    asset_class = engine.get_category_df(category="ASSET_CLASS")
    country = engine.get_category_df(category="COUNTRY")
    sector = engine.get_category_df(category="SECTOR")
    industry = engine.get_category_df(category="INDUSTRY")

    if all(
        [weights.empty, asset_class.empty, country.empty, sector.empty, industry.empty]
    ):
        console.print("No portfolio optimization results to show")

    return weights, asset_class, country, sector, industry
