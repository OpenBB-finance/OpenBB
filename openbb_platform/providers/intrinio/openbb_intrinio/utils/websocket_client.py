"""Intrinio WebSocket server."""

# pylint: disable=unused-argument

import asyncio
import json
import signal
import sys
from typing import Any

from openbb_core.provider.utils.websockets.database import Database, DatabaseWriter
from openbb_core.provider.utils.websockets.helpers import (
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
)
from openbb_core.provider.utils.websockets.message_queue import MessageQueue
from openbb_intrinio.models.websocket_connection import IntrinioWebSocketData
from openbb_intrinio.utils.stocks_client import IntrinioRealtimeClient
from pydantic import ValidationError

logger = get_logger("openbb.websocket.intrinio")
kwargs = parse_kwargs()
command_queue = MessageQueue(logger=logger)
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})
db_queue = MessageQueue(logger=logger)

DATABASE = DatabaseWriter(
    database=Database(
        results_file=kwargs["results_file"],
        table_name=kwargs["table_name"],
        limit=kwargs.get("limit"),
        logger=logger,
    ),
    queue=db_queue,
)


def process_message(message):
    """Process the message and write to the database."""
    result: Any = None
    try:
        result = IntrinioWebSocketData.model_validate_json(message.to_json())
        result = (  # type: ignore
            {}
            if result.exchange == "!" or result.price == 0  # type: ignore
            else result.model_dump_json()  # type: ignore
        )
    except ValidationError as e:
        try:
            handle_validation_error(logger, e)
        except ValidationError:
            raise e from e
    if result:
        db_queue.queue.put_nowait(result)


def on_message(message, backlog):
    """Process the message and write to the database."""
    process_message(message)


options = {
    "api_key": kwargs.get("api_key", ""),
    "provider": kwargs.get("feed", "").upper(),
    "logger": logger,
}

if kwargs.get("trades_only") is True:
    options["tradesonly"] = True

client = IntrinioRealtimeClient(
    options=options, on_trade=on_message, on_quote=on_message
)


async def subscribe(symbol, event):
    """Subscribe or unsubscribe to a symbol."""
    ticker = symbol.split(",") if isinstance(symbol, str) else symbol
    ticker = ["lobby"] if "*" in ticker or "LOBBY" in ticker else ticker
    try:
        if event == "subscribe":
            client.join(ticker)
        elif event == "unsubscribe":
            client.leave(ticker)
    except Exception as e:  # pylint: disable=broad-except
        exc = f"PROVIDER ERROR:     {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
        logger.error(exc)


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


async def process_stdin_queue():
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
        if command == "qsize":
            logger.info(
                "Queue size: %i - Writer Queue: %i",
                command_queue.queue.qsize(),
                DATABASE.batch_processor.task_queue.qsize(),
            )

        symbol = ["lobby" if d == "*" else d.upper() for d in command.get("symbol", [])]
        event = command.get("event")
        if symbol and event:
            await subscribe(symbol, event)


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""
    try:
        symbol = kwargs.pop("symbol", "lobby")
        symbol = ["lobby"] if "*" in symbol else symbol.split(",")
        stdin_task = asyncio.create_task(read_stdin_and_queue_commands())
        await DATABASE.start_writer()
        client.connect()
        client.join(symbol)
        process_stdin_task = asyncio.create_task(process_stdin_queue())
    finally:
        stdin_task.cancel()
        process_stdin_task.cancel()
        await stdin_task
        await process_stdin_task
        await DATABASE.stop_writer()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(lambda loop, context: None)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_termination_signal, logger)

        asyncio.run_coroutine_threadsafe(connect_and_stream(), loop)
        loop.run_forever()

    except KeyboardInterrupt:
        logger.error("PROVIDER INFO:     WebSocket connection closed")

    except Exception as e:  # pylint: disable=broad-except
        EXC = f"PROVIDER ERROR:    {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
        logger.error(EXC)

    finally:
        client.disconnect()
        loop.call_soon_threadsafe(loop.stop)
        loop.close()
        sys.exit(0)
