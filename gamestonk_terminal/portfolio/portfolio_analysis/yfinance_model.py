"""Yfinance model"""
__docformat__ = "numpy"

from typing import List
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd


def get_country(ticker):
    country = "NA"
    data = yf.utils.get_json(f"https://finance.yahoo.com/quote/{ticker}")

    if "summaryProfile" in data:
        country = data["summaryProfile"]["country"]
        if self.country not in financedatabase_model.get_countries():
            similar_cmd = difflib.get_close_matches(
                country,
                financedatabase_model.get_countries(),
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                country = similar_cmd[0]
    return country
