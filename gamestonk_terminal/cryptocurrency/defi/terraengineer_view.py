"""Terra Engineer View"""
__docformat__ = "numpy"

import os
import matplotlib.pyplot as plt
from matplotlib import ticker, dates as mdates
from gamestonk_terminal.cryptocurrency.defi import terraengineer_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    long_number_format,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI


def display_terra_asset_history(
    asset: str = "", address: str = "", export: str = ""
) -> None:
    """Displays the 30-day history of specified asset in terra address
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terraengineer_model.get_history_asset_from_terra_address(
        address=address, asset=asset
    )

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(df["x"], df["y"])
    ax.set_xlabel("Time")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlim(df["x"].iloc[0], df["x"].iloc[-1])
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    fig.tight_layout(pad=4)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_ylabel(f"{asset.upper()} Amount")
    ax.grid(alpha=0.5)
    ax.set_title(f"{asset.upper()} Amount in Address {address}")
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
        "aterra",
        df,
    )


def display_anchor_yield_reserve(export: str = "") -> None:
    """Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terraengineer_model.get_history_asset_from_terra_address(
        address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
    )

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(df["x"], df["y"])
    ax.set_xlabel("Time")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlim(df["x"].iloc[0], df["x"].iloc[-1])
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    fig.tight_layout(pad=4)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_ylabel("UST Amount")
    ax.grid(alpha=0.5)
    ax.set_title("Anchor UST Yield Reserve")
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
        "ayr",
        df,
    )
