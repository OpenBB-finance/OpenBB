"""Oanda Model."""
__docformat__ = "numpy"

import json
import logging
from datetime import datetime
from typing import Dict, Union

import pandas as pd
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

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

current_user = get_current_user()

if current_user.credentials.OANDA_ACCOUNT_TYPE != "REPLACE_ME":
    try:
        client = API(
            access_token=current_user.credentials.OANDA_TOKEN,
            environment=current_user.credentials.OANDA_ACCOUNT_TYPE,
        )
    except KeyError:
        client = None
else:
    client = None
account = current_user.credentials.OANDA_ACCOUNT


@log_start_end(log=logger)
def fx_price_request(
    accountID: str = account, instrument: Union[str, None] = None
) -> Union[Dict[str, str], bool]:
    """Request price for a forex pair.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    instrument : Union[str, None]
        The loaded currency pair, by default None

    Returns
    -------
    Union[Dict[str, str], bool]
        The currency pair price or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    try:
        parameters = {"instruments": instrument}
        request = pricing.PricingInfo(accountID=accountID, params=parameters)
        response = client.request(request)
        return response
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def account_summary_request(accountID: str = account) -> Union[pd.DataFrame, bool]:
    """Request Oanda account summary.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Account summary data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    if client is None:
        return False

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
        return df_summary
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def orderbook_plot_data_request(
    instrument: Union[str, None] = None, accountID: str = account
) -> Union[pd.DataFrame, bool]:
    """Request order book data for plotting.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Order book data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    parameters = {"bucketWidth": "1"}

    if client is None:
        return False

    try:
        request = instruments.InstrumentsOrderBook(
            instrument=instrument, params=parameters
        )
        response = client.request(request)
        df_orderbook_data = pd.DataFrame.from_dict(response["orderBook"]["buckets"])
        return df_orderbook_data
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def positionbook_plot_data_request(
    instrument: Union[str, None] = None, accountID: str = account
) -> Union[pd.DataFrame, bool]:
    """Request position book data for plotting.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Position book data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    if client is None:
        return False

    try:
        request = instruments.InstrumentsPositionBook(instrument=instrument)
        response = client.request(request)
        df_positionbook_data = pd.DataFrame.from_dict(
            response["positionBook"]["buckets"]
        )
        return df_positionbook_data
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def order_history_request(
    order_state: str = "PENDING", order_count: int = 0, accountID: str = account
) -> Union[pd.DataFrame, bool]:
    """Request the orders list from Oanda.

    Parameters
    ----------
    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    parameters: Dict[str, Union[str, int]] = {}
    parameters["state"] = order_state
    parameters["count"] = order_count

    if client is None:
        return False

    try:
        request = orders.OrderList(accountID, parameters)
        response = client.request(request)

        df_order_list = pd.DataFrame.from_dict(response["orders"])
        df_order_list = df_order_list[
            ["id", "instrument", "units", "price", "state", "type"]
        ]
        return df_order_list
    except KeyError:
        logger.exception("No orders were found")
        console.print("No orders were found\n")
        return False
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def create_order_request(
    price: int = 0,
    units: int = 0,
    instrument: Union[str, None] = None,
    accountID: str = account,
) -> Union[pd.DataFrame, bool]:
    """Request creation of buy/sell trade order.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Orders data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    price = (
        round(price, 3)
        if "JPY" in instrument or "THB" in instrument or "HUF" in instrument
        else round(price, 5)
    )
    data = {
        "order": {
            "price": price,
            "instrument": instrument,
            "units": units,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "positionFill": "DEFAULT",
        }
    }

    if client is None:
        return False

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
        df_orders = pd.DataFrame.from_dict(order_data)
        return df_orders
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False
    except Exception as e:
        logger.exception(str(e))
        console.print(e)
        return False


