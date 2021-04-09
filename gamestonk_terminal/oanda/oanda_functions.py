import argparse
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
from gamestonk_terminal import config_terminal as cfg

client = API(access_token=cfg.OANDA_TOKEN, environment="live")
account = cfg.OANDA_ACCOUNT


def get_fx_price(accountID, instrument):
    parameters = {
        "instruments": instrument
    }
    request = pricing.PricingInfo(accountID=accountID, params=parameters)
    response = client.request(request)
    bid = response["prices"][0]["bids"][0]["price"]
    ask = response["prices"][0]["asks"][0]["price"]
    print(instrument + " Bid: " + bid)
    print(instrument + " Ask: " + ask)


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


def list_orders(accountID, state="ALL", count="50"):
    parameters = {
        "state": state,
        "count": count
    }
    request = orders.OrderList(accountID, parameters) 
    response = client.request(request)
    for i in range(0, int(count), 1):
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
            print("")
        except KeyError as e:
            print(f"Key error: {e} not found \n")
            continue
        except IndexError as e:
            print(e)
            break


