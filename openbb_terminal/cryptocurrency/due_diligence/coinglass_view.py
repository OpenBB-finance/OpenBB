import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.due_diligence.coinglass_model import (
    get_funding_rate,
    get_liquidations,
    get_open_interest_per_exchange,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_funding_rate(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> None:
    """Plots funding rate by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search funding rate (e.g., BTC)
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """
    df = get_funding_rate(symbol)
    if df.empty:
        return None

    fig = plot_data(
        df, symbol, f"Exchange {symbol} Funding Rate", "Funding Rate [%]", True
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fundrate",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_open_interest(
    symbol: str,
    interval: int = 0,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
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
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = get_open_interest_per_exchange(symbol, interval)
    if df.empty:
        return None

    fig = plot_data(
        df,
        symbol,
        f"Exchange {symbol} Futures Open Interest",
        "Open futures value [$]",
        True,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_COINGLASS_KEY"])
def display_liquidations(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots liquidation per day data for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/#liquidation-chart]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    export : str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = get_liquidations(symbol)
    if df.empty:
        return None

    fig = plot_data_bar(
        df,
        symbol,
        f"Total liquidations for {symbol}",
        "Liquidations value [$]",
        True,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "liquidations",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plot_data(
    df: pd.DataFrame,
    symbol: str = "",
    title: str = "",
    ylabel: str = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    fig = OpenBBFigure.create_subplots(2, 1)

    df_price = df[["price"]].copy()
    df_without_price = df.drop("price", axis=1)

    groups = {"2": "two", "4": "three", "6": "four", "8": "five"}
    legendgroup = "one"
    for i, column in enumerate(df_without_price.columns):
        if i > 0:
            legendgroup = groups.get(str(i), legendgroup)

        fig.add_scatter(
            x=df_without_price.index,
            y=df_without_price[column],
            name=column,
            row=1,
            col=1,
            stackgroup="one",
            legendgroup=legendgroup,
        )

    fig.add_scatter(
        x=df_price.index,
        y=df_price["price"],
        name=f"{symbol} price",
        showlegend=False,
        line=dict(color=theme.get_colors()[0]),
        row=2,
        col=1,
    )

    if title:
        fig.set_title(title)
    if ylabel:
        fig.set_yaxis_title(ylabel, 1, 1)

    if symbol:
        fig.set_yaxis_title(f"{symbol} Price [$]", 2, 1)

    fig.update_layout(legend=dict(orientation="h"))

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plot_data_bar(
    df: pd.DataFrame,
    symbol: str = "",
    title: str = "",
    ylabel: str = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    fig = OpenBBFigure.create_subplots(2, 1)

    df_price = df[["price"]].copy()
    df_without_price = df.drop("price", axis=1)

    df_without_price["Shorts"] = df_without_price["Shorts"] * -1

    fig.add_bar(
        x=df_without_price.index,
        y=df_without_price["Shorts"],
        name="Shorts",
        row=1,
        col=1,
        marker_color=theme.down_color,
    )
    fig.add_bar(
        x=df_without_price.index,
        y=df_without_price["Longs"],
        name="Longs",
        row=1,
        col=1,
        marker_color=theme.up_color,
    )

    if title:
        fig.set_title(title)
    if ylabel:
        fig.set_yaxis_title(ylabel, 1, 1)

    fig.add_scatter(
        x=df_price.index,
        y=df_price["price"],
        name=f"{symbol} price",
        showlegend=False,
        line=dict(color=theme.get_colors()[0]),
        row=2,
        col=1,
    )
    if symbol:
        fig.set_yaxis_title(f"{symbol} Price [$]", 2, 1)

    fig.update_layout(
        legend=dict(orientation="h"),
        bargap=0,
        bargroupgap=0,
    )

    return fig.show(external=external_axes)
