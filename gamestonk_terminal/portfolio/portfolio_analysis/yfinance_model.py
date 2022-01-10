"""Yfinance model"""
__docformat__ = "numpy"

import difflib
import yfinance as yf
from gamestonk_terminal.stocks.sector_industry_analysis import financedatabase_model


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
