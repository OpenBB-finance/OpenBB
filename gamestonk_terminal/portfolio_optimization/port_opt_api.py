""" Portfolio Optimization Functions"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns


def equal_weight(list_of_stocks: List[str], other_args: List[str]):
    """
    Equally weighted portfolio, where weight = 1/# of stocks

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to be included in optimization

    Returns
    -------
    weights : dict
        Dictionary of weights where keys are the tickers

    """
    weights = {}
    n_stocks = len(list_of_stocks)
    for stock in list_of_stocks:
        weights[stock] = round(1 / n_stocks, 5)

    return weights


def property_weighting(
    list_of_stocks: List[str], property_type: str, other_args: List[str]
):
    """
    Property weighted portfolio where each weight is the relative fraction.  Examples
    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to be included in optimization
    property_type: str
        Property to weight by.  Can be anything in yfinance.Ticker().info.  Examples:
            "marketCap", "dividendYield", etc

    Returns
    -------
    weights: dict
        Dictionary of weights where keys are the tickers
    """
    weights = {}
    prop = {}
    prop_sum = 0

    for stock in list_of_stocks:
        stock_prop = yf.Ticker(stock).info["marketCap"]
        prop[stock] = stock_prop
        prop_sum += stock_prop
    for k, v in prop.items():
        weights[k] = round(v / prop_sum, 5)

    return weights


def max_sharpe(list_of_stocks: List[str], other_args: List[str]):
    """
    Return a portfolio that maximizes the sharpe ratio.  Currently defaulting to 3m of historical data
    Parameters
    ----------
    list_of_stocks: List[str]
        List of the stocks to be included in the weights

    Returns
    -------
    weights: dict
        Dictionary of weights where keys are the tickers.
    """

    df = yf.download(list_of_stocks, period="3mo", group_by="ticker")
    df1 = pd.DataFrame(index=df.index)
    # process df
    for stock in list_of_stocks:
        df1[stock] = df[stock]["Adj Close"]

    mu = expected_returns.mean_historical_return(df1)
    S = risk_models.sample_cov(df1)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    ef.portfolio_performance(verbose=True)
    return weights
