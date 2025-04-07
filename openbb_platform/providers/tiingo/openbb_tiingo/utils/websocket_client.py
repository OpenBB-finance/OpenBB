"""
Tiingo WebSocket Client.

This file should be run as a script, and is intended to be run as a subprocess of TiingoWebSocketFetcher.

Keyword arguments are passed from the command line as space-delimited, `key=value`, pairs.

Required Keyword Arguments
--------------------------
    api_key: str
        The API key for the Polygon WebSocket.
    asset_type: str
        The asset type to subscribe to. Default is "crypto".
        Options: "stock", "crypto", "fx"
    symbol: str
        The symbol to subscribe to. Example: "AAPL" or "AAPL,MSFT". Use "*" to subscribe to all symbols.
    feed: str
        The feed to subscribe to. One of: "trade" or "trade_and_quote".
    results_file: str
        The path to the file where the results will be stored.

Optional Keyword Arguments
--------------------------
    table_name: str
        The name of the table to store the data in. Default is "records".
    limit: int
        The maximum number of rows to store in the database.
    connect_kwargs: dict
        Additional keyword arguments to pass directly to `websockets.connect()`.
        Example: {"ping_timeout": 300}
"""

import asyncio
import json
import signal
import sys
from datetime import datetime

import websockets
from openbb_core.provider.utils.errors import UnauthorizedError
from openbb_core.provider.utils.websockets.database import Database, DatabaseWriter
from openbb_core.provider.utils.websockets.helpers import (
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
)
from openbb_core.provider.utils.websockets.message_queue import MessageQueue
from openbb_tiingo.models.websocket_connection import TiingoWebSocketData
from pandas import to_datetime
from pydantic import ValidationError
from pytz import UTC
from websockets.asyncio.client import connect

URL_MAP = {
    "stock": "wss://api.tiingo.com/iex",
    "fx": "wss://api.tiingo.com/fx",
    "crypto": "wss://api.tiingo.com/crypto",
}

# These are the data array definitions.
IEX_FIELDS = [
    "type",
    "date",
    "timestamp",
    "symbol",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_price",
    "ask_size",
    "last_price",
    "last_size",
    "halted",
    "after_hours",
    "sweep_order",
    "oddlot",
    "nms_rule",
]
FX_FIELDS = [
    "type",
    "symbol",
    "date",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_price",
    "ask_size",
    "ask_price",
]
CRYPTO_TRADE_FIELDS = [
    "type",
    "symbol",
    "timestamp",
    "exchange",
    "last_size",
    "last_price",
]
CRYPTO_QUOTE_FIELDS = [
    "type",
    "symbol",
    "timestamp",
    "exchange",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_size",
    "ask_price",
]
SUBSCRIPTION_ID = ""
logger = get_logger("openbb.websocket.tiingo")
input_queue = MessageQueue(logger=logger)
db_queue = MessageQueue(logger=logger)
kwargs = parse_kwargs()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
ASSET_TYPE = kwargs.pop("asset_type", "crypto")
FEED = kwargs.pop("feed", "trade")


SUBSCRIBED_SYMBOLS: set = set()

THRESHOLD_LEVEL = (
    5
    if ASSET_TYPE == "fx" or FEED == "trade"
    else (2 if ASSET_TYPE == "crypto" and FEED == "trade_and_quote" else 0)
)

URL = URL_MAP.get(ASSET_TYPE)

if not kwargs.get("api_key"):
    raise ValueError("No API key provided.")


if not URL:
    raise ValueError("Invalid asset type provided.")

DATABASE = DatabaseWriter(
    database=Database(
        results_file=kwargs["results_file"],
        table_name=kwargs["table_name"],
        limit=kwargs.get("limit"),
        logger=logger,
    ),
    queue=db_queue,
)


# Subscribe and unsubscribe events are handled in a separate connection using the subscription_id set by the login event.
async def update_symbols(symbol, event):
    """Update the symbols to subscribe to."""
    if not SUBSCRIPTION_ID:
        logger.error(
            "PROVIDER ERROR:    Must be assigned a subscription ID to update symbols. Try logging in."
        )
        return

    update_event = {
        "eventName": event,
        "authorization": kwargs["api_key"],
        "eventData": {
            "subscriptionId": SUBSCRIPTION_ID,
            "tickers": symbol,
        },
    }

    async with connect(URL) as websocket:
        await websocket.send(json.dumps(update_event))
        response = await websocket.recv(decode=False)
        message = json.loads(response)
        if "tickers" in message.get("data", {}):
            tickers = message["data"]["tickers"]
            threshold_level = message["data"].get("thresholdLevel")
            msg = f"PROVIDER INFO:      Subscribed to {tickers} with threshold level {threshold_level}"
            logger.info(msg)

    symbols = symbol.split(",")
    if event == "subscribe":
        for sym in symbols:
            SUBSCRIBED_SYMBOLS.add(sym)
    elif event == "unsubscribe":
        for sym in symbols:
            SUBSCRIBED_SYMBOLS.discard(sym)

    kwargs["symbol"] = ",".join(SUBSCRIBED_SYMBOLS)


async def read_stdin_and_update_symbols():
    """Read from stdin and update symbols."""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        sys.stdin.flush()

        if not line:
            break

        if "qsize" in line:
            logger.info(
                f"PROVIDER INFO:      Input Queue : {input_queue.queue.qsize()}"
                f" Database Queue : {db_queue.queue.qsize()}"
            )
        else:
            line = json.loads(line.strip())

            if line:
                symbol = line.get("symbol")
                event = line.get("event")
                await update_symbols(symbol, event)


