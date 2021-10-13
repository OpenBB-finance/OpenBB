"""Optimization Model"""
__docformat__ = "numpy"

from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models
from gamestonk_terminal.portfolio.portfolio_optimization import yahoo_finance_model


def get_equal_weights(stocks: List[str], value: float = 1.0) -> Dict:
    """Equally weighted portfolio, where weight = 1/# of stocks

    Parameters
    ----------
    stocks: List[str]
        List of tickers to be included in optimization
    value : float
        Amount of money to allocate instead of percentage

    Returns
    -------
    dict
        Dictionary of weights where keys are the tickers
    """
    return {stock: value * round(1 / len(stocks), 5) for stock in stocks}


def get_property_weights(
    stocks: List[str], s_property: str, value: float = 1.0
) -> Dict:
    """Calculate portfolio weights based on selected property

    Parameters
    ----------
    stocks : List[str]
        List of portfolio stocks
    s_property : str
        Property to weight portfolio by
    value : float, optional
        Amount of money to allocate

    Returns
    -------
    Dict
        Dictionary of portfolio weights or allocations
    """
    prop = {}
    prop_sum = 0
    for stock in stocks:
        stock_prop = yf.Ticker(stock).info[s_property]
        if stock_prop is None:
            stock_prop = 0
        prop[stock] = stock_prop
        prop_sum += stock_prop

    if prop_sum == 0:
        print(f"No {s_property} was found on list of tickers provided", "\n")
        return {}

    return {k: value * v / prop_sum for k, v in prop.items()}


def get_maxsharpe_portfolio(
    stocks: List[str], period: str, rfrate: float
) -> Tuple[Dict, EfficientFrontier]:
    """Generate weights for max sharpe portfolio

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str, optional
        Period to get stock data, by default "3mo"
    rfrate : float, optional
        Risk free rate, by default 0.02

    Returns
    -------
    Dict
        Dictionary of tickers and weights
    EfficientFrontier
        EfficientFrontier object
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    ef = prepare_efficient_frontier(stock_prices)
    return dict(ef.max_sharpe(rfrate)), ef


def get_minvol_portfolio(
    stocks: List[str], period: str = "3mo"
) -> Tuple[Dict, EfficientFrontier]:
    """Generate weights for minimum voltaility portfolio

    Parameters
    ----------
    stocks : List[str]
        List of portfolio tickers
    period : str, optional
        Period to get stock data, by default "3mo"

    Returns
    -------
    Dict
        Dictionary of tickers and weights
    EfficientFrontier
        EfficientFrontier object
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    ef = prepare_efficient_frontier(stock_prices)
    return dict(ef.min_volatility()), ef


def get_maxquadutil_portfolio(
    stocks: List[str],
    period: str = "3mo",
    risk_aversion: float = 1.0,
    market_neutral: bool = False,
) -> Tuple[Dict, EfficientFrontier]:
    """Get portfolio maximizing quadratic ultility at a given risk aversion

    Parameters
    ----------
    stocks : List[str]
        List of portfolio stocks
    period : str, optional
        Period to get stock data, by default "3mo"
    risk_aversion : float, optional
        Risk aversion level, by default 1.0
    market_neutral : bool, optional
        Whether portfolio is market neutral, by default False

    Returns
    -------
    Dict
        Dictionary of portfolio weights
    EfficientFrontier
        EfficientFrontier object
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    ef = prepare_efficient_frontier(stock_prices)
    return ef.max_quadratic_utility(risk_aversion, market_neutral), ef


def get_efficient_risk_portfolio(
    stocks: List[str],
    period: str = "3mo",
    target_vol: float = 0.1,
    market_neutral: bool = False,
) -> Tuple[Dict, EfficientFrontier]:
    """Get portfolio that maximizes returns at given volatility

    Parameters
    ----------
    stocks : List[str]
        List of portfolio stocks
    period : str, optional
        Period to get stock data, by default "3mo"
    target_vol : float, optional
        Target volatility level, by default 0.1
    market_neutral : bool, optional
        Whether portfolio is market neutral, by default False

    Returns
    -------
    Dict
        Dictionary of weights
    EfficientFrontier
        Efficient Frontier object
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    ef = prepare_efficient_frontier(stock_prices)
    return ef.efficient_risk(target_vol, market_neutral), ef


def get_efficient_return_portfolio(
    stocks: List[str],
    period: str = "3mo",
    target_return: float = 0.1,
    market_neutral: bool = False,
) -> Tuple[Dict, EfficientFrontier]:
    """Get portfolio that minimizes volatility at given return

    Parameters
    ----------
    stocks : List[str]
        List of portfolio stocks
    period : str, optional
        Period to get stock data, by default "3mo"
    target_return : float, optional
        Target return level, by default 0.1
    market_neutral : bool, optional
        Whether portfolio is market neutral, by default False

    Returns
    -------
    Dict
        Dictionary of weights
    EfficientFrontier
        Efficient Frontier object
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    ef = prepare_efficient_frontier(stock_prices)
    return ef.efficient_return(target_return, market_neutral), ef


def prepare_efficient_frontier(stock_prices: pd.DataFrame):
    """Take in a dataframe of prices and return an efficient frontier object

    Parameters
    ----------
    stock_prices : DataFrame
        DataFrame where indices are DateTime and columns are stocks

    Returns
    -------
    EfficientFrontier
        EfficientFrontier object
    """

    mu = expected_returns.mean_historical_return(stock_prices)
    S = risk_models.sample_cov(stock_prices)
    return EfficientFrontier(mu, S)


def generate_random_portfolios(
    stocks: List[str], period: str = "3mo", n_portfolios: int = 300
):
    """[summary]

    Parameters
    ----------
    stocks : List[str]
        [description]
    period : str, optional
        [description], by default "3mo"
    n_portfolios : int, optional
        [description], by default 300
    """
    stock_prices = yahoo_finance_model.process_stocks(stocks, period)
    mu = expected_returns.mean_historical_return(stock_prices)
    S = risk_models.sample_cov(stock_prices)
    ef = EfficientFrontier(mu, S)

    # Generate random portfolios
    n_samples = n_portfolios
    w = np.random.dirichlet(np.ones(len(mu)), n_samples)
    rets = w.dot(mu)
    stds = np.sqrt(np.diag(w @ S @ w.T))

    return ef, rets, stds
