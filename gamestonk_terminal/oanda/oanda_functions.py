import argparse
from oandapyV20 import API
from typing import List
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.forexlabs as labs
from oandapyV20.exceptions import V20Error
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf


client = API(access_token=cfg.OANDA_TOKEN, environment="live")
account = cfg.OANDA_ACCOUNT


def get_fx_price(accountID, instrument):
    try:
        parameters = {"instruments": instrument}
        request = pricing.PricingInfo(accountID=accountID, params=parameters)
        response = client.request(request)
        bid = response["prices"][0]["bids"][0]["price"]
        ask = response["prices"][0]["asks"][0]["price"]
        print(instrument + " Bid: " + bid)
        print(instrument + " Ask: " + ask)
    except V20Error as e:
        print(e)


def get_account_summary(accountID):
    request = accounts.AccountSummary(accountID=accountID)
    response = client.request(request)
    balance = response["account"]["balance"]
    margin_available = response["account"]["marginAvailable"]
    margin_closeout = response["account"]["marginCloseoutNAV"]
    margin_closeout_percent = response["account"]["marginCloseoutPercent"]
    margin_closeout_position_value = response["account"]["marginCloseoutPositionValue"]
    margin_used = response["account"]["marginUsed"]
    net_asset_value = response["account"]["NAV"]
    open_trade_count = response["account"]["openTradeCount"]
    total_pl = response["account"]["pl"]
    unrealized_pl = response["account"]["unrealizedPL"]

    print(f"Balance: {balance}")
    print(f"NAV: {net_asset_value}")
    print(f"Unrealized P/L:  {unrealized_pl}")
    print(f"Total P/L: {total_pl}")
    print(f"Open Trade Count: {open_trade_count}")
    print(f"Margin Available:  ${margin_available}")
    print(f"Margin Used: ${margin_used}")
    print(f"Margin Closeout {margin_closeout}")
    print(f"Margin Closeout Percent: {margin_closeout_percent}")
    print(f"Margin Closeout Position Value: {margin_closeout_position_value}")


