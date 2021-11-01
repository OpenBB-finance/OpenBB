import os
from matplotlib import pyplot as plt
from gamestonk_terminal.cryptocurrency.onchain.glassnode_model import (
    get_active_addresses,
)
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import config_plot as cfgPlot


def display_active_addresses(
    asset: str, since: int, until: int, interval: str, export: str = ""
) -> None:
    """Display active addresses of a certain asset over time
    [Source: https://glassnode.org]

    Parameters
    ----------
    asset : str
        Asset to search active addresses (e.g., BTC)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : str
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_addresses = get_active_addresses(asset, interval, since, until)

    if df_addresses.empty:
        print("Error in glassnode request")
    else:
        plot_data(df_addresses, asset)
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df_addresses,
    )


def plot_data(df, asset):
    _, main_ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

    main_ax.plot(df["t"], df["v"], linewidth=0.5)
    main_ax.grid(True)

    main_ax.set_title(f"Active {asset} addresses over time")
    main_ax.set_ylabel("Addresses")
    main_ax.set_xlabel("Date")

    plt.show()
