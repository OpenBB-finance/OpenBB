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
    parse_kwargs,
    write_to_db,
)

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
subscription_id = None
queue = MessageQueue()
logger = get_logger("openbb.websocket.tiingo")
kwargs = parse_kwargs()


# Subscribe and unsubscribe events are handled in a separate connection using the subscription_id set by the login event.
async def update_symbols(symbol, event):
    """Update the symbols to subscribe to."""
    url = kwargs["url"]

    if not subscription_id:
        logger.error(
            "PROVIDER ERROR:    Must be assigned a subscription ID to update symbols. Try logging in."
        )
        return

    update_event = {
        "eventName": event,
        "authorization": kwargs["api_key"],
        "eventData": {
            "subscriptionId": subscription_id,
            "tickers": symbol,
        },
    }

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(update_event))
        response = await websocket.recv()
        message = json.loads(response)
        if message.get("response", {}).get("code") != 200:
            logger.error(f"PROVIDER ERROR:     {message}")
        else:
            msg = (
                f"PROVIDER INFO:      {message.get('response', {}).get('message')}. "
                f"Subscribed to symbols: {message.get('data', {}).get('tickers')}"
            )
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
    result = {}
    data_message = {}
    message = json.loads(message)
    msg = ""
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
                global subscription_id

                subscription_id = message["data"]["subscriptionId"]

            if "tickers" in message.get("data", {}):
                tickers = message["data"]["tickers"]
                threshold_level = message["data"].get("thresholdLevel")
                msg = f"PROVIDER INFO:      Subscribed to {tickers} with threshold level {threshold_level}"
                logger.info(msg)
    elif message.get("messageType") == "A":
        data = message.get("data", [])
        service = message.get("service")
        if service == "iex":
            data_message = {IEX_FIELDS[i]: data[i] for i in range(len(data))}
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
        except Exception as e:
            msg = f"PROVIDER ERROR:    Error validating data: {e}"
            logger.error(msg)
            return
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
        "eventData": {"thresholdLevel": threshold_level, "tickers": ticker},
    }
    try:
        async with websockets.connect(
            url, ping_interval=20, ping_timeout=20, max_queue=1000
        ) as websocket:
            logger.info("PROVIDER INFO:      WebSocket connection established.")
            await websocket.send(json.dumps(subscribe_event))
            while True:
                message = await websocket.recv()
                await queue.enqueue(message)

    except websockets.ConnectionClosed as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e.reason}"
        logger.info(msg)
        # Attempt to reopen the connection
        await asyncio.sleep(5)
        await connect_and_stream(
            url, symbol, threshold_level, api_key, results_path, table_name, limit
        )

    except websockets.WebSocketException as e:
        logger.error(e)
        sys.exit(1)

    except Exception as e:
        msg = f"PROVIDER ERROR:    Unexpected error -> {e}"
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

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_termination_signal, logger)

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

    except (KeyboardInterrupt, websockets.ConnectionClosed):
        logger.error("PROVIDER ERROR:    WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        msg = f"PROVIDER ERROR:    {e.args[0]}"
        logger.error(msg)

    finally:
        sys.exit(0)
