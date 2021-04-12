""" Portfolio Optimization Functions"""
__docformat__ = "numpy"

import argparse
from typing import List
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

def equal_weight(list_of_stocks:List[str], other_args:List[str]):
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

def market_cap_weighting(list_of_stocks:List[str], other_args:List[str]):
    """
    Market cap weighted portfolio where each weight is the stocks market cap/ sum of all market caps
    Parameters
    ----------
    list_of_stocks: List[str[
        List of tickers to be included in optimization

    Returns
    -------
    weights: dict
        Dictionary of weights where keys are the tickers
    """
    weights = {}
    mkt_cap = {}
    total_cap = 0
    for stock in list_of_stocks:
        stock_cap = yf.Ticker(stock).info["marketCap"]
        mkt_cap[stock] = stock_cap
        total_cap += stock_cap
    for k,v in mkt_cap.items():
        weights[k] = round(v/total_cap,5)

    return weights
