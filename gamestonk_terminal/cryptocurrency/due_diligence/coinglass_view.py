import os
from matplotlib import pyplot as plt, dates as mdates
import pandas as pd

from gamestonk_terminal.cryptocurrency.due_diligence.coinglass_model import (
    get_open_interest_per_exchange,
)
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_open_interest(symbol: str, interval: int, export: str) -> None:
    """Displays open interest by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    interval : int
        Interval frequency (e.g., 0)
    export : str
        Export dataframe data to csv,json,xlsx file"""
    df = get_open_interest_per_exchange(symbol, interval)
    if df.empty:
        console.print("Error in coinglass request")
    else:
        plot_data(df, symbol)
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi",
        df,
    )


def plot_data(df: pd.DataFrame, symbol: str):
    df_price = df[["price"]].copy()

    df_without_price = df.drop("price", 1)
    _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    plt.plot(df_without_price.index, df_without_price / 1e9)
    plt.legend(df_without_price.columns)
    ax2 = ax1.twinx()
    plt.grid()
    plt.plot(df_price.index, df_price, lw=3, c="k")
    plt.legend([f"{symbol} price"], loc=1)

    ax1.set_ylabel(
        "Estimated notional value of all open futures positions [$ billions]"
    )
    ax2.set_ylabel(f"{symbol} Price [$]")

    plt.xlim([df_price.index[0], df_price.index[-1]])
    plt.title(f"Exchange {symbol} Futures Open Interest")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    plt.show()
