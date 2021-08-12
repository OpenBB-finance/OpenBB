"""Tradingview model"""
__docformat__ = "numpy"

import requests
from tradingview_ta import TA_Handler
import pandas as pd

from gamestonk_terminal import config_terminal as cfg

INTERVALS = {
    "1m": "1 min",
    "5m": "5 min",
    "15m": "15 min",
    "1h": "1 hour",
    "4h": "4 hours",
    "1d": "1 day",
    "1W": "1 week",
    "1M": "1 month",
}


def get_tradingview_recommendation(
    ticker: str, screener: str, exchange: str, interval: str
) -> str:
    """Get tradingview recommendation based on technical indicators

    Parameters
    ----------
    ticker : str
        Ticker to get the recommendation from tradingview based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation

    Returns
    -------
    str
        tradingview recommendation based on technical indicators
    """

    if not exchange:
        s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
        result = requests.get(s_req, stream=True)
        exchange = result.json()["Exchange"]

    if not interval:
        df_recommendation = pd.DataFrame()
        index_recommendation = list()
        for interv in ["1M", "1W", "1d", "4h", "1h", "15m", "5m", "1m"]:
            # If the returned data was successful
            if result.status_code == 200:
                stock_recommendation = TA_Handler(
                    symbol=ticker,
                    screener=screener,
                    exchange=exchange,
                    interval=interv,
                )
                d_recommendation = stock_recommendation.get_analysis().summary
                df_recommendation = df_recommendation.append(
                    d_recommendation, ignore_index=True
                )
                index_recommendation.append(INTERVALS[interv])
            df_recommendation.index = index_recommendation
            df_recommendation[["BUY", "NEUTRAL", "SELL"]] = df_recommendation[
                ["BUY", "NEUTRAL", "SELL"]
            ].astype(int)
        df_recommendation["-----"] = "-----"
        df_recommendation.index.name = "Interval"
        recommendation = df_recommendation[
            ["RECOMMENDATION", "-----", "BUY", "NEUTRAL", "SELL"]
        ].to_string()

    else:
        stock_recommendation = TA_Handler(
            symbol=ticker, screener=screener, exchange=exchange, interval=interval
        )
        d_recommendation = stock_recommendation.get_analysis().summary
        recommendation = f"Interval: {INTERVALS[interval]}\n"
        recommendation += f"Recommendation: {d_recommendation['RECOMMENDATION']}\n"
        recommendation += f"{int(d_recommendation['BUY'])} BUY, {int(d_recommendation['NEUTRAL'])} NEUTRAL"
        recommendation += f", {int(d_recommendation['SELL'])} SELL"

    return recommendation
