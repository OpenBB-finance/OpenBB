import os
from matplotlib import pyplot as plt, dates as mdates
import numpy as np
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_exchange_balances,
    get_exchange_net_position_change,
)


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
    until : int
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
        _, main_ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

        main_ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)
        main_ax.grid(True)

        main_ax.set_title(f"Active {asset} addresses over time")
        main_ax.set_ylabel("Addresses [thousands]")
        main_ax.set_xlabel("Date")
        main_ax.set_xlim(df_addresses.index[0], df_addresses.index[-1])

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.gcf().autofmt_xdate()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df_addresses,
    )


def display_exchange_net_position_change(
    asset: str, exchange: str, since: int, until: int, interval: str, export: str = ""
) -> None:
    """Display 30d change of the supply held in exchange wallets.
    [Source: https://glassnode.org]

    Parameters
    ----------
    asset : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_addresses = get_exchange_net_position_change(
        asset, exchange, interval, since, until
    )

    if df_addresses.empty:
        print("Error in glassnode request")
    else:
        _, ax1 = plt.subplots(figsize=(25, 7))

        ax1.grid()

        ax1.fill_between(
            df_addresses[df_addresses["v"] < 0].index,
            df_addresses[df_addresses["v"] < 0]["v"].values / 1e3,
            np.zeros(len(df_addresses[df_addresses["v"] < 0])),
            facecolor="red",
        )
        ax1.fill_between(
            df_addresses[df_addresses["v"] >= 0].index,
            df_addresses[df_addresses["v"] >= 0]["v"].values / 1e3,
            np.zeros(len(df_addresses[df_addresses["v"] >= 0])),
            facecolor="green",
        )

        ax1.set_ylabel(
            f"30d change of {asset} supply held in exchange wallets [thousands]"
        )
        ax1.set_title(
            f"{asset}: Exchange Net Position Change - {'all exchanges' if exchange == 'aggregated' else exchange}"
        )
        ax1.set_xlim(df_addresses.index[0], df_addresses.index[-1])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()

        plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "change",
        df_addresses,
    )


def display_exchange_balances(
    asset: str,
    exchange: str,
    since: int,
    until: int,
    interval: str,
    percentage: bool,
    export: str = "",
) -> None:
    """Display total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.org]

    Parameters
    ----------
    asset : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)
    percentage : bool
        Show percentage instead of stacked value.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_balance = get_exchange_balances(asset, exchange, interval, since, until)

    if df_balance.empty:
        print("Error in glassnode request")
    else:
        _, ax1 = plt.subplots(figsize=(25, 7))
        if percentage:
            ax1.plot(df_balance.index, df_balance["percentage"] * 100, c="k")
        else:
            ax1.plot(df_balance.index, df_balance["stacked"] / 1000, c="k")

        ax2 = ax1.twinx()

        ax1.grid()
        ax2.plot(df_balance.index, df_balance["price"], c="orange")

        ax1.set_ylabel(f"{asset} units [{'%' if percentage else 'thousands'}]")
        ax2.set_ylabel(f"{asset} price [$]", c="orange")
        ax1.set_title(
            f"{asset}: Total Balance in {'all exchanges' if exchange == 'aggregated' else exchange}"
        )
        ax1.set_xlim(df_balance.index[0], df_balance.index[-1])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "eb",
        df_balance,
    )
