import argparse
from oandapyV20 import API
from typing import List
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.trades as trades
from oandapyV20.exceptions import V20Error
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

client = API(access_token=cfg.OANDA_TOKEN, environment="live")
account = cfg.OANDA_ACCOUNT


def get_fx_price(accountID, other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="getfxprice",
        description="Get price for forex",
    )
    parser.add_argument(
    "-i",
    "--instrument",
    dest="instrument",
    action="store",
    required=True
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        parameters = {
            "instruments": ns_parser.instrument
        }
        request = pricing.PricingInfo(accountID=accountID, params=parameters)
        response = client.request(request)
        bid = response["prices"][0]["bids"][0]["price"]
        ask = response["prices"][0]["asks"][0]["price"]
        print(ns_parser.instrument + " Bid: " + bid)
        print(ns_parser.instrument + " Ask: " + ask)
    except V20Error as e:
        print(e)
    except NameError as e:
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
    print(f"Margin Available:  {margin_available}")
    print(f"Margin Used: {margin_used}")
    print(f"Margin Closeout {margin_closeout}")
    print(f"Margin Closeout Percent: {margin_closeout_percent}")
    print(f"Margin Closeout Position Value: {margin_closeout_position_value}")


def list_orders(accountID, other_args: List [str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="listorders",
        description="List order history",
    )
    parser.add_argument(
    "-s",
    "--state",
    dest="state",
    action="store",
    default="ALL",
    required=False
    )
    parser.add_argument(
    "-c",
    "--count",
    dest="count",
    action="store",
    default=50,
    required=False
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {
#         "state": ns_parser.state,
#         "count": ns_parser.count,
    }
    if ns_parser.state is not None:
        parameters["state"] = ns_parser.state
    if ns_parser.count is not None:
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
            print("-"*30)
        except KeyError:
            continue
        except IndexError:
            break


def get_order_book(other_args: List [str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="get_order_book",
        description="Get Order book",
    )
    parser.add_argument(
    "-i",
    "--instrument",
    dest="instrument",
    action="store",
    required=True
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    parameters = {
        "bucketWidth": 0.1
    }
    request = instruments.InstrumentsOrderBook(instrument=ns_parser.instrument, params=parameters)
    response = client.request(request)

    for i in range(400, 700, 1):
        order_instrument = response["orderBook"]["instrument"]
        price = response["orderBook"]["buckets"][i]["price"]
        short_count_percent = response["orderBook"]["buckets"][i]["shortCountPercent"]
        long_count_percent = response["orderBook"]["buckets"][i]["longCountPercent"]
        print(f"Instrument: {order_instrument}")
        print(f"Price: {price}")
        print(f"Short count percent: {short_count_percent}")
        print(f"Long count percent: {long_count_percent}")
        print("-"*30)


def get_position_book(other_args: List [str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="get_position_book ",
        description="Get Position Book",
    )
    parser.add_argument(
        "-i",
        "--instrument",
        dest="instrument",
        action="store",
        required=True
        )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    parameters = {
        "bucketWidth": 0.1
    }
    request = instruments.InstrumentsPositionBook (instrument=ns_parser.instrument, params=parameters)
    response = client.request(request)

    for i in range(200,400,1):
        order_instrument = response["positionBook"]["instrument"]
        price = response["positionBook"]["buckets"][i]["price"]
        short_count_percent = response["positionBook"]["buckets"][i]["shortCountPercent"]
        long_count_percent = response["positionBook"]["buckets"][i]["longCountPercent"]
        print(f"Instrument: {order_instrument}")
        print(f"Price: {price}")
        print(f"Short count percent: {short_count_percent}")
        print(f"Long count percent: {long_count_percent}")
        print("-"*30)


def create_limit_order(accountID, instrument, other_args: List[str]):
    parser = argparse.ArgumentParser(
    add_help=False,
    prog="create_limit_order",
    description="Create limit order",
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
        "order":{
            "price": ns_parser.price,
            "instrument": instrument,
            "units": ns_parser.units,
            "type": "LIMIT",
            "timeInForce":"GTC",
            "positionFill": "DEFAULT"
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
    for i in range(0,25,1):
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
            print("-"*30)
        except IndexError:
            break


def get_open_positions(accountID):
    request = positions.OpenPositions(accountID)
    response = client.request(request)
    for i in range(0,100,1):
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
            print(f"Long P/L: {long_pl}")
            print(f"Long Unrealized P/L: {long_upl}\n")
            print(f"Short Units: {short_units}")
            print(f"Short P/L: {short_pl}")
            print(f"Short Unrealized P/L: {short_upl}")
            print("-"*30+"\n")
        except IndexError:
            break


def get_open_trades(accountID):
    request = trades.OpenTrades(accountID)
    response = client.request(request)
    for i in range (0,100,1):
        try:
            order_id = response["trades"][i]["id"]
            instrument = response["trades"][i]["instrument"]
            initial_units = response["trades"][i]["initialUnits"]
            current_units = response["trades"][i]["currentUnits"]
            price = response["trades"][i]["price"]
            unrealized_pl = response["trades"][i]["unrealizedPL"]
            print(f"Order ID: {order_id}\n")
            print(f"Instrument: {instrument}")
            print(f"Initial Units: {initial_units}")
            print(f"Current Units: {current_units}")
            print(f"Price: {price}")
            print(f"Unrealized P/L: {unrealized_pl}")
            print("-"*30+"\n")
        except IndexError:
            break






def close_trade(accountID, other_args: List[str]):
    parser = ArgumentParser(
        add_help = False,
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
    data={
        "units": ns_parser.units,
        }
    try:
        request = trades.TradeClose(accountID, ns_parser.orderID, data)
        response = client.request(request)
    except V20Error as e:
        print(e)
