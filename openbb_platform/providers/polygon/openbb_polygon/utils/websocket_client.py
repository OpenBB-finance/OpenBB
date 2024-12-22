"""Polygon WebSocket client."""

import asyncio
import json
import os
import signal
import sys

import websockets
from openbb_core.provider.utils.websockets.database import Database
from openbb_core.provider.utils.websockets.helpers import (
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
)
from openbb_core.provider.utils.websockets.message_queue import MessageQueue
from openbb_polygon.models.websocket_connection import (
    FEED_MAP,
    PolygonWebSocketData,
)
from pydantic import ValidationError

URL_MAP = {
    "stock": "wss://socket.polygon.io/stocks",
    "stock_delayed": "wss://delayed.polygon.io/stocks",
    "options": "wss://socket.polygon.io/options",
    "options_delayed": "wss://delayed.polygon.io/options",
    "fx": "wss://socket.polygon.io/forex",
    "crypto": "wss://socket.polygon.io/crypto",
    "index": "wss://socket.polygon.io/indices",
    "index_delayed": "wss://delayed.polygon.io/indices",
}

logger = get_logger("openbb.websocket.polygon")
queue = MessageQueue(logger=logger, backoff_factor=2)
command_queue = MessageQueue(logger=logger)

kwargs = parse_kwargs()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
FEED = kwargs.pop("feed", None)
ASSET_TYPE = kwargs.pop("asset_type", "crypto")
kwargs["results_file"] = os.path.abspath(kwargs.get("results_file"))
URL = URL_MAP.get(ASSET_TYPE)

if not URL:
    raise ValueError("Invalid asset type provided.")

DATABASE = Database(
    results_file=kwargs["results_file"],
    table_name=kwargs["table_name"],
    limit=kwargs.get("limit"),
    logger=logger,
)


async def handle_symbol(symbol):
    """Handle the symbol and map it to the correct format."""
    symbols = symbol.split(",") if isinstance(symbol, str) else symbol
    new_symbols: list = []
    feed = FEED_MAP.get(ASSET_TYPE, {}).get(FEED)
    for s in symbols:

        if ASSET_TYPE in ["options", "options_delayed"] and "*" in s:
            symbol_error = (
                f"SymbolError -> {symbol}: Options symbols do not support wildcards."
            )
            logger.error(symbol_error)
            continue

        if s == "*":
            new_symbols.append(f"{feed}.*")
            continue

        if "." in s:
            _check = s.split(".")[0]
            if _check not in list(FEED_MAP.get(ASSET_TYPE, {}).values()):
                raise ValueError(
                    f"SymbolError -> Invalid feed, {_check}, for asset type, {ASSET_TYPE}"
                )

        ticker = s.upper()

        if ticker and "." not in ticker:
            ticker = f"{feed}.{ticker}"

        if ASSET_TYPE == "crypto" and "-" not in ticker and "*" not in ticker:
            ticker = ticker[:-3] + "-" + ticker[-3:]
        elif ASSET_TYPE == "fx" and "/" not in ticker and "*" not in ticker:
            ticker = ticker[:-3] + "/" + ticker[-3:]
        elif ASSET_TYPE == "fx" and "-" in ticker:
            ticker = ticker.replace("-", "/")
        elif (
            ASSET_TYPE in ["index", "index_delayed"]
            and ":" not in ticker
            and "*" not in ticker
        ):
            _feed, _ticker = ticker.split(".") if "." in ticker else (feed, ticker)
            ticker = f"{_feed}.I:{_ticker}"
        elif ASSET_TYPE in ["options", "options_delayed"] and ":" not in ticker:
            _feed, _ticker = ticker.split(".") if "." in ticker else (feed, ticker)
            ticker = f"{_feed}.O:{_ticker}"

        if ticker == "XL2.*":
            symbol_error = f"SymbolError -> {symbol}: L2 Crypto does not support the all-symbols wildcard."
            logger.error(symbol_error)
        else:
            new_symbols.append(ticker)

    return ",".join(new_symbols)


async def login(websocket):
    """Login to the WebSocket."""
    login_event = f'{{"action":"auth","params":"{kwargs["api_key"]}"}}'
    try:
        await websocket.send(login_event)
        res = await websocket.recv()
        response = json.loads(res)
        messages = response if isinstance(response, list) else [response]
        for msg in messages:
            if msg.get("status") == "connected":
                logger.info("PROVIDER INFO:      %s", msg.get("message"))
                continue
            if "Your plan doesn't include websocket access" in msg.get("message"):
                err = f"UnauthorizedError -> {msg.get('message')}"
                logger.error(err)
                sys.exit(1)
            if msg.get("status") != "auth_success":
                err = (
                    f"UnauthorizedError -> {msg.get('status')} -> {msg.get('message')}"
                )
                logger.error(err)
                sys.exit(1)
            logger.info("PROVIDER INFO:      %s", msg.get("message"))
    except Exception as e:
        logger.error(
            "PROVIDER ERROR:     %s -> %s",
            e.__class__.__name__ if hasattr(e, "__class__") else e,
            e.args[0],
        )
        sys.exit(1)