@log_start_end(log=logger)
def cancel_pending_order_request(
    orderID: str, accountID: str = account
) -> Union[str, bool]:
    """Request cancellation of a pending order.

    Parameters
    ----------
    orderID : str
        The pending order ID to cancel.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False

    if client is None:
        return False

    try:
        request = orders.OrderCancel(accountID, orderID)
        response = client.request(request)
        order_id = response["orderCancelTransaction"]["orderID"]
        return order_id
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def open_positions_request(accountID: str = account) -> Union[pd.DataFrame, bool]:
    """Request information on open positions.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False

    if client is None:
        return False

    try:
        request = positions.OpenPositions(accountID)
        response = client.request(request)
        position_data = [
            {
                "Instrument": response["positions"][i]["instrument"],
                "Long Units": response["positions"][i]["long"]["units"],
                "Total Long P/L": response["positions"][i]["long"]["units"],
                "Unrealized Long P/L": response["positions"][i]["long"]["unrealizedPL"],
                "Short Units": response["positions"][i]["short"]["units"],
                "Total Short P/L": response["positions"][i]["short"]["pl"],
                "Short Unrealized P/L": response["positions"][i]["short"][
                    "unrealizedPL"
                ],
            }
            for i in range(len(response["positions"]))
        ]

        df_positions = pd.DataFrame.from_dict(position_data)
        return df_positions
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def pending_orders_request(accountID: str = account) -> Union[pd.DataFrame, bool]:
    """Request information on pending orders.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Pending orders data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False

    if client is None:
        return False

    try:
        request = orders.OrdersPending(accountID)
        response = client.request(request)
        pending_data = [
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
            for i in range(len(response["orders"]))
        ]

        if len(pending_data) == 0:
            return pd.DataFrame()
        df_pending = pd.DataFrame.from_dict(pending_data)
        return df_pending
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def open_trades_request(accountID: str = account) -> Union[pd.DataFrame, bool]:
    """Request open trades data.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Open trades data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False

    if client is None:
        return False

    try:
        request = trades.OpenTrades(accountID)
        response = client.request(request)
        if "trades" in response and len(response["trades"]) > 0:
            df_trades = pd.DataFrame.from_dict(response["trades"])
            df_trades = df_trades[
                [
                    "id",
                    "instrument",
                    "initialUnits",
                    "currentUnits",
                    "price",
                    "unrealizedPL",
                ]
            ]
            df_trades = df_trades.rename(
                columns={
                    "id": "ID",
                    "instrument": "Instrument",
                    "initialUnits": "Initial Units",
                    "currentUnits": "Current Units",
                    "price": "Entry Price",
                    "unrealizedPL": "Unrealized P/L",
                }
            )
        else:
            df_trades = pd.DataFrame()
        return df_trades
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def close_trades_request(
    orderID: str, units: Union[int, None] = 0, accountID: str = account
) -> Union[pd.DataFrame, bool]:
    """Close a trade.

    Parameters
    ----------
    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Close trades data or False
    """
    if accountID == "REPLACE_ME":
        console.print("Error: Oanda account credentials are required.")
        return False
    data = {}
    if units is not None:
        data["units"] = units

    if client is None:
        return False

    try:
        request = trades.TradeClose(accountID, orderID, data)
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
        if len(close_data) == 0:
            return pd.DataFrame()
        df_trades = pd.DataFrame.from_dict(close_data)
        return df_trades
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def get_candles_dataframe(
    instrument: Union[str, None] = None, granularity: str = "D", candlecount: int = 180
) -> Union[pd.DataFrame, bool]:
    """Request data for candle chart.

    Parameters
    ----------
    instrument : str
        Loaded currency pair code
    granularity : str, optional
        Data granularity, by default "D"
    candlecount : int, optional
        Limit for the number of data points, by default 180

    Returns
    -------
    Union[pd.DataFrame, bool]
        Candle chart data or False
    """
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    parameters = {
        "granularity": granularity,
        "count": candlecount,
    }

    if client is None:
        return False

    try:
        request = instruments.InstrumentsCandles(instrument, params=parameters)
        response = client.request(request)
        candles_data = [
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
            for i in range(len(response["candles"]))
        ]

        if len(candles_data) == 0:
            df_candles = pd.DataFrame()
        else:
            df_candles = pd.DataFrame(candles_data)
            df_candles.set_index("Date", inplace=True)
            df_candles.index = pd.to_datetime(df_candles.index)
        return df_candles
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["errorMessage"], "\n")
        return False


@log_start_end(log=logger)
def get_calendar_request(
    days: int = 14, instrument: Union[str, None] = None
) -> Union[pd.DataFrame, bool]:
    """Request data of significant events calendar.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    days : int
        Number of days in advance

    Returns
    -------
    Union[pd.DataFrame, bool]
        Calendar events data or False
    """
    if instrument is None:
        console.print(
            "Error: An instrument should be loaded before running this command."
        )
        return False
    parameters = {"instrument": instrument, "period": str(days * 86400 * -1)}

    if client is None:
        return False

    try:
        request = forexlabs.Calendar(params=parameters)
        response = client.request(request)
    except V20Error as e:
        logger.exception(str(e))
        d_error = json.loads(e.msg)
        console.print(d_error["message"], "\n")
        return False

    l_data = []
    for i in enumerate(response):
        if "forecast" in response[i[0]]:
            forecast = response[i[0]]["forecast"]
            if response[i[0]]["unit"] != "Index":
                forecast += response[i[0]]["unit"]
        else:
            forecast = ""

        if "market" in response[i[0]]:
            market = response[i[0]]["market"]
            if response[i[0]]["unit"] != "Index":
                market += response[i[0]]["unit"]
        else:
            market = ""

        if "actual" in response[i[0]]:
            actual = response[i[0]]["actual"]
            if response[i[0]]["unit"] != "Index":
                actual += response[i[0]]["unit"]
        else:
            actual = ""

        if "previous" in response[i[0]]:
            previous = response[i[0]]["previous"]
            if response[i[0]]["unit"] != "Index":
                previous += response[i[0]]["unit"]
        else:
            previous = ""

        impact = response[i[0]]["impact"] if "impact" in response[i[0]] else ""

        l_data.append(
            {
                "Title": response[i[0]]["title"],
                "Time": datetime.fromtimestamp(response[i[0]]["timestamp"]),
                "Impact": impact,
                "Forecast": forecast,
                "Market Forecast": market,
                "Currency": response[i[0]]["currency"],
                "Region": response[i[0]]["region"],
                "Actual": actual,
                "Previous": previous,
            }
        )
    df_calendar = pd.DataFrame() if len(l_data) == 0 else pd.DataFrame(l_data)
    return df_calendar
