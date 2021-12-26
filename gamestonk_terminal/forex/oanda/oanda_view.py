"""Oanda View."""
__docformat__ = "numpy"

from typing import Dict, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplfinance as mpf
import pandas as pd
import pandas_ta as ta
import seaborn as sns

from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
)

from gamestonk_terminal.forex.oanda.oanda_model import (
    cancel_pending_order_request,
    close_trades_request,
    fx_price_request,
    account_summary_request,
    open_positions_request,
    open_trades_request,
    orderbook_plot_data_request,
    pending_orders_request,
    positionbook_plot_data_request,
    order_history_request,
    create_order_request,
    get_candles_dataframe,
    get_calendar_request,
)


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
        print(f"{instrument if instrument else ''}" + " Bid: " + bid)
        print(f"{instrument if instrument else ''}" + " Ask: " + ask)
        print("")
    else:
        print("No data was retrieved.\n")


def get_account_summary(accountID: str):
    """Print Oanda account summary.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_summary = account_summary_request(accountID)
    if df_summary is not False and not df_summary.empty:
        print(df_summary.to_string(index=False, header=False))
    else:
        print("No data was retrieved.\n")


def get_order_book(accountID: str, instrument: str):
    """
    Plot the orderbook for the instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
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
        book_plot(df_orderbook_data, instrument, "Order Book")
        print("")
    else:
        print("No data was retrieved.\n")


def get_position_book(accountID: str, instrument: str):
    """Plot a position book for an instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
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
        book_plot(df_positionbook_data, instrument, "Position Book")
        print("")
    else:
        print("No data was retrieved.\n")


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
        print(df_order_list)
        print("")
    else:
        print("No data was retrieved.\n")


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
        print(df_orders.to_string(index=False))
        print("")
    else:
        print("No data was returned from Oanda.\n")


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
        print(f"Order {order_id} canceled.")
        print("")
    else:
        print("No data was returned from Oanda.\n")


def get_open_positions(accountID: str):
    """Get information about open positions.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_positions = open_positions_request(accountID)
    if df_positions is not False and not df_positions.empty:
        print(df_positions.to_string(index=False))
        print("")
    else:
        print("No data was returned from Oanda.\n")


def get_pending_orders(accountID: str):
    """Get information about pending orders.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_pending = pending_orders_request(accountID)
    if df_pending is not False and not df_pending.empty:
        print(df_pending.to_string(index=False))
        print("")
    elif df_pending is not False and df_pending.empty:
        print("No pending orders.\n")
    else:
        print("No data was returned from Oanda.\n")


# Pylint raises no-member error because the df_trades can be either
# a dataframe or a boolean (False) value that has no .empty and no .to_string
# pylint: disable=no-member
def get_open_trades(accountID: str):
    """View open trades.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    """
    df_trades = open_trades_request(accountID)
    if df_trades is not False and not df_trades.empty:
        print(df_trades.to_string(index=False))
        print("")
    elif df_trades is not False and df_trades.empty:
        print("No trades were found.\n")
    else:
        print("No data was returned from Oanda.\n")


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
        print(df_trades.to_string(index=False))
        print("")
    elif df_trades is not False and df_trades.empty:
        print("No trades were found.\n")
    else:
        print("No data was returned from Oanda.\n")


def show_candles(
    instrument: str,
    granularity: str,
    candlecount: int,
    additional_charts: Dict[str, bool],
):
    """Show candle chart.

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
    """
    df_candles = get_candles_dataframe(instrument, granularity, candlecount)
    if df_candles is not False and not df_candles.empty:
        plots_to_add, legends, subplot_legends = add_plots(
            df_candles, additional_charts
        )

    if gtff.USE_ION:
        plt.ion()

    _, ax = mpf.plot(
        df_candles,
        type="candle",
        style="charles",
        volume=True,
        scale_padding={"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        returnfig=True,
        addplot=plots_to_add,
    )

    ax[0].set_title(f"{instrument} {granularity}")
    if len(legends) > 0:
        ax[0].legend(legends)
    # pylint: disable=C0200
    for i in range(0, len(subplot_legends), 2):
        ax[subplot_legends[i]].legend(subplot_legends[i + 1])

    print("")


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
        print(df_calendar.to_string(index=False))
        print("")
    elif df_calendar is not False and df_calendar.empty:
        print("No calendar records were found.\n")
    else:
        print("No data was returned from Oanda.\n")


# Utilities


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


def book_plot(df: pd.DataFrame, instrument: str, book_type: str):
    """Plot the order book for a given instrument.

    Parameters
    ----------
    df : pd.DataFrame
        Order book data
    instrument : str
        The loaded currency pair
    book_type : str
        Order book type
    """
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    df = df.apply(pd.to_numeric)
    df["shortCountPercent"] = df["shortCountPercent"] * -1
    axis_origin = max(
        abs(max(df["longCountPercent"])), abs(max(df["shortCountPercent"]))
    )
    ax.set_xlim(-axis_origin, +axis_origin)

    sns.set_style(style="darkgrid")

    sns.barplot(
        x="longCountPercent",
        y="price",
        data=df,
        label="Count Percent",
        color="green",
        orient="h",
    )

    sns.barplot(
        x="shortCountPercent",
        y="price",
        data=df,
        label="Prices",
        color="red",
        orient="h",
    )

    ax.invert_yaxis()
    plt.title(f"{instrument} {book_type}")
    plt.xlabel("Count Percent")
    plt.ylabel("Price")
    sns.despine(left=True, bottom=True)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(5))
    if gtff.USE_ION:
        plt.ion()
    plt.show()
