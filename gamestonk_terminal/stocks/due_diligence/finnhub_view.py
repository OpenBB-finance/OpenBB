import argparse
from typing import List
import requests
import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def get_rating_over_time(ticker: str) -> pd.DataFrame:
    """Get rating over time

    Parameters
    ----------
    ticker : str
        Ticker to get ratings from

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/stock/recommendation?symbol={ticker}&token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        return pd.DataFrame(response.json())

    return pd.DataFrame()


def plot_rating_over_time(rot: pd.DataFrame, ticker: str):
    """Plot rating over time

    Parameters
    ----------
    rot : pd.DataFrame
        Rating over time
    ticker : str
        Ticker associated with ratings

    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    rot.sort_values("period", inplace=True)
    plt.plot(pd.to_datetime(rot["period"]), rot["strongBuy"], c="green", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["buy"], c="lightgreen", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["hold"], c="grey", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["sell"], c="pink", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["strongSell"], c="red", lw=3)
    plt.xlim(
        pd.to_datetime(rot["period"].values[0]),
        pd.to_datetime(rot["period"].values[-1]),
    )
    plt.grid()
    plt.title(f"{ticker}'s ratings over time")
    plt.xlabel("Time")
    plt.ylabel("Rating")
    plt.legend(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def rating_over_time(other_args: List[str], ticker: str):
    """Rating over time

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to get ratings from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="rot",
        description="""
            Rating over time. [Source: https://finnhub.io]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_rot = get_rating_over_time(ticker)

        if df_rot.empty:
            print("No ratings over time found\n")
            return

        plot_rating_over_time(df_rot, ticker)
        print("")

    except Exception as e:
        print(e, "\n")
