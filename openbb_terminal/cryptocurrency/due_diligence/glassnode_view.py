import logging
import os
from datetime import datetime
from typing import Optional, Union

import numpy as np

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_exchange_balances,
    get_exchange_net_position_change,
    get_hashrate,
    get_non_zero_addresses,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data

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
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df_addresses = get_active_addresses(symbol, interval, start_date, end_date)

    if df_addresses.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Addresses")
    fig.set_title(f"Active {symbol} addresses over time")

    fig.add_scatter(
        x=df_addresses.index,
        y=df_addresses["v"],
        name="Active Addresses",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df_addresses,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_non_zero_addresses(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df_addresses = get_non_zero_addresses(symbol, start_date, end_date)

    if df_addresses.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Addresses")
    fig.set_title(f"{symbol} Addresses with non-zero balances")

    fig.add_scatter(x=df_addresses.index, y=df_addresses["v"], name="Addresses")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "nonzero",
        df_addresses,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_exchange_net_position_change(
    symbol: str,
    exchange: str = "binance",
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df_addresses = get_exchange_net_position_change(
        symbol, exchange, start_date, end_date
    )

    if df_addresses.empty:
        return None

    fig = OpenBBFigure(
        yaxis_title=f"30d change of {symbol} supply held in exchange wallets"
    )
    fig.set_title(
        f"{symbol}: Exchange Net Position Change - {'all exchanges' if exchange == 'aggregated' else exchange}",
    )

    fig.add_scatter(
        x=df_addresses[df_addresses["v"] < 0].index,
        y=df_addresses[df_addresses["v"] < 0]["v"].values,
        mode="lines",
        name="Negative",
        line_color=theme.down_color,
    )
    fig.add_scatter(
        x=df_addresses[df_addresses["v"] < 0].index,
        y=np.zeros(len(df_addresses[df_addresses["v"] < 0])),
        mode="lines",
        fill="tonexty",
        name="Negative",
        line_color=theme.down_color,
        fillcolor=theme.down_color,
    )
    fig.add_scatter(
        x=df_addresses[df_addresses["v"] >= 0].index,
        y=df_addresses[df_addresses["v"] >= 0]["v"].values,
        mode="lines",
        name="Positive",
        line_color=theme.up_color,
    )
    fig.add_scatter(
        x=df_addresses[df_addresses["v"] >= 0].index,
        y=np.zeros(len(df_addresses[df_addresses["v"] >= 0])),
        mode="lines",
        fill="tonexty",
        name="Positive",
        line_color=theme.up_color,
        fillcolor=theme.up_color,
    )
    fig.update_traces(showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "change",
        df_addresses,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


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
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.dd.eb_chart(symbol="BTC")
    """

    df_balance = get_exchange_balances(symbol, exchange, start_date, end_date)

    if df_balance.empty:
        return None

    fig = OpenBBFigure.create_subplots(specs=[[{"secondary_y": True}]])
    fig.set_title(
        f"{symbol}: Total Balance in"
        f" {'all exchanges' if exchange == 'aggregated' else exchange}"
    )

    fig.set_yaxis_title(
        f"{symbol} units {'[%]' if percentage else ''}", secondary_y=True, side="left"
    )
    fig.set_yaxis_title(f"{symbol} price [$]", secondary_y=False, showgrid=False)

    fig.add_scatter(
        x=df_balance.index,
        y=df_balance["percentage"] * 100 if percentage else df_balance["stacked"],
        mode="lines",
        name=f"{symbol} Unit",
        secondary_y=True,
    )

    fig.add_scatter(
        x=df_balance.index,
        y=df_balance["price"],
        mode="lines",
        name=f"{symbol} Price",
        line_color="orange",
        secondary_y=False,
    )

    fig.update_layout(margin=dict(t=30))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "eb",
        df_balance,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def display_hashrate(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    interval: str = "24h",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = get_hashrate(symbol, interval, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure.create_subplots(specs=[[{"secondary_y": True}]])

    fig.add_scatter(
        x=df.index,
        y=df["hashrate"] / 1e12,
        mode="lines",
        name="Hash Rate",
        line_color=theme.down_color,
        secondary_y=True,
    )

    fig.set_yaxis_title(
        f"{symbol} hashrate (Terahashes/second)",
        secondary_y=True,
        side="left",
        tickformat=".2s",
    )
    fig.set_yaxis_title(f"{symbol} price [$]", secondary_y=False, showgrid=False)
    fig.set_title(f"{symbol}: Mean hashrate")

    fig.add_scatter(
        x=df.index,
        y=df["price"],
        mode="lines",
        name="Price",
        line_color=theme.up_color,
        secondary_y=False,
    )
    fig.update_layout(margin=dict(t=30))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hr",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
