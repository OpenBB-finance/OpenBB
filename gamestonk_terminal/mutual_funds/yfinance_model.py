"""Yahoo Finance Mutual Fund Model"""
__docformat__ = "numpy"

from typing import Dict

import yfinance as yf


def get_information(fund: str) -> Dict:
    """Get fund information for fund symbol

    Parameters
    ----------
    fund : str
        Symbol of fund

    Returns
    -------
    dict
        Dictionary containing fund information
    """
    return yf.Ticker(fund).info