async def process_message(message):  # pylint: disable=too-many-branches
    """Process the message and write to the database."""
    result: dict = {}
    data_message: dict = {}
    message = message if isinstance(message, (dict, list)) else json.loads(message)
    msg: str = ""
    if message.get("messageType") == "E":
        response = message.get("response", {})
        msg = f"PROVIDER ERROR:     {response.get('code')}: {response.get('message')}"
        logger.error(msg)
        sys.exit(1)
    elif message.get("messageType") == "I":
        response = message.get("response", {})

        if response.get("code") != 200:
            msg = (
                f"PROVIDER ERROR:    {response.get('code')}: {response.get('message')}"
            )
            logger.error(msg)
            raise UnauthorizedError(msg)

        if response.get("code") == 200:
            msg = f"PROVIDER INFO:      Authorization: {response.get('message')}"
            logger.info(msg)
            if message.get("data", {}).get("subscriptionId"):
                global SUBSCRIPTION_ID  # noqa: PLW0603  # pylint: disable=global-statement
                SUBSCRIPTION_ID = message["data"]["subscriptionId"]

        if "tickers" in response.get("data", {}):
            tickers = message["data"]["tickers"]
            threshold_level = message["data"].get("thresholdLevel")
            msg = f"PROVIDER INFO:      Subscribed to {tickers} with threshold level {threshold_level}"
            logger.info(msg)
    elif message.get("messageType") == "A":
        data = message.get("data", [])
        service = message.get("service")

        if service == "iex":
            data_message = {IEX_FIELDS[i]: data[i] for i in range(len(data))}
            _ = data_message.pop("timestamp", None)
        elif service == "fx":
            data_message = {FX_FIELDS[i]: data[i] for i in range(len(data))}
        elif service == "crypto_data":

            if data[0] == "Q":
                data_message = {
                    CRYPTO_QUOTE_FIELDS[i]: data[i] for i in range(len(data))
                }
            elif data[0] == "T":
                data_message = {
                    CRYPTO_TRADE_FIELDS[i]: data[i] for i in range(len(data))
                }
            data_message["date"] = datetime.now(UTC).isoformat()
            tiingo_date = data_message.pop("tiingo_date", None)

            if isinstance(tiingo_date, str):
                tiingo_date = to_datetime(tiingo_date)
                tiingo_date = tiingo_date.tz_convert("America/New_York").to_pydatetime()
                data_message["timestamp"] = tiingo_date

    if data_message:
        try:
            result = TiingoWebSocketData.model_validate(data_message).model_dump_json(
                exclude_none=True, exclude_unset=True
            )
        except ValidationError as e:
            try:
                handle_validation_error(logger, e)
            except ValidationError:
                raise e from e

        if result:
            await db_queue.enqueue(result)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""

    tasks: set = set()
    ticker: list = []
    conn_kwargs = {
        "ping_interval": 8,
        "ping_timeout": 8,
        "close_timeout": 1,
    }
    conn_kwargs.update(CONNECT_KWARGS)

    if isinstance(kwargs["symbol"], str):
        ticker = kwargs["symbol"].lower().split(",")

    subscribe_event = {
        "eventName": "subscribe",
        "authorization": kwargs["api_key"],
        "eventData": {
            "thresholdLevel": THRESHOLD_LEVEL,
            "tickers": ticker,
        },
    }

    async def message_receiver(websocket):
        """Receive messages from the WebSocket."""
        while True:
            message = await websocket.recv(decode=False)
            input_queue.queue.put_nowait(json.loads(message))

    stdin_task = asyncio.create_task(read_stdin_and_update_symbols())
    tasks.add(stdin_task)

    try:
        await DATABASE.start_writer()

        async for websocket in connect(URL, **conn_kwargs):
            try:
                if not any(
                    task.name == "receiver_task"
                    for task in tasks
                    if hasattr(task, "name")
                ):
                    receiver_task = asyncio.create_task(
                        message_receiver(websocket), name="receiver_task"
                    )
                    tasks.add(receiver_task)

                await websocket.send(json.dumps(subscribe_event))
                logger.info("PROVIDER INFO:      WebSocket connection established.")
                for _ in range(9):
                    process_task = asyncio.create_task(
                        input_queue.process_queue(
                            lambda message: process_message(message)
                        )
                    )
                    tasks.add(process_task)

                await asyncio.gather(*tasks, return_exceptions=True)

            except UnauthorizedError as e:
                logger.error(str(e))
                sys.exit(1)

            except websockets.ConnectionClosed as e:
                msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
                logger.info(msg)
                # Attempt to reopen the connection
                logger.info("PROVIDER INFO:      Attempting to reconnect...")
                await asyncio.sleep(1)
                continue

    except websockets.WebSocketException as e:
        logger.info(str(e))
        sys.exit(0)

    except Exception as e:  # pylint: disable=broad-except
        msg = f"Unexpected error -> {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
        logger.error(msg)
        sys.exit(1)

    finally:
        for task in tasks:
            task.cancel()
            await task
        asyncio.gather(*tasks, return_exceptions=True)
        await DATABASE.stop_writer()
        sys.exit(0)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(lambda loop, context: None)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(signal.SIGTERM, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(
            connect_and_stream(),
            loop,
        )
        loop.run_forever()

    except (KeyboardInterrupt, websockets.ConnectionClosed):
        logger.error("PROVIDER ERROR:     WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        ERR = (
            f"PROVIDER ERROR:     Unexpected error -> "
            f"{e.__class__.__name__ if hasattr(e, '__class__') else e}: {e}"
        )
        logger.error(ERR)

    finally:
        loop.call_soon_threadsafe(loop.stop)
        loop.close()
        sys.exit(0)
