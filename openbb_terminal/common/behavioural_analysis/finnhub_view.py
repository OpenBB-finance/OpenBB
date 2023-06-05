"""Finnhub View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.common.behavioural_analysis import finnhub_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def display_sentiment_stats(
    ticker: str, export: str = "", sheet_name: Optional[str] = None
):
    """
    Prints Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
    bullish vs bearish percentages, sector average bullish percentage, and sector average news score

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats
    export : str
        Format to export data
    """
    d_stats = finnhub_model.get_sentiment_stats(ticker)
    print(d_stats)

    if d_stats.empty:
        return

    if d_stats:
        console.print(
            f"""
Buzz: {round(100*d_stats['buzz']['buzz'],2)} %
News Score: {round(100*d_stats['companyNewsScore'],2)} %

Articles Last Week: {d_stats['buzz']['articlesInLastWeek']}
Articles Weekly Average: {d_stats['buzz']['weeklyAverage']}

Bullish: {round(100*d_stats['sentiment']['bullishPercent'],2)} %
Bearish: {round(100*d_stats['sentiment']['bearishPercent'],2)} %

Sector Average Bullish: {round(100*d_stats['sectorAverageBullishPercent'],2)}
Sector Average News Score: {round(100*d_stats['sectorAverageNewsScore'],2)} %"""
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "stats",
            pd.DataFrame(d_stats),
            sheet_name,
        )

    else:
        console.print("No sentiment stats found.")