def list_orders(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="listorders",
        description="List order history",
    )
    parser.add_argument(
        "-s", "--state", dest="state", action="store", default="ALL", required=False
    )
    parser.add_argument(
        "-c", "--count", dest="count", action="store", default=50, required=False
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {
    }
    parameters["state"] = ns_parser.state
    parameters["count"] = ns_parser.count

    request = orders.OrderList(accountID, parameters)
    response = client.request(request)
    for i in range(0, int(ns_parser.count), 1):
        try:
            order_id = response["orders"][i]["id"]
            instrument = response["orders"][i]["instrument"]
            units = response["orders"][i]["units"]
            order_state = response["orders"][i]["state"]
            order_type = response["orders"][i]["type"]

            print(f"Order id: {order_id}")
            print(f"Instrument: {instrument}")
            print(f"Units: {units}")
            print(f"Order State: {order_state}")
            print(f"Order Type: {order_type}")
            print("-" * 30)
        except KeyError:
            continue
        except IndexError:
            break


def get_order_book(instrument):
    try:
        request = instruments.InstrumentsOrderBook(instrument=instrument)
        response = client.request(request)
        for i in range(len(response["orderBook"]["buckets"])):
            order_instrument = response["orderBook"]["instrument"]
            price = response["orderBook"]["buckets"][i]["price"]
            short_count_percent = response["orderBook"]["buckets"][i]["shortCountPercent"]
            long_count_percent = response["orderBook"]["buckets"][i]["longCountPercent"]
            print(f"Instrument: {order_instrument}")
            print(f"Price: {price}")
            print(f"Short count percent: {short_count_percent}")
            print(f"Long count percent: {long_count_percent}")
            print("-" * 30)
    except V20Error as e:
        print(e)


def get_position_book(instrument):
    try:
        request = instruments.InstrumentsPositionBook(instrument=instrument)
        response = client.request(request)
        for i in range(len(response["positionBook"]["buckets"])):
            order_instrument = response["positionBook"]["instrument"]
            price = response["positionBook"]["buckets"][i]["price"]
            short_count_percent = response["positionBook"]["buckets"][i][ "shortCountPercent" ]
            long_count_percent = response["positionBook"]["buckets"][i]["longCountPercent"]
            print(f"Instrument: {order_instrument}")
            print(f"Price: {price}")
            print(f"Short count percent: {short_count_percent}")
            print(f"Long count percent: {long_count_percent}")
            print("-" * 30)
    except V20Error as e:
        print(e)


def create_order(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="create_order",
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
    )
    parser.add_argument(
        "-p",
        "--price",
        dest="price",
        action="store",
        type=float,
        required=True,
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

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
    request = orders.OrderCreate(accountID, data)
    response = client.request(request)
    print(response)


def cancel_pending_order(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="cancelpendingorder",
        description="Cancel Pending Order",
    )
    parser.add_argument(
        "-i",
        "--id",
        dest="orderID",
        action="store",
        type=str,
        required=True,
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    try:
        request = orders.OrderCancel(accountID, ns_parser.orderID)
        client.request(request)
    except V20Error as e:
        print(e)


def get_pending_orders(accountID):
    request = orders.OrdersPending(accountID)
    response = client.request(request)
    for i in range(len(response["orders"])):
        try:
            order_id = response["orders"][i]["id"]
            instrument = response["orders"][i]["instrument"]
            price = response["orders"][i]["price"]
            units = response["orders"][i]["units"]
            create_time = response["orders"][i]["createTime"]
            time_in_force = response["orders"][i]["timeInForce"]
            print(f"Order ID: {order_id}")
            print(f"Instrument: {instrument}")
            print(f"Price: {price}")
            print(f"Units: {units}")
            print(f"Time created: {create_time}")
            print(f"Time in force: {time_in_force}")
            print("-" * 30)
        except IndexError:
            break


def get_open_positions(accountID):
    request = positions.OpenPositions(accountID)
    response = client.request(request)
    for i in range(0, 100, 1):
        try:
            instrument = response["positions"][i]["instrument"]
            long_units = response["positions"][i]["long"]["units"]
            long_pl = response["positions"][i]["long"]["pl"]
            long_upl = response["positions"][i]["long"]["unrealizedPL"]
            short_units = response["positions"][i]["short"]["units"]
            short_pl = response["positions"][i]["short"]["pl"]
            short_upl = response["positions"][i]["short"]["unrealizedPL"]
            print(f"Instrument: {instrument}\n")
            print(f"Long Units: {long_units}")
            print(f"Total Long P/L: {long_pl}")
            print(f"Long Unrealized P/L: {long_upl}\n")
            print(f"Short Units: {short_units}")
            print(f"Total Short P/L: {short_pl}")
            print(f"Short Unrealized P/L: {short_upl}")
            print("-" * 30 + "\n")
        except IndexError:
            break


def get_open_trades(accountID):
    request = trades.OpenTrades(accountID)
    response = client.request(request)
    for i in range(len(response["trades"])):
        try:
            order_id = response["trades"][i]["id"]
            instrument = response["trades"][i]["instrument"]
            initial_units = response["trades"][i]["initialUnits"]
            current_units = response["trades"][i]["currentUnits"]
            price = response["trades"][i]["price"]
            unrealized_pl = response["trades"][i]["unrealizedPL"]
            print(f"Order ID: {order_id}")
            print(f"Instrument: {instrument}")
            print(f"Initial Units: {initial_units}")
            print(f"Current Units: {current_units}")
            print(f"Entry Price: {price}")
            print(f"Unrealized P/L: {unrealized_pl}")
            print("-" * 30 + "\n")
        except IndexError:
            break


def close_trade(accountID, other_args: List[str]):
    parser = ArgumentParser(
        add_help=False,
        prog="close_trade",
        description="close a trade",
    )
    parser.add_argument(
        "-i",
        "--id",
        dest="orderID",
        action="store",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-u",
        "--units",
        dest="units",
        action="store",
        type=str,
        required=False,
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    data = {
        "units": ns_parser.units,
    }
    try:
        request = trades.TradeClose(accountID, ns_parser.orderID, data)
        response = client.request(request)
    except V20Error as e:
        print(e)


def show_candles(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
            add_help=False,
            prog="show_candles",
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
        )
    parser.add_argument(
        "-c",
        "--count",
        dest="candlecount",
        action="store",
        default=180,
        type=int,
        required=False,
        )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {
    }
    parameters["granularity"] = ns_parser.granularity
    parameters["count"] = ns_parser.candlecount
    try:
        request = instruments.InstrumentsCandles(instrument, params=parameters)
        response = client.request(request)
        process_response(response)
        oanda_fix_date(".temp_candles.csv")
        df = pd.read_csv(".candles.csv", index_col=0)
        df.index = pd.to_datetime(df.index)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        mpf.plot(df, type="candle", style="charles", volume=True)
    except Exception as e:
        print(e)
    except NameError as e:
        print(e)


def process_response(response):
    with open(".temp_candles.csv", 'w') as out:
        for i in range(len(response["candles"])):
            time = response["candles"][i]["time"]
            volume = response["candles"][i]["volume"]
            o = response["candles"][i]["mid"]["o"]
            h = response["candles"][i]["mid"]["h"]
            l = response["candles"][i]["mid"]["l"]
            c = response["candles"][i]["mid"]["c"]
            out.write(str(time) + "," + str(o) + "," + str(h) + "," + str(l) + "," + str(c) + "," + str(volume) + "\n")


def oanda_fix_date(file):
    with open(file, 'r') as candle_file:
        lines = candle_file.readlines()
        with open(".candles.csv", 'w') as out:
            out.write("Datetime, Open, High, Low, Close, Volume\n")
        for line in lines:
            with open(".candles.csv", "a") as output:
                output.write(line[:10] + " " + line[11:19] + line[30:])


def calendar(instrument):
    parameters = {
        "instrument": instrument,
        "period": "604800"
    }
    request = labs.Calendar(params=parameters)
    response = client.request(request)
#     print(response)
    for i in range(len(response)):
        if "title" in response[i]:
            title = response[i]["title"]
            print(f"Title: {title}")
        if "impact" in response[i]:
            impact = response[i]["impact"]
            print(f"Impact: {impact}")
        if "market" in response[i]:
            market = response[i]["market"]
            unit = response[i]["unit"]
            if unit != "Index":
                print(f"Market Forecast: {market}{unit}")
            else:
                print(f"Market Forecast: {market}")
        if "currency" in response[i]:
            currency = response[i]["currency"]
            print(f"Currency: {currency}")
        if "region" in response[i]:
            region = response[i]["region"]
            print(f"Region: {region}")
        if "actual" in response[i]:
            actual = response[i]["actual"]
            unit = response[i]["unit"]
            if unit != "Index":
                print(f"Actual: {actual}{unit}")
            else:
                print(f"Actual: {actual}")
        if "previous" in response[i]:
            previous = response[i]["previous"]
            unit = response[i]["unit"]
            if unit != "Index":
                print(f"Previous: {previous}{unit}")
            else:
                print(f"Previous: {previous}")
        print("-"*30)


def load(other_args: List[str]):
    """Load a forex instrument to use"""
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Forex",
        description = "Forex using oanda",
    )

    parser.add_argument(
    "-i",
    "--instrument",
    required=True,
    type=str,
    dest="instrument",
    help="Instrument to use for function calls"
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return
        return ns_parser.instrument.upper()
    except Exception as e:
        print(e)
