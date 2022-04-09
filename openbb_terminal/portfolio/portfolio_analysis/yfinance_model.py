"""Yfinance model"""
__docformat__ = "numpy"

import difflib
import logging

import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.sector_industry_analysis import financedatabase_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_country(ticker):
    country = "NA"
    data = yf.utils.get_json(f"https://finance.yahoo.com/quote/{ticker}")

    if "summaryProfile" in data:
        country = data["summaryProfile"]["country"]
        if country not in financedatabase_model.get_countries():
            similar_cmd = difflib.get_close_matches(
                country,
                financedatabase_model.get_countries(),
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                country = similar_cmd[0]
    return country
