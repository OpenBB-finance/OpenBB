"""FMP WebSocket server."""

import asyncio
import json
import os
import signal
import sys

import websockets
from openbb_core.provider.utils.errors import UnauthorizedError
from openbb_tiingo.models.websocket_connection import TiingoWebSocketData
from openbb_websockets.helpers import (
    MessageQueue,
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
    write_to_db,
)
from pydantic import ValidationError

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
    "date",
    "exchange",
    "last_size",
    "last_price",
]
CRYPTO_QUOTE_FIELDS = [
    "type",
    "symbol",
    "date",
    "exchange",
    "bid_size",
    "bid_price",
    "mid_price",
    "ask_size",
    "ask_price",
]
SUBSCRIPTION_ID = ""
queue = MessageQueue()
logger = get_logger("openbb.websocket.tiingo")
kwargs = parse_kwargs()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})


# Subscribe and unsubscribe events are handled in a separate connection using the subscription_id set by the login event.
async def update_symbols(symbol, event):
    """Update the symbols to subscribe to."""
    url = kwargs["url"]

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

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(update_event))
        response = await websocket.recv()
        message = json.loads(response)
        if "tickers" in message.get("data", {}):
            tickers = message["data"]["tickers"]
            threshold_level = message["data"].get("thresholdLevel")
            msg = f"PROVIDER INFO:      Subscribed to {tickers} with threshold level {threshold_level}"
            logger.info(msg)


async def read_stdin_and_update_symbols():
    """Read from stdin and update symbols."""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        sys.stdin.flush()

        if not line:
            break

        line = json.loads(line.strip())

        if line:
            symbol = line.get("symbol")
            event = line.get("event")
            await update_symbols(symbol, event)


async def process_message(message, results_path, table_name, limit):
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
                global SUBSCRIPTION_ID  # noqa: PLW0603
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
            if data[0] == "T":
                data_message = {
                    CRYPTO_TRADE_FIELDS[i]: data[i] for i in range(len(data))
                }
            elif data[0] == "Q":
                data_message = {
                    CRYPTO_QUOTE_FIELDS[i]: data[i] for i in range(len(data))
                }
        else:
            return

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
            await write_to_db(result, results_path, table_name, limit)
    return


async def connect_and_stream(
    url, symbol, threshold_level, api_key, results_path, table_name, limit
):
    """Connect to the WebSocket and stream data to file."""

    handler_task = asyncio.create_task(
        queue.process_queue(
            lambda message: process_message(message, results_path, table_name, limit)
        )
    )

    stdin_task = asyncio.create_task(read_stdin_and_update_symbols())

    if isinstance(symbol, str):
        ticker = symbol.lower().split(",")

    subscribe_event = {
        "eventName": "subscribe",
        "authorization": api_key,
        "eventData": {
            "thresholdLevel": threshold_level,
            "tickers": ticker,
        },
    }
    connect_kwargs = CONNECT_KWARGS.copy()
    if "ping_timeout" not in connect_kwargs:
        connect_kwargs["ping_timeout"] = None
    if "close_timeout" not in connect_kwargs:
        connect_kwargs["close_timeout"] = None

    try:
        try:
            async with websockets.connect(url, **connect_kwargs) as websocket:
                logger.info("PROVIDER INFO:      WebSocket connection established.")
                await websocket.send(json.dumps(subscribe_event))
                while True:
                    message = await websocket.recv()
                    await queue.enqueue(message)

        except UnauthorizedError as e:
            logger.error(str(e))
            sys.exit(1)

    except websockets.ConnectionClosed as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
        logger.info(msg)
        # Attempt to reopen the connection
        logger.info("PROVIDER INFO:      Attempting to reconnect after five seconds...")
        await asyncio.sleep(5)
        await connect_and_stream(
            url, symbol, threshold_level, api_key, results_path, table_name, limit
        )

    except websockets.WebSocketException as e:
        logger.info(str(e))
        sys.exit(0)

    except Exception as e:
        msg = f"Unexpected error -> {e.__class__.__name__}: {e}"
        logger.error(msg)
        sys.exit(1)

    finally:
        handler_task.cancel()
        await handler_task
        stdin_task.cancel()
        await stdin_task
        sys.exit(0)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.add_signal_handler(signal.SIGTERM, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(
            connect_and_stream(
                kwargs["url"],
                kwargs["symbol"],
                kwargs["threshold_level"],
                kwargs["api_key"],
                os.path.abspath(kwargs["results_file"]),
                kwargs["table_name"],
                kwargs.get("limit", None),
            ),
            loop,
        )
        loop.run_forever()

    except Exception as e:  # pylint: disable=broad-except
        msg = f"Unexpected error -> {e.__class__.__name__}: {e}"
        logger.error(msg)

    finally:
        loop.stop()
        loop.close
        sys.exit(0)
