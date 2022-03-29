"""Oanda View."""
__docformat__ = "numpy"

import logging
from typing import Dict, Union, Optional, List

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplfinance as mpf
import pandas as pd
import pandas_ta as ta
import seaborn as sns

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import check_api_key
from openbb_terminal.decorators import log_start_end
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
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_fx_price(account: str, instrument: Union[str, None]):
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
        console.print("")
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
    instrument: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """
    Plot the orderbook for the instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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
        console.print("")
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def get_position_book(
    accountID: str, instrument: str, external_axes: Optional[List[plt.Axes]] = None
):
    """Plot a position book for an instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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
        console.print("")
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def list_orders(accountID: str, order_state: str, order_count: int):
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
        console.print("")
    else:
        console.print("No data was retrieved.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def create_order(accountID: str, instrument: str, price: int, units: int):
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
        console.print("")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def cancel_pending_order(accountID: str, orderID: str):
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
        console.print("")
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
        console.print("")
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
        console.print("")
    elif df_pending is not False and df_pending.empty:
        console.print("No pending orders.\n")
    else:
        console.print("No data was returned from Oanda.\n")


# Pylint raises no-member error because the df_trades can be either
# a dataframe or a boolean (False) value that has no .empty and no .to_string
# pylint: disable=no-member
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
    if df_trades is not False and not df_trades.empty:
        console.print(df_trades.to_string(index=False))
        console.print("")
    elif df_trades is not False and df_trades.empty:
        console.print("No trades were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def close_trade(accountID: str, orderID: str, units: Union[int, None]):
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
        console.print("")
    elif df_trades is not False and df_trades.empty:
        console.print("No trades were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def show_candles(
    instrument: str,
    granularity: str,
    candlecount: int,
    additional_charts: Optional[Dict[str, bool]] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show candle chart.

    Note that additional plots (ta indicators) not supported in external axis mode.

    Parameters
    ----------
    instrument : str
        The loaded currency pair
    granularity : str, optional
        Data granularity
    candlecount : int, optional
        Limit for the number of data points
    additional_charts : Dict[str, bool]
        A dictionary of flags to include additional charts
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_candles = get_candles_dataframe(instrument, granularity, candlecount)
    if (
        df_candles is not False
        and not df_candles.empty
        and additional_charts is not None
    ):
        plots_to_add, legends, subplot_legends = add_plots(
            df_candles, additional_charts
        )
    else:
        plots_to_add, legends, subplot_legends = None, [], []

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "mav": (20, 50),
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    # This plot has 2 axes
    if external_axes is not None:
        if len(external_axes) != 2:
            logger.error("Expected list of 2 axis items")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax, volume = external_axes
        candle_chart_kwargs["ax"] = ax
        candle_chart_kwargs["volume"] = volume
        mpf.plot(df_candles, **candle_chart_kwargs)
    else:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        if plots_to_add:
            candle_chart_kwargs["addplot"] = plots_to_add
        if isinstance(df_candles, pd.DataFrame):
            fig, ax = mpf.plot(df_candles, **candle_chart_kwargs)
            fig.suptitle(
                f"{instrument} {granularity}",
                x=0.055,
                y=0.965,
                horizontalalignment="left",
            )
            if len(legends) > 0:
                ax[0].legend(legends)
            # pylint: disable=C0200
            for i in range(0, len(subplot_legends), 2):
                ax[subplot_legends[i]].legend(subplot_legends[i + 1])
            theme.visualize_output(force_tight_layout=False)
        else:
            logger.error("Data not found")
            console.print("[red]Data not found[/red]\n")


@log_start_end(log=logger)
@check_api_key(["OANDA_ACCOUNT", "OANDA_TOKEN", "OANDA_ACCOUNT_TYPE"])
def calendar(instrument: str, days: int):
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
        console.print("")
    elif df_calendar is not False and df_calendar.empty:
        console.print("No calendar records were found.\n")
    else:
        console.print("No data was returned from Oanda.\n")


# Utilities


@log_start_end(log=logger)
def add_plots(df: pd.DataFrame, additional_charts: Dict[str, bool]):
    """Add additional plots to the candle chart.

    Parameters
    ----------
    df : pd.DataFrame
        The source data
    additional_charts : Dict[str, bool]
        A dictionary of flags to include additional charts

    Returns
    -------
    Tuple
        Tuple of lists containing the plots, legends and subplot legends
    """
    panel_number = 2
    plots_to_add = []
    legends = []
    subplot_legends = []

    if additional_charts["ad"]:
        ad = ta.ad(df["High"], df["Low"], df["Close"], df["Volume"])
        ad_plot = mpf.make_addplot(ad, panel=panel_number)
        plots_to_add.append(ad_plot)
        subplot_legends.extend([panel_number * 2, ["AD"]])
        panel_number += 1

    if additional_charts["bbands"]:
        bbands = ta.bbands(df["Close"])
        bbands = bbands.drop("BBB_5_2.0", axis=1)
        bbands_plot = mpf.make_addplot(bbands, panel=0)
        plots_to_add.append(bbands_plot)
        legends.extend(["Lower BBand", "Middle BBand", "Upper BBand"])

    if additional_charts["cci"]:
        cci = ta.cci(df["High"], df["Low"], df["Close"])
        cci_plot = mpf.make_addplot(cci, panel=panel_number)
        plots_to_add.append(cci_plot)
        subplot_legends.extend([panel_number * 2, ["CCI"]])
        panel_number += 1

    if additional_charts["ema"]:
        ema = ta.ema(df["Close"])
        ema_plot = mpf.make_addplot(ema, panel=0)
        plots_to_add.append(ema_plot)
        legends.append("10 EMA")

    if additional_charts["rsi"]:
        rsi = ta.rsi(df["Close"])
        rsi_plot = mpf.make_addplot(rsi, panel=panel_number)
        plots_to_add.append(rsi_plot)
        subplot_legends.extend([panel_number * 2, ["RSI"]])
        panel_number += 1

    if additional_charts["obv"]:
        obv = ta.obv(df["Close"], df["Volume"])
        obv_plot = mpf.make_addplot(obv, panel=panel_number)
        plots_to_add.append(obv_plot)
        subplot_legends.extend([panel_number * 2, ["OBV"]])
        panel_number += 1

    if additional_charts["sma"]:
        sma_length = [20, 50]
        for length in sma_length:
            sma = ta.sma(df["Close"], length=length)
            sma_plot = mpf.make_addplot(sma, panel=0)
            plots_to_add.append(sma_plot)
            legends.append(f"{length} SMA")

    if additional_charts["vwap"]:
        vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
        vwap_plot = mpf.make_addplot(vwap, panel=0)
        plots_to_add.append(vwap_plot)
        legends.append("vwap")

    return plots_to_add, legends, subplot_legends


@log_start_end(log=logger)
def book_plot(
    df: pd.DataFrame,
    instrument: str,
    book_type: str,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis are expected in the list), by default None
    """
    df = df.apply(pd.to_numeric)
    df["shortCountPercent"] = df["shortCountPercent"] * -1
    axis_origin = max(
        abs(max(df["longCountPercent"])), abs(max(df["shortCountPercent"]))
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.set_xlim(-axis_origin, +axis_origin)

    sns.barplot(
        x="longCountPercent",
        y="price",
        data=df,
        label="Count Percent",
        color=theme.up_color,
        orient="h",
    )

    sns.barplot(
        x="shortCountPercent",
        y="price",
        data=df,
        label="Prices",
        color=theme.down_color,
        orient="h",
    )

    ax.invert_yaxis()
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.set_xlabel("Count Percent")
    ax.set_ylabel("Price")
    ax.set_title(f"{instrument} {book_type}")

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()
