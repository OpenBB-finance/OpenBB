""" Portfolio Optimization Helper Functions """
__docformat__ = "numpy"

from typing import List, Dict
import pandas as pd
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns


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


def process_stocks(list_of_stocks: List[str], period: str = "3mo") -> pd.DataFrame:
    """Get adjusted closing price for each stock in the list

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to get historical data for
    period: str
        Period to get data from yfinance

    Returns
    -------
    stock_closes: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """

    stock_prices = yf.download(
        list_of_stocks, period=period, progress=False, group_by="ticker"
    )
    stock_closes = pd.DataFrame(index=stock_prices.index)
    for stock in list_of_stocks:
        stock_closes[stock] = stock_prices[stock]["Adj Close"]
    return stock_closes


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
