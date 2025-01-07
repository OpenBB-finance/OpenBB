"""
Polygon WebSocket Client.

This file should be run as a script, and is intended to be run as a subprocess of PolygonWebSocketFetcher.

Keyword arguments are passed from the command line as space-delimited, `key=value`, pairs.

Required Keyword Arguments
--------------------------
    api_key: str
        The API key for the Polygon WebSocket.
    symbol: str
        The symbol to subscribe to. Example: "AAPL" or "AAPL,MSFT". Use "*" to subscribe to all symbols.
    feed: str
        The feed to subscribe to. Example: "aggs_sec", "aggs_min", "trade", "quote".
    results_file: str
        The path to the file where the results will be stored.

Optional Keyword Arguments
--------------------------
    asset_type: str
        The asset type to subscribe to. Default is "crypto".
        Options: "stock", "stock_delayed", "options", "options_delayed", "fx", "crypto", "index", "index_delayed".
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
import time

import websockets
from openbb_core.provider.utils.websockets.database import Database, DatabaseWriter
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
from websockets.asyncio.client import connect

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
process_queue = MessageQueue(logger=logger, backoff_factor=0, max_size=1000000)
input_queue = MessageQueue(logger=logger, backoff_factor=0, max_size=1000000)
stdin_queue = MessageQueue(logger=logger)
db_queue = MessageQueue(logger=logger, backoff_factor=0, max_size=1000000)
kwargs = parse_kwargs()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
FEED = kwargs.pop("feed", None)
ASSET_TYPE = kwargs.pop("asset_type", "crypto")
URL = URL_MAP.get(ASSET_TYPE)
SUBSCRIBED_SYMBOLS: set = set()

MESSAGE_COUNT = 0
AVG_RATE = 0
LAST_MINUTE_COUNT = 0
PREVIOUS_MINUTE_COUNT = 0

if not kwargs.get("api_key"):
    raise ValueError("No API key provided.")

if not URL:
    raise ValueError("Invalid asset type provided.")


DATABASE = DatabaseWriter(
    database=Database(
        results_file=kwargs["results_file"],
        table_name=kwargs.get("table_name", "records"),
        limit=kwargs.get("limit"),
        logger=logger,
    ),
    queue=db_queue,
)


async def message_rate():
    """Calculate the average message rate."""
    global AVG_RATE  # pylint: disable=global-statement  # noqa
    start = time.time()
    while True:
        await asyncio.sleep(1)
        elapsed = time.time() - start
        if elapsed > 0:
            AVG_RATE = round(MESSAGE_COUNT / elapsed)


async def reset_last_minute_count():
    """Reset the last minute message count every minute."""
    global LAST_MINUTE_COUNT, PREVIOUS_MINUTE_COUNT  # pylint: disable=global-statement  # noqa
    while True:
        await asyncio.sleep(60)
        PREVIOUS_MINUTE_COUNT = LAST_MINUTE_COUNT
        LAST_MINUTE_COUNT = 0


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
        else:
            new_symbols.append(ticker)

    return ",".join(new_symbols)


async def login(websocket):
    """Login to the WebSocket."""
    login_event = f'{{"action":"auth","params":"{kwargs["api_key"]}"}}'
    try:
        await websocket.send(login_event)
        res = await websocket.recv(decode=False)
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
        msg = f"PROVIDER ERROR:     {e.__class__.__name__  if hasattr(e, '__class__') else e} -> {e.args}"
        logger.error(msg)

    tickers = ticker.split(",")
    if event == "subscribe":
        for t in tickers:
            SUBSCRIBED_SYMBOLS.add(t)
    elif event == "unsubscribe":
        for t in tickers:
            SUBSCRIBED_SYMBOLS.discard(t)

    kwargs["symbol"] = ",".join(SUBSCRIBED_SYMBOLS)


async def read_stdin():
    """Read from stdin and queue commands."""
    while True:
        line = await asyncio.to_thread(sys.stdin.readline)
        sys.stdin.flush()
        if line:
            try:
                command = line.strip()
                if command == "qsize":
                    logger.info(
                        f"PROVIDER INFO:      Input Queue: {input_queue.queue.qsize()} -"
                        f" Processing Queue: {process_queue.queue.qsize()}:{db_queue.queue.qsize()} -"
                        f" Writing Queue: {DATABASE.batch_processor.write_queue.qsize()}"
                    )
                elif command == "msgrate":
                    logger.info(
                        f"PROVIDER INFO:      Total Messages: {MESSAGE_COUNT}"
                        f" - Average Message Rate: {AVG_RATE}"
                        f" - Messages in Last Minute: {PREVIOUS_MINUTE_COUNT}"
                    )
                else:
                    command = json.loads(line.strip())
                    await stdin_queue.enqueue(command)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from stdin")


async def process_stdin_queue(websocket):
    """Process the command queue."""
    while True:
        command = await stdin_queue.dequeue()
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
                db_queue.queue.put_nowait(result)
        else:
            logger.info("PROVIDER INFO:      %s", msg)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""

    tasks: set = set()
    conn_kwargs = {
        "ping_timeout": None,
        "ping_interval": 10,
        "close_timeout": 1,
        "max_size": 32768,
        "compression": None,
    }
    conn_kwargs.update(CONNECT_KWARGS)

    async def message_receiver(websocket):
        """Message receiver."""
        while True:
            message = await websocket.recv(decode=False)
            await input_queue.enqueue(message)

    async def process_input_messages(message):
        """Process the messages offloaded from the websocket."""

        def _process_in_thread():
            global LAST_MINUTE_COUNT, MESSAGE_COUNT  # pylint: disable=global-statement  # noqa

            message_data = json.loads(message)
            if isinstance(message_data, list):
                MESSAGE_COUNT += len(message_data)
                LAST_MINUTE_COUNT += len(message_data)
                status_msgs = [
                    msg
                    for msg in message_data
                    if isinstance(msg, dict) and ("status" in msg or "message" in msg)
                ]
                data_msgs = [msg for msg in message_data if msg not in status_msgs]

                if status_msgs:
                    asyncio.run(process_message(status_msgs))
                if data_msgs:
                    process_queue.queue.put_nowait(data_msgs)
            elif isinstance(message_data, dict):
                if "status" in message_data or "message" in message_data:
                    asyncio.run(process_message(message_data))
                else:
                    process_queue.queue.put_nowait(message_data)
            elif isinstance(message_data, str) and "status" in message_data:
                asyncio.run(process_message(message_data))

        # Run processing in thread
        process = asyncio.to_thread(_process_in_thread)
        process_task = asyncio.create_task(process)
        tasks.add(process_task)

    try:
        handler_task = asyncio.create_task(
            process_queue.process_queue(lambda message: process_message(message))
        )
        tasks.add(handler_task)
        stdin_task = asyncio.create_task(read_stdin())
        tasks.add(stdin_task)

        await DATABASE.start_writer()

        processor_task = asyncio.create_task(
            input_queue.process_queue(lambda message: process_input_messages(message))
        )
        tasks.add(processor_task)
        rate_task = asyncio.create_task(message_rate())
        tasks.add(rate_task)
        minute_task = asyncio.create_task(reset_last_minute_count())
        tasks.add(minute_task)

        async for websocket in connect(
            URL,
            **conn_kwargs,
        ):
            try:
                if not any(
                    task.name == "cmd_task" for task in tasks if hasattr(task, "name")
                ):
                    cmd_task = asyncio.create_task(
                        process_stdin_queue(websocket), name="cmd_task"
                    )
                    tasks.add(cmd_task)

                await login(websocket)

                response = await websocket.recv(decode=False)

                await process_message(json.loads(response))

                await subscribe(websocket, kwargs["symbol"], "subscribe")

                await message_receiver(websocket)

            # Attempt to reopen the connection
            except (
                websockets.ConnectionClosed,
                websockets.ConnectionClosedError,
            ) as e:
                msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
                logger.info(msg)
                logger.info("PROVIDER INFO:      Attempting to reconnect...")
                await asyncio.sleep(1)
                continue

            except websockets.ConnectionClosedOK as e:
                msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
                logger.info(msg)
                sys.exit(0)

            except websockets.WebSocketException as e:
                if "code=1012" in str(e):
                    await asyncio.sleep(1)
                    for task in tasks:
                        task.cancel()
                        await task
                    asyncio.gather(*tasks, return_exceptions=True)
                    await DATABASE.stop_writer()
                    await asyncio.sleep(1)
                    asyncio.run_coroutine_threadsafe(
                        connect_and_stream(),
                        asyncio.get_event_loop(),
                    )
                msg = f"PROVIDER ERROR:     WebSocketException -> {e}"
                logger.error(msg)
                sys.exit(1)

            except Exception as e:  # pylint: disable=broad-except
                msg = (
                    f"PROVIDER ERROR:     Unexpected error -> "
                    f"{e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
                )
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
            loop.add_signal_handler(sig, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(
            connect_and_stream(),
            loop,
        )
        loop.run_forever()

    except (websockets.ConnectionClosed, websockets.ConnectionClosedError) as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
        logger.info(msg)
        # Attempt to reopen the connection
        logger.info("PROVIDER INFO:      Attempting to reconnect...")
        time.sleep(1)
        asyncio.run_coroutine_threadsafe(
            connect_and_stream(),
            loop,
        )

    except (KeyboardInterrupt, websockets.ConnectionClosed):
        logger.error("PROVIDER ERROR:     WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        ERR = f"PROVIDER ERROR:     {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
        logger.error(ERR)

    finally:
        loop.call_soon_threadsafe(loop.stop)
        loop.close()
        sys.exit(0)
