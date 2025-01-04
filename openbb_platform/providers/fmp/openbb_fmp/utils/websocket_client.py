"""FMP WebSocket client."""

import asyncio
import signal
import sys

import orjson as json
import websockets
from openbb_core.provider.utils.websockets.database import Database, DatabaseWriter
from openbb_core.provider.utils.websockets.helpers import (
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
)
from openbb_core.provider.utils.websockets.message_queue import MessageQueue
from openbb_fmp.models.websocket_connection import FmpWebSocketData
from pydantic import ValidationError

URL_MAP = {
    "stock": "wss://websockets.financialmodelingprep.com",
    "fx": "wss://forex.financialmodelingprep.com",
    "crypto": "wss://crypto.financialmodelingprep.com",
}

logger = get_logger("openbb.websocket.fmp")
kwargs = parse_kwargs()
input_queue = MessageQueue()
command_queue = MessageQueue()
database_queue = MessageQueue()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
URL = URL_MAP.get(kwargs.pop("asset_type"), None)

if not URL:
    raise ValueError("Invalid asset type provided.")

if not kwargs.get("api_key"):
    raise ValueError("API key is required.")

DATABASE = DatabaseWriter(
    database=Database(
        results_file=kwargs.get("results_file"),
        table_name=kwargs.get("table_name"),
        limit=kwargs.get("limit"),
        logger=logger,
    ),
    queue=database_queue,
)


async def login(websocket):
    """Login to the WebSocket."""
    login_event = {
        "event": "login",
        "data": {
            "apiKey": kwargs["api_key"],
        },
    }
    try:
        await websocket.send(json.dumps(login_event))
        await asyncio.sleep(1)
        response = await websocket.recv()
        message = json.loads(response)
        if message.get("message") == "Unauthorized":
            logger.error(
                "UnauthorizedError -> Account not authorized."
                " Please check that the API key is entered correctly and is entitled to access."
            )
            sys.exit(1)
        else:
            msg = message.get("message")
            logger.info("PROVIDER INFO:      %s", msg)
    except Exception as e:  # pylint: disable=broad-except
        msg = f"PROVIDER ERROR:     {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
        logger.error(msg)
        sys.exit(1)


async def subscribe(websocket, symbol, event):
    """Subscribe or unsubscribe to a symbol."""
    ticker = symbol.split(",") if isinstance(symbol, str) else symbol
    subscribe_event = {
        "event": event,
        "data": {
            "ticker": ticker,
        },
    }
    try:
        await websocket.send(json.dumps(subscribe_event))
    except Exception as e:  # pylint: disable=broad-except
        msg = f"PROVIDER ERROR:     {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e}"
        logger.error(msg)


async def read_stdin_and_queue_commands():
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
            logger.error("Invalid JSON received from stdin -> %s", line.strip())


async def process_stdin_queue(websocket):
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
        symbol = command.get("symbol")
        event = command.get("event")
        if symbol and event:
            await subscribe(websocket, symbol, event)


async def process_message(message):
    """Process the message and write to the database."""
    result: dict = {}
    message = json.loads(message) if isinstance(message, str) else message
    if message.get("event") != "heartbeat":
        if message.get("event") in ["login", "subscribe", "unsubscribe"]:
            if "you are not authorized" in message.get("message", "").lower():
                msg = f"UnauthorizedError -> FMP Message: {message['message']}"
                logger.error(msg)
            elif "Connected from another location" in message.get("message", ""):
                msg = f"UnauthorizedError -> FMP Message: {message.get('message')}"
                logger.info(msg)
                sys.exit(0)
            else:
                msg = f"PROVIDER INFO:      {message.get('message')}"
                logger.info(msg)
        else:
            try:
                result = FmpWebSocketData.model_validate(message).model_dump_json(
                    exclude_none=True, exclude_unset=True
                )
            except ValidationError as e:
                try:
                    handle_validation_error(logger, e)
                except ValidationError:
                    raise e from e
            if result:
                await database_queue.enqueue(result)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""

    handler_task = asyncio.create_task(
        input_queue.process_queue(lambda message: process_message(message))
    )

    stdin_task = asyncio.create_task(read_stdin_and_queue_commands())

    await DATABASE.start_writer()

    disconnects = 0

    async for websocket in websockets.connect(URL, **CONNECT_KWARGS):
        try:
            await login(websocket)

            await subscribe(websocket, kwargs["symbol"], "subscribe")

            while True:
                ws_task = asyncio.create_task(websocket.recv())
                cmd_task = asyncio.create_task(process_stdin_queue(websocket))

                done, pending = await asyncio.wait(
                    [ws_task, cmd_task], return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()

                for task in done:
                    if task == cmd_task:
                        await cmd_task
                    elif task == ws_task:
                        message = task.result()
                        await input_queue.enqueue(json.loads(message))

        except websockets.ConnectionClosed as e:
            msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
            logger.info(msg)
            # Attempt to reopen the connection
            logger.info("PROVIDER INFO:      Attempting to reconnect...")
            await asyncio.sleep(2)
            disconnects += 1
            if disconnects > 5:
                logger.error("PROVIDER ERROR:    Too many disconnects. Exiting...")
                sys.exit(1)
            continue

        except websockets.WebSocketException as e:
            logger.error(e)
            sys.exit(1)

        except Exception as e:  # pylint: disable=broad-except
            msg = f"PROVIDER ERROR:     Unexpected error -> {e.__class__.__name__}: {e}"
            logger.error(msg)
            sys.exit(1)

        finally:
            await websocket.close()
            handler_task.cancel()
            stdin_task.cancel()
            await asyncio.gather(handler_task, stdin_task, return_exceptions=True)
            await DATABASE.stop_writer()
            sys.exit(0)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(
            connect_and_stream(),
            loop,
        )
        loop.run_forever()

    except (KeyboardInterrupt, websockets.ConnectionClosed):
        logger.error("PROVIDER ERROR:    WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        ERR = f"PROVIDER ERROR:    {e.__class__.__name__ if hasattr(e, '__class__') else e}"
        logger.error(ERR)

    finally:
        loop.call_soon_threadsafe(loop.stop)
        loop.close()
        sys.exit(0)