async def subscribe(websocket, symbol, event):
    """Subscribe or unsubscribe to a symbol."""
    try:
        ticker = await handle_symbol(symbol)
    except ValueError as e:
        logger.error(e)
        return
    subscribe_event = f'{{"action":"{event}","params":"{ticker}"}}'
    try:
        await websocket.send(subscribe_event)
    except Exception as e:
        msg = f"PROVIDER ERROR:     {e.__class__.__name__} -> {e}"
        logger.error(msg)


async def read_stdin():
    """Read from stdin and queue commands."""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        sys.stdin.flush()
        if line:
            try:
                command = line.strip() if "qsize" in line else json.loads(line.strip())
                await command_queue.enqueue(command)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from stdin")


async def process_stdin_queue(websocket):
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
        if command == "qsize":
            logger.info(f"PROVIDER INFO:      Queue size: {queue.queue.qsize()}")
        else:
            symbol = command.get("symbol")
            event = command.get("event")
            if symbol and event:
                await subscribe(websocket, symbol, event)


async def process_message(message):
    """Process the WebSocket message."""
    messages = message if isinstance(message, list) else [message]
    for msg in messages:
        if "status" in msg or "message" in msg:
            if "status" in msg and msg["status"] == "error":
                err = msg.get("message")
                raise websockets.WebSocketException(err)
            if "message" in msg and msg.get("message"):
                if "Your plan doesn't include websocket access" in msg.get("message"):
                    err = f"UnauthorizedError -> {msg.get('message')}"
                    logger.error(err)
                    sys.exit(1)

                logger.info("PROVIDER INFO:      %s", msg.get("message"))
        elif msg and "ev" in msg and "status" not in msg:
            try:
                result = PolygonWebSocketData(**msg).model_dump_json(
                    exclude_none=True, exclude_unset=True
                )
            except ValidationError as e:
                try:
                    handle_validation_error(logger, e)
                except ValidationError:
                    raise e from e

            if result:
                await DATABASE._write_to_db(result)  # pylint: disable=protected-access
        else:
            logger.info("PROVIDER INFO:      %s", msg)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""

    tasks: set = set()

    handler_task = asyncio.create_task(
        queue.process_queue(lambda message: process_message(message))
    )
    tasks.add(handler_task)
    for i in range(0, 64):
        new_task = asyncio.create_task(
            queue.process_queue(lambda message: process_message(message))
        )
        tasks.add(new_task)
    stdin_task = asyncio.shield(asyncio.create_task(read_stdin()))
    try:
        connect_kwargs = CONNECT_KWARGS.copy()
        connect_kwargs["max_size"] = None
        connect_kwargs["read_limit"] = 2**32
        connect_kwargs["close_timeout"] = 10
        connect_kwargs["ping_timeout"] = None

        try:
            async with websockets.connect(URL, **connect_kwargs) as websocket:
                await login(websocket)
                response = await websocket.recv()
                messages = json.loads(response)
                await process_message(messages)
                await subscribe(websocket, kwargs["symbol"], "subscribe")
                response = await websocket.recv()
                messages = json.loads(response)
                await process_message(messages)
                cmd_task = asyncio.get_running_loop().create_task(
                    process_stdin_queue(websocket)
                )
                while True:
                    messages = await websocket.recv()
                    await queue.enqueue(json.loads(messages))

                cmd_task.cancel()
                await cmd_task
                asyncio.gather(*cmd_task, return_exceptions=True)

        except websockets.InvalidStatusCode as e:
            if e.status_code == 404:
                msg = f"PROVIDER ERROR:     {e}"
                logger.error(msg)
                sys.exit(1)
            else:
                raise
        except websockets.InvalidURI as e:
            msg = f"PROVIDER ERROR:     {e}"
            logger.error(msg)
            sys.exit(1)

    except websockets.ConnectionClosedOK as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
        logger.info(msg)
        sys.exit(0)

    except websockets.ConnectionClosed as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
        logger.info(msg)
        # Attempt to reopen the connection
        logger.info("PROVIDER INFO:      Attempting to reconnect after five seconds.")
        await asyncio.sleep(5)
        await connect_and_stream()

    except websockets.WebSocketException as e:
        msg = f"PROVIDER ERROR:     WebSocketException -> {e}"
        logger.error(msg)
        sys.exit(1)

    except Exception as e:
        msg = (
            f"PROVIDER ERROR:     Unexpected error -> "
            f"{e.__class__.__name__ if hasattr(e, '__class__') else e}: {e}"
        )
        logger.error(msg)
        sys.exit(1)

    finally:
        tasks.add(stdin_task)
        for task in tasks:
            task.cancel()
            await task
        asyncio.gather(*tasks, return_exceptions=True)
        sys.exit(0)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(lambda loop, context: None)
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(
            connect_and_stream(),
            loop,
        )
        loop.run_forever()

    except (KeyboardInterrupt, websockets.ConnectionClosed):
        logger.error("PROVIDER ERROR:     WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        ERR = f"PROVIDER ERROR:     {e.__class__.__name__} -> {e}"
        logger.error(ERR)

    finally:
        loop.close()
        sys.exit(0)
