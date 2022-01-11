from datetime import datetime
import os
from matplotlib import pyplot as plt, dates as mdates, ticker
import matplotlib
import numpy as np
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_close_price,
    get_exchange_balances,
    get_exchange_net_position_change,
    get_hashrate,
    get_non_zero_addresses,
)
from gamestonk_terminal import feature_flags as gtff


def display_btc_rainbow(since: int, until: int, export: str = ""):
    """Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    since : int
        Initial date timestamp. Default is initial BTC timestamp: 1_325_376_000
    until : int
        Final date timestamp. Default is current BTC timestamp
    """
    df_data = get_close_price("BTC", "24h", since, until)
    if df_data.empty:
        print("Error in glassnode request\n")
    else:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

        d0 = datetime.strptime("2012-01-01", "%Y-%m-%d")
        x = range((df_data.index[0] - d0).days, (df_data.index[-1] - d0).days + 1)

        y0 = [
            10 ** ((2.90 * ln_x) - 19.463) for ln_x in [np.log(val + 1400) for val in x]
        ]
        y1 = [
            10 ** ((2.886 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1375) for val in x]
        ]
        y2 = [
            10 ** ((2.872 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1350) for val in x]
        ]
        y3 = [
            10 ** ((2.859 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1320) for val in x]
        ]
        y4 = [
            10 ** ((2.8445 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1293) for val in x]
        ]
        y5 = [
            10 ** ((2.8295 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1275) for val in x]
        ]
        y6 = [
            10 ** ((2.815 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1250) for val in x]
        ]
        y7 = [
            10 ** ((2.801 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1225) for val in x]
        ]
        y8 = [
            10 ** ((2.788 * ln_x) - 19.463)
            for ln_x in [np.log(val + 1200) for val in x]
        ]
        ax.fill_between(df_data.index, y0, y1, color="red", alpha=0.7)
        ax.fill_between(df_data.index, y1, y2, color="orange", alpha=0.7)
        ax.fill_between(df_data.index, y2, y3, color="yellow", alpha=0.7)
        ax.fill_between(df_data.index, y3, y4, color="green", alpha=0.7)
        ax.fill_between(df_data.index, y4, y5, color="blue", alpha=0.7)
        ax.fill_between(df_data.index, y5, y6, color="violet", alpha=0.7)
        ax.fill_between(df_data.index, y6, y7, color="indigo", alpha=0.7)
        ax.fill_between(df_data.index, y7, y8, color="purple", alpha=0.7)

        ax.semilogy(df_data.index, df_data["v"].values, c="k", lw=1.2)
        ax.set_xlim(df_data.index[0], df_data.index[-1])
        ax.set_title("Bitcoin Rainbow Chart")
        ax.set_xlabel("Time")
        dateFmt = mdates.DateFormatter("%m/%d/%Y")
        ax.set_ylabel("Price ($)")
        ax.xaxis.set_major_formatter(dateFmt)
        ax.tick_params(axis="x", labelrotation=45)

        ax.legend(
            [
                "Bubble bursting imminent!!",
                "SELL!",
                "Everyone FOMO'ing....",
                "Is this a bubble??",
                "Still cheap",
                "Accumulate",
                "BUY!",
                "Basically a Fire Sale",
                "Bitcoin Price",
            ],
            prop={"size": 6},
        )

        sample_dates = np.array(
            [datetime(2012, 11, 28), datetime(2016, 7, 9), datetime(2020, 5, 11)]
        )
        sample_dates = mdates.date2num(sample_dates)
        ax.vlines(x=sample_dates, ymin=0, ymax=10 ** 5, color="grey")
        for i, x in enumerate(sample_dates):
            ax.text(x, 1, f"Halving {i+1}", rotation=-90, verticalalignment="center")

        ax.grid(alpha=0.2)
        ax.minorticks_off()
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, _: int(x) if x >= 1 else x)
        )
        ax.yaxis.set_major_locator(
            matplotlib.ticker.LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
        )

        if gtff.USE_ION:
            plt.ion()
        plt.show()
        print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rainbox",
            df_data,
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

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df_addresses,
    )


def display_non_zero_addresses(
    asset: str, since: int, until: int, interval: str, export: str = ""
) -> None:
    """Display addresses with non-zero balance of a certain asset
    [Source: https://glassnode.org]

    Parameters
    ----------
    asset : str
        Asset to search (e.g., BTC)
    since : int
        Initial date timestamp (e.g., 1_577_836_800)
    until : int
        End date timestamp (e.g., 1_609_459_200)
    interval : str
        Interval frequency (e.g., 24h)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_addresses = get_non_zero_addresses(asset, interval, since, until)

    if df_addresses.empty:
        print("Error in glassnode request")
    else:
        _, main_ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

        main_ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)
        main_ax.grid(True)

        main_ax.set_title(f"{asset} Addresses with non-zero balances")
        main_ax.set_ylabel("Number of Addresses")
        main_ax.set_xlabel("Date")
        main_ax.set_xlim(df_addresses.index[0], df_addresses.index[-1])

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "nonzero",
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

        if gtff.USE_ION:
            plt.ion()

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

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "eb",
        df_balance,
    )


def display_hashrate(
    asset: str,
    since: int,
    until: int,
    interval: str,
    export: str = "",
) -> None:
    """Display dataframe with mean hashrate of btc or eth blockchain and asset price.
    [Source: https://glassnode.org]

    Parameters
    ----------
    asset : str
        Blockchain to check mean hashrate (BTC or ETH)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = get_hashrate(asset, interval, since, until)

    if df.empty:
        print("Error in glassnode request")
    else:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        ax1.plot(df.index, df["hashrate"] / 1_000_000_000_000, c="k")
        ax2 = ax1.twinx()

        ax1.grid()
        ax2.plot(df.index, df["price"] / 1_000, c="orange")
        ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:.1f}k"))
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}T"))

        ax1.set_ylabel(f"{asset} hashrate (Terahashes/second)")
        ax2.set_ylabel(f"{asset} price [$]", c="orange")
        ax1.set_title(f"{asset}: Mean hashrate")
        ax1.set_xlim(df.index[0], df.index[-1])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hr",
        df,
    )
