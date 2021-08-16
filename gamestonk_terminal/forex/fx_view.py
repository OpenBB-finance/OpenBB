import argparse
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplfinance as mpf
import pandas as pd
import pandas_ta as ta
import seaborn as sns
from oandapyV20 import API
from oandapyV20.endpoints import (
    accounts,
    forexlabs,
    instruments,
    orders,
    positions,
    pricing,
    trades,
)
from oandapyV20.exceptions import V20Error

from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    parse_known_args_and_warn,
    plot_autoscale,
)

client = API(access_token=cfg.OANDA_TOKEN, environment=cfg.OANDA_ACCOUNT_TYPE)
account = cfg.OANDA_ACCOUNT


def get_fx_price(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="price",
        description="Get price for selected instrument.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        parameters = {"instruments": instrument}
        request = pricing.PricingInfo(accountID=accountID, params=parameters)
        response = client.request(request)
        bid = response["prices"][0]["bids"][0]["price"]
        ask = response["prices"][0]["asks"][0]["price"]
        print(instrument + " Bid: " + bid)
        print(instrument + " Ask: " + ask)
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_account_summary(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="summary",
        description="Print some information about your account.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        request = accounts.AccountSummary(accountID=accountID)
        response = client.request(request)

        df_summary = pd.DataFrame(
            [
                {"Type": "Balance", "Value": response["account"]["balance"]},
                {"Type": "NAV", "Value": response["account"]["NAV"]},
                {
                    "Type": "Unrealized P/L",
                    "Value": response["account"]["unrealizedPL"],
                },
                {"Type": "Total P/L", "Value": response["account"]["pl"]},
                {
                    "Type": "Open Trade Count",
                    "Value": response["account"]["openTradeCount"],
                },
                {
                    "Type": "Margin Available",
                    "Value": response["account"]["marginAvailable"],
                },
                {"Type": "Margin Used", "Value": response["account"]["marginUsed"]},
                {
                    "Type": "Margin Closeout",
                    "Value": response["account"]["marginCloseoutNAV"],
                },
                {
                    "Type": "Margin Closeout Percent",
                    "Value": response["account"]["marginCloseoutPercent"],
                },
                {
                    "Type": "Margin Closeout Position Value",
                    "Value": response["account"]["marginCloseoutPositionValue"],
                },
            ]
        )

        print(df_summary.to_string(index=False, header=False))

        print("")
    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def list_orders(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="list",
        description="List order history",
    )
    parser.add_argument(
        "-s",
        "--state",
        dest="state",
        action="store",
        default="ALL",
        required=False,
        help="Select state for order list. ",
    )
    parser.add_argument(
        "-c",
        "--count",
        dest="count",
        action="store",
        default=20,
        required=False,
        help="the number of orders to retrieve ",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {}
    parameters["state"] = ns_parser.state.upper()
    parameters["count"] = ns_parser.count

    try:
        request = orders.OrderList(accountID, parameters)
        response = client.request(request)

        df = pd.DataFrame.from_dict(response["orders"])
        df = df[["id", "instrument", "units", "price", "state", "type"]]
        print(df)
        print("")

    except KeyError:
        print("No orders were found\n")
    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_order_book(instrument, other_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="orderbook",
        description="Plot the orderbook for the instrument if Oanda provides one.",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    parameters = {"bucketWidth": "1"}
    try:
        instrument = format_instrument(instrument, "_")
        request = instruments.InstrumentsOrderBook(
            instrument=instrument, params=parameters
        )
        response = client.request(request)
        df = pd.DataFrame.from_dict(response["orderBook"]["buckets"])
        pd.set_option("display.max_rows", None)
        df = df.take(range(527, 727, 1))
        book_plot(df, instrument, "Order Book")
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_position_book(instrument, other_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="positionbook",
        description="Plot the positionbook for the instrument if Oanda provides one.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        instrument = format_instrument(instrument, "_")
        request = instruments.InstrumentsPositionBook(instrument=instrument)
        response = client.request(request)
        df = pd.DataFrame.from_dict(response["positionBook"]["buckets"])
        pd.set_option("display.max_rows", None)
        df = df.take(range(219, 415, 1))
        book_plot(df, instrument, "Position Book")
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def create_order(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="order",
        description="Create order",
    )
    parser.add_argument(
        "-u",
        "--unit",
        dest="units",
        action="store",
        type=int,
        default=0,
        required=True,
        help="The number of units to place in the order request. Positive for "
        + "a long position and negative for a short position ",
    )
    parser.add_argument(
        "-p",
        "--price",
        dest="price",
        action="store",
        type=check_non_negative,
        required=True,
        help="The price to set for the limit order. ",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    if "JPY" in instrument or "THB" in instrument or "HUF" in instrument:
        ns_parser.price = round(ns_parser.price, 3)
    else:
        ns_parser.price = round(ns_parser.price, 5)

    data = {
        "order": {
            "price": ns_parser.price,
            "instrument": instrument,
            "units": ns_parser.units,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "positionFill": "DEFAULT",
        }
    }
    try:
        request = orders.OrderCreate(accountID, data)
        response = client.request(request)
        order_data = []
        order_data.append(
            {
                "Order ID": response["orderCreateTransaction"]["id"],
                "Instrument": response["orderCreateTransaction"]["instrument"],
                "Price": response["orderCreateTransaction"]["price"],
                "Units": response["orderCreateTransaction"]["units"],
            }
        )

        df = pd.DataFrame.from_dict(order_data)
        print(df.to_string(index=False))
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")
    except Exception as e:
        print(e)


def cancel_pending_order(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="cancel",
        description="Cancel Pending Order ",
    )
    parser.add_argument(
        "-i",
        "--id",
        dest="orderID",
        action="store",
        type=str,
        help="The pending order ID to cancel ",
    )
    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-i")
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    try:
        request = orders.OrderCancel(accountID, ns_parser.orderID)
        response = client.request(request)
        order_id = response["orderCancelTransaction"]["orderID"]
        print(f"Order {order_id} canceled.")
        print("")
    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_pending_orders(accountID, other_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="pending",
        description="Gets information about pending orders.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        request = orders.OrdersPending(accountID)
        response = client.request(request)
        pending_data = []
        for i in range(len(response["orders"])):
            pending_data.append(
                {
                    "Order ID": response["orders"][i]["id"],
                    "Instrument": response["orders"][i]["instrument"],
                    "Price": response["orders"][i]["price"],
                    "Units": response["orders"][i]["units"],
                    "Time Created": response["orders"][i]["createTime"][:10]
                    + " "
                    + response["orders"][i]["createTime"][11:19],
                    "Time In Force": response["orders"][i]["timeInForce"],
                }
            )

        df = pd.DataFrame.from_dict(pending_data)
        if not pending_data:
            print("No pending orders")
        else:
            print(df.to_string(index=False))
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_open_positions(accountID, other_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="positions",
        description="Gets information about open positions.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    try:
        request = positions.OpenPositions(accountID)
        response = client.request(request)
        position_data = []
        for i in range(len(response["positions"])):
            position_data.append(
                {
                    "Instrument": response["positions"][i]["instrument"],
                    "Long Units": response["positions"][i]["long"]["units"],
                    "Total Long P/L": response["positions"][i]["long"]["units"],
                    "Unrealized Long P/L": response["positions"][i]["long"][
                        "unrealizedPL"
                    ],
                    "Short Units": response["positions"][i]["short"]["units"],
                    "Total Short P/L": response["positions"][i]["short"]["pl"],
                    "Short Unrealized P/L": response["positions"][i]["short"][
                        "unrealizedPL"
                    ],
                }
            )

        df = pd.DataFrame.from_dict(position_data)
        print(df.to_string(index=False))
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


def get_open_trades(accountID, other_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="trades",
        description="Gets information about open trades.",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        request = trades.OpenTrades(accountID)
        response = client.request(request)
        try:
            df = pd.DataFrame.from_dict(response["trades"])
            df = df[
                [
                    "id",
                    "instrument",
                    "initialUnits",
                    "currentUnits",
                    "price",
                    "unrealizedPL",
                ]
            ]
            df = df.rename(
                columns={
                    "id": "ID",
                    "instrument": "Instrument",
                    "initialUnits": "Initial Units",
                    "currentUnits": "Current Units",
                    "price": "Entry Price",
                    "unrealizedPL": "Unrealized P/L",
                }
            )

            print(df.to_string(index=False))
            print("")

        except KeyError:
            print("No trades were found")
            print("")
    except V20Error as e:
        msg_length = len(e.msg)
        msg = e.msg[17 : msg_length - 2]
        print(msg)
        print("")


def close_trade(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="closetrade",
        description="Close a trade by id.",
    )
    parser.add_argument(
        "-i",
        "--id",
        dest="orderID",
        action="store",
        type=str,
        required=False,
        help="The Trade ID to close. ",
    )
    parser.add_argument(
        "-u",
        "--units",
        dest="units",
        action="store",
        required=False,
        help="The number of units on the trade to close. If not set it "
        + "defaults to all units. ",
    )
    if other_args:
        if "-i" not in other_args[0]:
            other_args.insert(0, "-i")
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    data = {}
    if ns_parser.units is not None:
        data["units"] = ns_parser.units
    try:
        request = trades.TradeClose(accountID, ns_parser.orderID, data)
        response = client.request(request)

        close_data = []
        close_data.append(
            {
                "OrderID": response["orderCreateTransaction"]["tradeClose"]["tradeID"],
                "Instrument": response["orderFillTransaction"]["instrument"],
                "Units": response["orderCreateTransaction"]["units"],
                "Price": response["orderFillTransaction"]["price"],
                "P/L": response["orderFillTransaction"]["pl"],
            }
        )
        df = pd.DataFrame.from_dict(close_data)
        print(df.to_string(index=False))
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")
    except Exception as e:
        print(e, "\n")


def show_candles(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="candles",
        description="Display Candle Data",
    )
    parser.add_argument(
        "-g",
        "--granularity",
        dest="granularity",
        action="store",
        type=str,
        default="D",
        required=False,
        help="The timeframe to get for the candle chart (Seconds: S5, S10, S15, S30 "
        + "Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12 "
        + "Day (default): D, Week: W Month: M",
    )
    parser.add_argument(
        "-c",
        "--count",
        dest="candlecount",
        action="store",
        default=180,
        type=int,
        required=False,
        help="The number of candles to retrieve. Default:180 ",
    )
    parser.add_argument(
        "-a",
        "--ad",
        dest="ad",
        action="store_true",
        help="Adds ad (Accumulation/Distribution Indicator) to the chart",
    )
    parser.add_argument(
        "-b",
        "--bbands",
        dest="bbands",
        action="store_true",
        help="Adds Bollinger Bands to the chart",
    )
    parser.add_argument(
        "-C",
        "--cci",
        dest="cci",
        action="store_true",
        help="Adds cci (Commodity Channel Index) to the chart",
    )
    parser.add_argument(
        "-e",
        "--ema",
        dest="ema",
        action="store_true",
        help="Adds ema (Exponential Moving Average) to the chart",
    )
    parser.add_argument(
        "-o",
        "--obv",
        dest="obv",
        action="store_true",
        help="Adds obv (On Balance Volume) to the chart",
    )
    parser.add_argument(
        "-r",
        "--rsi",
        dest="rsi",
        action="store_true",
        help="Adds rsi (Relative Strength Index) to the chart",
    )
    parser.add_argument(
        "-s",
        "--sma",
        dest="sma",
        action="store_true",
        help="Adds sma (Simple Moving Average) to the chart",
    )
    parser.add_argument(
        "-v",
        "--vwap",
        dest="vwap",
        action="store_true",
        help="Adds vwap (Volume Weighted Average Price) to the chart",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {}
    parameters["granularity"] = ns_parser.granularity.upper()
    parameters["count"] = ns_parser.candlecount
    try:
        instrument = format_instrument(instrument, "_")
        df = get_candles_dataframe(accountID, instrument, parameters)

        plots_to_add, legends, subplot_legends = add_plots(df, ns_parser)

        if gtff.USE_ION:
            plt.ion()

        # pylint: disable=W0612
        fig, ax = mpf.plot(
            df,
            type="candle",
            style="charles",
            volume=True,
            title=f"{instrument} {ns_parser.granularity}",
            returnfig=True,
            addplot=plots_to_add,
        )

        ax[0].set_title(f"{instrument} {ns_parser.granularity}")
        ax[0].legend(legends)
        # pylint: disable=C0200
        for i in range(0, len(subplot_legends), 2):
            ax[subplot_legends[i]].legend(subplot_legends[i + 1])

        print("")
    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")
    except TypeError as e:
        print(e)


def add_plots(df, ns_parser):
    panel_number = 2
    plots_to_add = []
    legends = []
    subplot_legends = []

    if ns_parser.ad:
        ad = ta.ad(df["High"], df["Low"], df["Close"], df["Volume"])
        ad_plot = mpf.make_addplot(ad, panel=panel_number)
        plots_to_add.append(ad_plot)
        subplot_legends.extend([panel_number * 2, ["AD"]])
        panel_number += 1

    if ns_parser.bbands:
        bbands = ta.bbands(df["Close"])
        bbands = bbands.drop("BBB_5_2.0", axis=1)
        bbands_plot = mpf.make_addplot(bbands, panel=0)
        plots_to_add.append(bbands_plot)
        legends.extend(["Lower BBand", "Middle BBand", "Upper BBand"])

    if ns_parser.cci:
        cci = ta.cci(df["High"], df["Low"], df["Close"])
        cci_plot = mpf.make_addplot(cci, panel=panel_number)
        plots_to_add.append(cci_plot)
        subplot_legends.extend([panel_number * 2, ["CCI"]])
        panel_number += 1

    if ns_parser.ema:
        ema = ta.ema(df["Close"])
        ema_plot = mpf.make_addplot(ema, panel=0)
        plots_to_add.append(ema_plot)
        legends.append("10 EMA")

    if ns_parser.rsi:
        rsi = ta.rsi(df["Close"])
        rsi_plot = mpf.make_addplot(rsi, panel=panel_number)
        plots_to_add.append(rsi_plot)
        subplot_legends.extend([panel_number * 2, ["RSI"]])
        panel_number += 1

    if ns_parser.obv:
        obv = ta.obv(df["Close"], df["Volume"])
        obv_plot = mpf.make_addplot(obv, panel=panel_number)
        plots_to_add.append(obv_plot)
        subplot_legends.extend([panel_number * 2, ["OBV"]])
        panel_number += 1

    if ns_parser.sma:
        sma_length = [20, 50]
        for length in sma_length:
            sma = ta.sma(df["Close"], length=length)
            sma_plot = mpf.make_addplot(sma, panel=0)
            plots_to_add.append(sma_plot)
            legends.append(f"{length} SMA")

    if ns_parser.vwap:
        vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
        vwap_plot = mpf.make_addplot(vwap, panel=0)
        plots_to_add.append(vwap_plot)
        legends.append("vwap")

    return plots_to_add, legends, subplot_legends


def calendar(instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="calendar",
        description="Show Calendar Data",
    )
    parser.add_argument(
        "-d",
        "--days",
        dest="days",
        action="store",
        type=int,
        default=7,
        required=False,
        help="The number of days to search for, up to 30 forward or backward "
        + "use negative numbers to search back. ",
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {"instrument": instrument, "period": str(ns_parser.days * 86400 * -1)}
    try:
        request = forexlabs.Calendar(params=parameters)
        response = client.request(request)

        l_data = []
        # pylint: disable=C0200
        for i in range(len(response)):
            if "forecast" in response[i]:
                forecast = response[i]["forecast"]
                if response[i]["unit"] != "Index":
                    forecast += response[i]["unit"]
            else:
                forecast = ""

            if "market" in response[i]:
                market = response[i]["market"]
                if response[i]["unit"] != "Index":
                    market += response[i]["unit"]
            else:
                market = ""

            if "actual" in response[i]:
                actual = response[i]["actual"]
                if response[i]["unit"] != "Index":
                    actual += response[i]["unit"]
            else:
                actual = ""

            if "previous" in response[i]:
                previous = response[i]["previous"]
                if response[i]["unit"] != "Index":
                    previous += response[i]["unit"]
            else:
                previous = ""

            if "impact" in response[i]:
                impact = response[i]["impact"]
            else:
                impact = ""

            l_data.append(
                {
                    "Title": response[i]["title"],
                    "Time": datetime.fromtimestamp(response[i]["timestamp"]),
                    "Impact": impact,
                    "Forecast": forecast,
                    "Market Forecast": market,
                    "Currency": response[i]["currency"],
                    "Region": response[i]["region"],
                    "Actual": actual,
                    "Previous": previous,
                }
            )

        print(pd.DataFrame(l_data).to_string(index=False))
        print("")

    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["message"], "\n")


# pylint: disable=W0613
# pylint: disable=R1710
def get_candles_dataframe(accountID, instrument, parameters):
    if not parameters:
        parameters = {
            "granularity": "D",
            "count": "1500",
        }
    try:
        request = instruments.InstrumentsCandles(instrument, params=parameters)
        response = client.request(request)
        candles_data = []
        for i in range(len(response["candles"])):
            candles_data.append(
                {
                    "Date": response["candles"][i]["time"][:10]
                    + " "
                    + response["candles"][i]["time"][11:19],
                    "Open": float(response["candles"][i]["mid"]["o"]),
                    "High": float(response["candles"][i]["mid"]["h"]),
                    "Low": float(response["candles"][i]["mid"]["l"]),
                    "Close": float(response["candles"][i]["mid"]["c"]),
                    "Volume": response["candles"][i]["volume"],
                }
            )
        df = pd.DataFrame(candles_data)
        df.set_index("Date", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df
    except V20Error as e:
        # pylint: disable=W0123
        d_error = eval(e.msg)
        print(d_error["errorMessage"], "\n")


# pylint: disable=R1710
def load(other_args: List[str]):
    """Load a forex instrument to use"""
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="load",
        description="Forex using oanda",
    )

    parser.add_argument(
        "-i",
        "--instrument",
        required=True,
        type=str,
        dest="instrument",
        help="Forex pair to use. ",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        print("")
        return ns_parser.instrument.upper()

    except Exception as e:
        print(e, "\n")
        return None


def book_plot(df, instrument, book_type):
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


# pylint: disable=R1710
def format_instrument(instrument, char):
    try:
        if char not in instrument:
            instrument_list = list(instrument)
            instrument_list.pop(3)
            if char == " ":
                instrument = "".join(map(str, instrument_list))
            else:
                instrument_list.insert(3, char)
                instrument = "".join(map(str, instrument_list))
        return instrument
    except TypeError:
        print("Please load an instrument")
        print("")
