""" Portfolio Optimization Functions"""
__docformat__ = "numpy"

import argparse
from typing import List

def optimize(list_of_stocks:List[str], other_args:List[str]):
    """

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to be included in optimization

    Returns
    -------
    weights : dict
        Dictionary of weights where keys are the tickers

    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="optimize",
    )

    parse

    weights = {}
    n_stocks = len(list_of_stocks)
    for stock in list_of_stocks:
        weights[stock] = round(1/n_stocks, 5)

    return weights

def equal_weight(list_of_stocks:List[str]):
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

