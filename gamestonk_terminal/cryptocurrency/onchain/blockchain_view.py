"""Blockchain View"""
__docformat__ = "numpy"

import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import ticker, dates as mdates
from gamestonk_terminal.cryptocurrency.onchain import blockchain_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    long_number_format,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI


def display_btc_circulating_supply(since: int, until: int, export: str) -> None:
    """Returns BTC circulating supply [Source: https://api.blockchain.info/]

    Parameters
    ----------
    since : int
        Initial date timestamp (e.g., 1_609_459_200)
    until : int
        End date timestamp (e.g., 1_641_588_030)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = blockchain_model.get_btc_circulating_supply()
    df = df[
        (df["x"] > datetime.fromtimestamp(since))
        & (df["x"] < datetime.fromtimestamp(until))
    ]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(df["x"], df["y"])
    ax.set_xlabel("Time")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlim(df["x"].iloc[0], df["x"].iloc[-1])
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    fig.tight_layout(pad=4)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_ylabel("BTC")
    ax.grid(alpha=0.5)
    ax.set_title("BTC Circulating Supply")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: long_number_format(x))
    )

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btccp",
        df,
    )


def display_btc_confirmed_transactions(since: int, until: int, export: str) -> None:
    """Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

    Parameters
    ----------
    since : int
        Initial date timestamp (e.g., 1_609_459_200)
    until : int
        End date timestamp (e.g., 1_641_588_030)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = blockchain_model.get_btc_confirmed_transactions()
    df = df[
        (df["x"] > datetime.fromtimestamp(since))
        & (df["x"] < datetime.fromtimestamp(until))
    ]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(df["x"], df["y"], lw=0.8)
    ax.set_xlabel("Time")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlim(df["x"].iloc[0], df["x"].iloc[-1])
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    fig.tight_layout(pad=4)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_ylabel("Transactions")
    ax.grid(alpha=0.5)
    ax.set_title("BTC Confirmed Transactions")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: long_number_format(x))
    )

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btcct",
        df,
    )
