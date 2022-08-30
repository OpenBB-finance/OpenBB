import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import matplotlib
import numpy as np
import pandas as pd
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
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_btc_rainbow(
    start_date: int = int(datetime(2010, 1, 1).timestamp()),
    end_date: int = int(datetime.now().timestamp()),
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : int
        Initial date timestamp. Default is initial BTC timestamp: 1_325_376_000
    end_date : int
        Final date timestamp. Default is current BTC timestamp
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_data = get_close_price("BTC", start_date, end_date)

    if df_data.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    d0 = datetime.strptime("2012-01-01", "%Y-%m-%d")
    dend = datetime.fromtimestamp(end_date)

    x = range((df_data.index[0] - d0).days, (dend - d0).days + 1)

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

    x_dates = pd.date_range(df_data.index[0], dend, freq="d")

    ax.fill_between(x_dates, y0, y1, color="red", alpha=0.7)
    ax.fill_between(x_dates, y1, y2, color="orange", alpha=0.7)
    ax.fill_between(x_dates, y2, y3, color="yellow", alpha=0.7)
    ax.fill_between(x_dates, y3, y4, color="green", alpha=0.7)
    ax.fill_between(x_dates, y4, y5, color="blue", alpha=0.7)
    ax.fill_between(x_dates, y5, y6, color="violet", alpha=0.7)
    ax.fill_between(x_dates, y6, y7, color="indigo", alpha=0.7)
    ax.fill_between(x_dates, y7, y8, color="purple", alpha=0.7)

    ax.semilogy(df_data.index, df_data["v"].values)
    ax.set_xlim(df_data.index[0], dend)
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
        [
            datetime(2012, 11, 28),
            datetime(2016, 7, 9),
            datetime(2020, 5, 11),
            datetime(2024, 4, 4),
        ]
    )
    sample_dates = mdates.date2num(sample_dates)
    ax.vlines(x=sample_dates, ymin=0, ymax=max(y0), color="grey")
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
    symbol: str,
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    interval: str = "24h",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display active addresses of a certain symbol over time
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (possible values are: 24h, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_active_addresses(symbol, interval, start_date, end_date)

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)

    ax.set_title(f"Active {symbol} addresses over time")
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
    symbol: str,
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : int
        End date timestamp (e.g., 1_609_459_200)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_non_zero_addresses(symbol, start_date, end_date)

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(df_addresses.index, df_addresses["v"] / 1_000, linewidth=1.5)

    ax.set_title(f"{symbol} Addresses with non-zero balances")
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
    symbol: str,
    exchange: str = "binance",
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display 30d change of the supply held in exchange wallets.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance,
        bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex,
        hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_addresses = get_exchange_net_position_change(
        symbol, exchange, start_date, end_date
    )

    if df_addresses.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

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

    ax.set_ylabel(f"30d change of {symbol} supply held in exchange wallets [thousands]")
    ax.set_title(
        f"{symbol}: Exchange Net Position Change - {'all exchanges' if exchange == 'aggregated' else exchange}"
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
    symbol: str,
    exchange: str = "binance",
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    percentage: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance, bittrex,
        coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,
        okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    percentage : bool
        Show percentage instead of stacked value.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    df_balance = get_exchange_balances(symbol, exchange, start_date, end_date)

    if df_balance.empty:
        return

    # This plot has 2 axes
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        ax2 = ax1.twinx()

    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    if percentage:
        ax1.plot(df_balance.index, df_balance["percentage"] * 100)
    else:
        ax1.plot(df_balance.index, df_balance["stacked"] / 1000)

    ax1.set_ylabel(f"{symbol} units [{'%' if percentage else 'thousands'}]")
    ax1.set_title(
        f"{symbol}: Total Balance in {'all exchanges' if exchange == 'aggregated' else exchange}"
    )
    ax1.tick_params(axis="x", labelrotation=10)
    ax1.legend([f"{symbol} Unit"], loc="upper right")

    ax2.grid(visible=False)
    ax2.plot(df_balance.index, df_balance["price"], color="orange")
    ax2.set_ylabel(f"{symbol} price [$]")
    ax2.legend([f"{symbol} Price"], loc="upper left")

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
    symbol: str,
    start_date: int = int((datetime.now() - timedelta(days=365)).timestamp()),
    end_date: int = int(datetime.now().timestamp()),
    interval: str = "24h",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display dataframe with mean hashrate of btc or eth blockchain and symbol price.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Blockchain to check mean hashrate (BTC or ETH)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (possible values are: 24, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    df = get_hashrate(symbol, interval, start_date, end_date)

    if df.empty:
        return

    # This plot has 2 axes
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        ax2 = ax1.twinx()

    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    ax1.plot(
        df.index, df["hashrate"] / 1_000_000_000_000, color=theme.down_color, lw=0.8
    )
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}T"))
    ax1.set_ylabel(f"{symbol} hashrate (Terahashes/second)")
    ax1.set_title(f"{symbol}: Mean hashrate")
    ax1.tick_params(axis="x", labelrotation=10)

    ax2.set_xlim(left=df.index[0])
    ax2.grid(visible=False)
    ax2.plot(df.index, df["price"] / 1_000, color=theme.up_color, lw=0.8)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:.1f}k"))
    ax2.set_ylabel(f"{symbol} price [$]")

    # Manually construct the chart legend
    lines = [
        Line2D([0], [0], color=color) for color in [theme.up_color, theme.down_color]
    ]
    labels = ["Price", "Hash Rate"]
    ax2.legend(lines, labels)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hr",
        df,
    )
