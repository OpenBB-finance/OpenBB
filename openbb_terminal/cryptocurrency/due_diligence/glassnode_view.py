import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib
import numpy as np
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.lines import Line2D

from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key
from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_close_price,
    get_exchange_balances,
    get_exchange_net_position_change,
    get_hashrate,
    get_non_zero_addresses,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_btc_rainbow(
    since: int,
    until: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    since : int
        Initial date timestamp. Default is initial BTC timestamp: 1_325_376_000
    until : int
        Final date timestamp. Default is current BTC timestamp
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_data = get_close_price("BTC", "24h", since, until)

    if df_data.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    d0 = datetime.strptime("2012-01-01", "%Y-%m-%d")
    x = range((df_data.index[0] - d0).days, (df_data.index[-1] - d0).days + 1)

    y0 = [10 ** ((2.90 * ln_x) - 19.463) for ln_x in [np.log(val + 1400) for val in x]]
    y1 = [10 ** ((2.886 * ln_x) - 19.463) for ln_x in [np.log(val + 1375) for val in x]]
    y2 = [10 ** ((2.872 * ln_x) - 19.463) for ln_x in [np.log(val + 1350) for val in x]]
    y3 = [10 ** ((2.859 * ln_x) - 19.463) for ln_x in [np.log(val + 1320) for val in x]]
    y4 = [
        10 ** ((2.8445 * ln_x) - 19.463) for ln_x in [np.log(val + 1293) for val in x]
    ]
    y5 = [
        10 ** ((2.8295 * ln_x) - 19.463) for ln_x in [np.log(val + 1275) for val in x]
    ]
    y6 = [10 ** ((2.815 * ln_x) - 19.463) for ln_x in [np.log(val + 1250) for val in x]]
    y7 = [10 ** ((2.801 * ln_x) - 19.463) for ln_x in [np.log(val + 1225) for val in x]]
    y8 = [10 ** ((2.788 * ln_x) - 19.463) for ln_x in [np.log(val + 1200) for val in x]]

    ax.fill_between(df_data.index, y0, y1, color="red", alpha=0.7)
    ax.fill_between(df_data.index, y1, y2, color="orange", alpha=0.7)
    ax.fill_between(df_data.index, y2, y3, color="yellow", alpha=0.7)
    ax.fill_between(df_data.index, y3, y4, color="green", alpha=0.7)
    ax.fill_between(df_data.index, y4, y5, color="blue", alpha=0.7)
    ax.fill_between(df_data.index, y5, y6, color="violet", alpha=0.7)
    ax.fill_between(df_data.index, y6, y7, color="indigo", alpha=0.7)
    ax.fill_between(df_data.index, y7, y8, color="purple", alpha=0.7)

    ax.semilogy(df_data.index, df_data["v"].values)
    ax.set_xlim(df_data.index[0], df_data.index[-1])
    ax.set_title("Bitcoin Rainbow Chart")
    ax.set_ylabel("Price ($)")

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
        prop={"size": 8},
    )

    sample_dates = np.array(
        [datetime(2012, 11, 28), datetime(2016, 7, 9), datetime(2020, 5, 11)]
    )
    sample_dates = mdates.date2num(sample_dates)
    ax.vlines(x=sample_dates, ymin=0, ymax=10**5, color="grey")
    for i, x in enumerate(sample_dates):
        ax.text(x, 1, f"Halving {i+1}", rotation=-90, verticalalignment="center")

    ax.minorticks_off()
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: int(x) if x >= 1 else x)
    )
    ax.yaxis.set_major_locator(
        matplotlib.ticker.LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
    )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rainbox",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_active_addresses(
    asset: str,
    since: int,
    until: int,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_active_addresses(asset, interval, since, until)

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)

    ax.set_title(f"Active {asset} addresses over time")
    ax.set_ylabel("Addresses [thousands]")
    ax.set_xlim(df_addresses.index[0], df_addresses.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df_addresses,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_non_zero_addresses(
    asset: str,
    since: int,
    until: int,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_non_zero_addresses(asset, interval, since, until)

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)

    ax.set_title(f"{asset} Addresses with non-zero balances")
    ax.set_ylabel("Number of Addresses")
    ax.set_xlim(df_addresses.index[0], df_addresses.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "nonzero",
        df_addresses,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_exchange_net_position_change(
    asset: str,
    exchange: str,
    since: int,
    until: int,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_exchange_net_position_change(
        asset, exchange, interval, since, until
    )

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.fill_between(
        df_addresses[df_addresses["v"] < 0].index,
        df_addresses[df_addresses["v"] < 0]["v"].values / 1e3,
        np.zeros(len(df_addresses[df_addresses["v"] < 0])),
        facecolor=theme.down_color,
    )
    ax.fill_between(
        df_addresses[df_addresses["v"] >= 0].index,
        df_addresses[df_addresses["v"] >= 0]["v"].values / 1e3,
        np.zeros(len(df_addresses[df_addresses["v"] >= 0])),
        facecolor=theme.up_color,
    )

    ax.set_ylabel(f"30d change of {asset} supply held in exchange wallets [thousands]")
    ax.set_title(
        f"{asset}: Exchange Net Position Change - {'all exchanges' if exchange == 'aggregated' else exchange}"
    )
    ax.set_xlim(df_addresses.index[0], df_addresses.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "change",
        df_addresses,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_exchange_balances(
    asset: str,
    exchange: str,
    since: int,
    until: int,
    interval: str,
    percentage: bool,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_balance = get_exchange_balances(asset, exchange, interval, since, until)

    if df_balance.empty:
        return

    # This plot has 2 axis
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        ax2 = ax1.twinx()

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax1, ax2) = external_axes

    if percentage:
        ax1.plot(df_balance.index, df_balance["percentage"] * 100)
    else:
        ax1.plot(df_balance.index, df_balance["stacked"] / 1000)

    ax1.set_ylabel(f"{asset} units [{'%' if percentage else 'thousands'}]")
    ax1.set_title(
        f"{asset}: Total Balance in {'all exchanges' if exchange == 'aggregated' else exchange}"
    )
    ax1.tick_params(axis="x", labelrotation=10)
    ax1.legend(["ETH Unit"], loc="best")

    ax2.grid(visible=False)
    ax2.plot(df_balance.index, df_balance["price"], color="orange")
    ax2.set_ylabel(f"{asset} price [$]")
    ax2.legend(["ETH Price"], loc="best")

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "eb",
        df_balance,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_hashrate(
    asset: str,
    since: int,
    until: int,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = get_hashrate(asset, interval, since, until)

    if df.empty:
        return

    # This plot has 2 axis
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        ax2 = ax1.twinx()

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.plot(
        df.index, df["hashrate"] / 1_000_000_000_000, color=theme.down_color, lw=0.8
    )
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}T"))
    ax1.set_ylabel(f"{asset} hashrate (Terahashes/second)")
    ax1.set_title(f"{asset}: Mean hashrate")
    ax1.tick_params(axis="x", labelrotation=10)

    ax2.set_xlim(left=df.index[0])
    ax2.grid(visible=False)
    ax2.plot(df.index, df["price"] / 1_000, color=theme.up_color, lw=0.8)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:.1f}k"))
    ax2.set_ylabel(f"{asset} price [$]")

    # Manually construct the chart legend
    lines = [
        Line2D([0], [0], color=color) for color in [theme.up_color, theme.down_color]
    ]
    labels = ["Hash Rate", "Price"]
    ax2.legend(lines, labels)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hr",
        df,
    )
