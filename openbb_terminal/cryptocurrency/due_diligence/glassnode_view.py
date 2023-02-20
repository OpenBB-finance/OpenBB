import logging
import os
from datetime import datetime
from typing import List, Optional

import numpy as np
from matplotlib import (
    pyplot as plt,
    ticker,
)
from matplotlib.lines import Line2D

from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_exchange_balances,
    get_exchange_net_position_change,
    get_hashrate,
    get_non_zero_addresses,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_active_addresses(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    interval: str = "24h",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots active addresses of a certain symbol over time
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    interval : str
        Interval frequency (possible values are: 24h, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

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
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_non_zero_addresses(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search (e.g., BTC)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

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
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_exchange_net_position_change(
    symbol: str,
    exchange: str = "binance",
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots 30d change of the supply held in exchange wallets.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance,
        bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex,
        hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

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
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_exchange_balances(
    symbol: str,
    exchange: str = "aggregated",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    percentage: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance, bittrex,
        coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,
        okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno), by default "aggregated"
    start_date : Optional[str], optional
        Initial date (format YYYY-MM-DD) by default 2 years ago
    end_date : Optional[str], optional
        Final date (format YYYY-MM-DD) by default 1 year ago
    percentage : bool
        Show percentage instead of stacked value.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.dd.eb_chart(symbol="BTC")
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
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_hashrate(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    interval: str = "24h",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots dataframe with mean hashrate of btc or eth blockchain and symbol price.
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Blockchain to check mean hashrate (BTC or ETH)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    interval : str
        Interval frequency (possible values are: 24, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

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
        sheet_name,
    )
