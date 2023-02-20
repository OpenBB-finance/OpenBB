import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import (
    pyplot as plt,
    ticker,
)

from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.due_diligence.coinglass_model import (
    get_funding_rate,
    get_liquidations,
    get_open_interest_per_exchange,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format,
    plot_autoscale,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_funding_rate(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Plots funding rate by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search funding rate (e.g., BTC)
    export : str
        Export dataframe data to csv,json,xlsx file"""
    df = get_funding_rate(symbol)
    if df.empty:
        return

    plot_data(df, symbol, f"Exchange {symbol} Funding Rate", "Funding Rate [%]")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fundrate",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_open_interest(
    symbol: str, interval: int = 0, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Plots open interest by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0
    export : str
        Export dataframe data to csv,json,xlsx file"""
    df = get_open_interest_per_exchange(symbol, interval)
    if df.empty:
        return

    plot_data(
        df,
        symbol,
        f"Exchange {symbol} Futures Open Interest",
        "Open futures value [$B]",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_liquidations(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Plots liquidation per day data for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/#liquidation-chart]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    export : str
        Export dataframe data to csv,json,xlsx file"""
    df = get_liquidations(symbol)
    if df.empty:
        return

    plot_data_bar(
        df,
        symbol,
        f"Total liquidations for {symbol}",
        "Liquidations value [$M]",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "liquidations",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def plot_data(
    df: pd.DataFrame,
    symbol: str = "",
    title: str = "",
    ylabel: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    # This plot has 2 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    df_price = df[["price"]].copy()
    df_without_price = df.drop("price", axis=1)

    ax1.stackplot(
        df_without_price.index,
        df_without_price.transpose().to_numpy(),
        labels=df_without_price.columns.tolist(),
    )

    ax1.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )
    ax1.legend(df_without_price.columns, fontsize="x-small", ncol=2)
    if title:
        ax1.set_title(title)
    if ylabel:
        ax1.set_ylabel(ylabel)

    ax2.plot(df_price.index, df_price)
    if symbol:
        ax2.legend([f"{symbol} price"])
        ax2.set_ylabel(f"{symbol} Price [$]")
    ax2.set_xlim([df_price.index[0], df_price.index[-1]])
    ax2.set_ylim(bottom=0.0)

    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def plot_data_bar(
    df: pd.DataFrame,
    symbol: str = "",
    title: str = "",
    ylabel: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    # This plot has 2 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    df_price = df[["price"]].copy()
    df_without_price = df.drop("price", axis=1)

    df_without_price["Shorts"] = df_without_price["Shorts"] * -1

    ax1.bar(
        df_without_price.index,
        df_without_price["Shorts"],
        label="Shorts",
        color=theme.down_color,
    )

    ax1.bar(
        df_without_price.index,
        df_without_price["Longs"],
        label="Longs",
        color=theme.up_color,
    )

    ax1.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )
    ax1.legend(df_without_price.columns, fontsize="x-small", ncol=2)
    if title:
        ax1.set_title(title)
    if ylabel:
        ax1.set_ylabel(ylabel)

    ax2.plot(df_price.index, df_price)
    if symbol:
        ax2.legend([f"{symbol} price"])
        ax2.set_ylabel(f"{symbol} Price [$]")
    ax2.set_xlim([df_price.index[0], df_price.index[-1]])
    ax2.set_ylim(bottom=0.0)

    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)

    if not external_axes:
        theme.visualize_output()
