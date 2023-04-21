"""Oanda View."""
__docformat__ = "numpy"

import logging
from typing import Dict, Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.forex.oanda.oanda_model import (
    account_summary_request,
    cancel_pending_order_request,
    close_trades_request,
    create_order_request,
    fx_price_request,
    get_calendar_request,
    get_candles_dataframe,
    open_positions_request,
    open_trades_request,
    order_history_request,
    orderbook_plot_data_request,
    pending_orders_request,
    positionbook_plot_data_request,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_fx_price(account: str, instrument: Union[str, None] = ""):
    """View price for loaded currency pair.

    Parameters
    ----------
    accountID : str
        Oanda account ID
    instrument : Union[str, None]
        Instrument code or None
    """
    data = fx_price_request(accountID=account, instrument=instrument)
    if data and data is not None and "prices" in data:
        bid = data["prices"][0]["bids"][0]["price"]
        ask = data["prices"][0]["asks"][0]["price"]
        console.print(f"{instrument if instrument else ''}" + " Bid: " + bid)
        console.print(f"{instrument if instrument else ''}" + " Ask: " + ask)
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_account_summary(accountID: str):
    """Print Oanda account summary.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_summary = account_summary_request(accountID)
    if df_summary is not False and not df_summary.empty:
        console.print(df_summary.to_string(index=False, header=False))
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_order_book(
    accountID: str,
    instrument: str = "",
    external_axes: bool = False,
):
    """
    Plot the orderbook for the instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_orderbook_data = orderbook_plot_data_request(
        accountID=accountID, instrument=instrument
    )
    if df_orderbook_data is not False and not df_orderbook_data.empty:
        pd.set_option("display.max_rows", None)
        # HELP WANTED!
        # TODO:
        # An early contributor left "magic constants" in this function
        # help is needed to figure out the rationale behind these or
        # refactor it to not include the magic numbers.
        df_orderbook_data = df_orderbook_data.take(range(527, 727, 1))
        book_plot(
            df_orderbook_data, instrument, "Order Book", external_axes=external_axes
        )
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_position_book(
    accountID: str, instrument: str = "", external_axes: bool = False
):
    """Plot a position book for an instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_positionbook_data = positionbook_plot_data_request(
        accountID=accountID, instrument=instrument
    )
    if df_positionbook_data is not False and not df_positionbook_data.empty:
        pd.set_option("display.max_rows", None)
        # HELP WANTED!
        # TODO:
        # An early contributor left "magic constants" in this function
        # help is needed to figure out the rationale behind these or
        # refactor it to not include the magic numbers.
        df_positionbook_data = df_positionbook_data.take(range(219, 300, 1))
        book_plot(
            df_positionbook_data,
            instrument,
            "Position Book",
            external_axes=external_axes,
        )
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def list_orders(accountID: str, order_state: str = "PENDING", order_count: int = 0):
    """List order history.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
    """
    df_order_list = order_history_request(order_state, order_count, accountID)
    if df_order_list is not False and not df_order_list.empty:
        console.print(df_order_list)
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def create_order(accountID: str, instrument: str = "", price: int = 0, units: int = 0):
    """Create a buy/sell order.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
    """
    df_orders = create_order_request(price, units, instrument, accountID)
    if df_orders is not False and not df_orders.empty:
        console.print(df_orders.to_string(index=False))
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def cancel_pending_order(accountID: str, orderID: str = ""):
    """Cancel a Pending Order.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    orderID : str
        The pending order ID to cancel.
    """
    order_id = cancel_pending_order_request(orderID, accountID)
    if order_id is not False and order_id is not None:
        console.print(f"Order {order_id} canceled.")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_open_positions(accountID: str):
    """Get information about open positions.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_positions = open_positions_request(accountID)
    if df_positions is not False and not df_positions.empty:
        console.print(df_positions.to_string(index=False))
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_pending_orders(accountID: str):
    """Get information about pending orders.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_pending = pending_orders_request(accountID)
    if df_pending is not False and not df_pending.empty:
        console.print(df_pending.to_string(index=False))
    elif df_pending is not False and df_pending.empty:
        console.print("No pending orders.\n")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_open_trades(accountID: str):
    """View open trades.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_trades = open_trades_request(accountID)
    if isinstance(df_trades, pd.DataFrame) and not df_trades.empty:
        console.print(df_trades.to_string(index=False))
    elif df_trades is not False and df_trades.empty:
        console.print("No trades were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def close_trade(accountID: str, orderID: str = "", units: Union[int, None] = None):
    """Close a trade.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    """
    df_trades = close_trades_request(orderID, units, accountID)
    if df_trades is not False and not df_trades.empty:
        console.print(df_trades.to_string(index=False))
    elif df_trades is not False and df_trades.empty:
        console.print("No trades were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def show_candles(
    instrument: str = "",
    granularity: str = "D",
    candlecount: int = 180,
    additional_charts: Optional[Dict[str, bool]] = None,
    external_axes: bool = False,
):
    """Show candle chart.

    Note that additional plots (ta indicators) not supported in external axis mode.

    Parameters
    ----------
    instrument : str
        The loaded currency pair
    granularity : str, optional
        The timeframe to get for the candle chart. Seconds: S5, S10, S15, S30
        Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12
        Day (default): D, Week: W Month: M,
    candlecount : int, optional
        Limit for the number of data points
    additional_charts : Dict[str, bool]
        A dictionary of flags to include additional charts
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_candles = get_candles_dataframe(instrument, granularity, candlecount)

    if not (has_volume := False) and "Volume" in df_candles.columns:
        has_volume = bool(df_candles["Volume"].sum() > 0)

    indicators = dict(rma=dict(length=[20, 50]))
    defaults = dict(ema=dict(length=10), sma=dict(length=[20, 50]))
    if additional_charts:
        for key, value in additional_charts.items():
            if value:
                indicators[key] = defaults.get(key, {}) or {}  # type: ignore

    if isinstance(df_candles, pd.DataFrame):
        df_candles.name = f"{instrument} {granularity}"
        fig = PlotlyTA.plot(df_candles, indicators, volume=has_volume)
        return fig.show(external=external_axes)

    logger.error("Data not found")
    console.print("[red]Data not found[/red]\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def calendar(instrument: str, days: int = 7):
    """View calendar of significant events.

    Parameters
    ----------
    instrument : str
        The loaded currency pair
    days : int
        Number of days in advance
    """
    df_calendar = get_calendar_request(days, instrument)
    if df_calendar is not False and not df_calendar.empty:
        console.print(df_calendar.to_string(index=False))
    elif df_calendar is not False and df_calendar.empty:
        console.print("No calendar records were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


# Utilities


@log_start_end(log=logger)
def book_plot(
    df: pd.DataFrame,
    instrument: str,
    book_type: str,
    external_axes: bool = False,
):
    """Plot the order book for a given instrument.

    Parameters
    ----------
    df : pd.DataFrame
        Order book data
    instrument : str
        The loaded currency pair
    book_type : str
        Order book type
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = df.apply(pd.to_numeric)
    df["shortCountPercent"] = df["shortCountPercent"] * -1

    fig = OpenBBFigure(xaxis_title="Count Percent", yaxis_title="Price")
    fig.set_title(f"{instrument} {book_type}")

    fig.add_bar(
        x=df["longCountPercent"],
        y=df["price"],
        name="Count Percent",
        marker_color=theme.up_color,
        orientation="h",
    )
    fig.add_bar(
        x=df["shortCountPercent"],
        y=df["price"],
        name="Prices",
        marker_color=theme.down_color,
        orientation="h",
    )
    fig.update_layout(yaxis_nticks=20, bargap=0.01, bargroupgap=0.01)

    return fig.show(external=external_axes)
