"""Polygon WebSocket client."""

import asyncio
import json
import os
import signal
import sys

import websockets
import websockets.exceptions
from openbb_polygon.models.websocket_connection import (
    FEED_MAP,
    PolygonWebSocketData,
)
from openbb_websockets.helpers import (
    MessageQueue,
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
    write_to_db,
)
from pydantic import ValidationError

logger = get_logger("openbb.websocket.polygon")
queue = MessageQueue(logger=logger)
command_queue = MessageQueue(logger=logger)

kwargs = parse_kwargs()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
FEED = kwargs.pop("feed", None)
ASSET_TYPE = kwargs.pop("asset_type", None)
kwargs["results_file"] = os.path.abspath(kwargs.get("results_file"))


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
        logger.error("PROVIDER ERROR:     %s -> %s", e.__class__.__name__, e.args[0])
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

        if not line:
            break

        try:
            command = json.loads(line.strip())
            await command_queue.enqueue(command)
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from stdin")


async def process_stdin_queue(websocket):
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
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
                await write_to_db(
                    result,
                    kwargs["results_file"],
                    kwargs["table_name"],
                    kwargs.get("limit"),
                )
        else:
            logger.info("PROVIDER INFO:      %s", msg)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""

    handler_task = asyncio.create_task(
        queue.process_queue(lambda message: process_message(message))
    )
    stdin_task = asyncio.create_task(read_stdin())
    try:
        connect_kwargs = CONNECT_KWARGS.copy()
        if "ping_timeout" not in connect_kwargs:
            connect_kwargs["ping_timeout"] = None
        if "close_timeout" not in connect_kwargs:
            connect_kwargs["close_timeout"] = None

        try:
            async with websockets.connect(kwargs["url"], **connect_kwargs) as websocket:

                await login(websocket)
                response = await websocket.recv()
                messages = json.loads(response)
                await process_message(messages)
                await subscribe(websocket, kwargs["symbol"], "subscribe")
                response = await websocket.recv()
                messages = json.loads(response)
                await process_message(messages)
                while True:
                    cmd_task = asyncio.create_task(process_stdin_queue(websocket))
                    msg_task = asyncio.create_task(websocket.recv())
                    done, pending = await asyncio.wait(
                        [cmd_task, msg_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in pending:
                        task.cancel()

                    for task in done:
                        if task == cmd_task:
                            await cmd_task
                        elif task == msg_task:
                            messages = task.result()
                            await asyncio.shield(queue.enqueue(json.loads(messages)))

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
        msg = f"PROVIDER ERROR:     Unexpected error -> {e.__class__.__name__}: {e}"
        logger.error(msg)
        sys.exit(1)

    finally:
        handler_task.cancel()
        stdin_task.cancel()
        await asyncio.gather(handler_task, stdin_task, return_exceptions=True)
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
        msg = f"PROVIDER ERROR:     {e.__class__.__name__} -> {e}"
        logger.error(msg)

    finally:
        sys.exit(0)
