import argparse
from typing import List, Dict
import requests
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def get_sentiment_stats(ticker: str) -> Dict:
    """Get sentiment stats

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats

    Returns
    -------
    Dict
        Get sentiment stats
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        return response.json()

    return {}


def sentiment_stats(other_args: List[str], ticker: str):
    """
    Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
    bullish vs bearish percentages, sector average bullish percentage, and sector average news score

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to get sentiment stats
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="stats",
        description="""
            Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
            bullish vs bearish percentages, sector average bullish percentage, and sector average news score.
            [Source: https://finnhub.io]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        d_stats = get_sentiment_stats(ticker)

        if d_stats:
            print(f"Buzz: {round(100*d_stats['buzz']['buzz'],2)} %")
            print(f"News Score: {round(100*d_stats['companyNewsScore'],2)} %")
            print("")
            print(f"Articles Last Week: {d_stats['buzz']['articlesInLastWeek']}")
            print(f"Articles Weekly Average: {d_stats['buzz']['weeklyAverage']}")
            print("")
            print(f"Bullish: {round(100*d_stats['sentiment']['bullishPercent'],2)} %")
            print(f"Bearish: {round(100*d_stats['sentiment']['bearishPercent'],2)} %")
            print("")
            print(
                f"Sector Average Bullish: {round(100*d_stats['sectorAverageBullishPercent'],2)} %"
            )
            print(
                f"Sector Average News Score: {round(100*d_stats['sectorAverageNewsScore'],2)} %"
            )
        else:
            print("No sentiment stats found.")
        print("")

    except Exception as e:
        print(e, "\n")
