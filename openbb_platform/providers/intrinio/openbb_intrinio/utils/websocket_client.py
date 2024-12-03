"""Intrinio WebSocket server."""

import asyncio
import json
import signal
import sys

from openbb_intrinio.models.websocket_connection import IntrinioWebSocketData
from openbb_intrinio.utils.stocks_client import IntrinioRealtimeClient, Quote, Trade
from openbb_websockets.helpers import (
    MessageQueue,
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
    write_to_db,
)
from pydantic import ValidationError

logger = get_logger("openbb.websocket.intrinio")
kwargs = parse_kwargs()
command_queue = MessageQueue()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})


async def subscribe(client, symbol, event):
    """Subscribe or unsubscribe to a symbol."""
    ticker = symbol.split(",") if isinstance(symbol, str) else symbol
    try:
        if event == "subscribe":
            client.join(ticker)
        elif event == "unsubscribe":
            client.leave(ticker)
    except Exception as e:  # pylint: disable=broad-except
        msg = f"PROVIDER ERROR:     {e.__class__.__name__}: {e}"
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


async def process_stdin_queue(client):
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
        symbol = ["lobby" if d == "*" else d.upper() for d in command.get("symbol", [])]
        event = command.get("event")
        if symbol and event:
            await subscribe(client, symbol, event)


async def process_message(message):
    """Process the message and write to the database."""
    result: dict = {}
    message = json.loads(message) if isinstance(message, str) else message
    is_trade = isinstance(message, Trade)
    is_quote = isinstance(message, Quote)
    if hasattr(message, "__dict__"):
        message = message.__dict__
        if is_trade or is_quote:
            message["type"] = "trade" if is_trade else "quote"

    try:
        result = IntrinioWebSocketData.model_validate(message).model_dump_json(
            exclude_none=True, exclude_unset=True
        )
        result = message
    except ValidationError as e:
        try:
            handle_validation_error(logger, e)
        except ValidationError:
            raise e from e
    if result:
        await write_to_db(
            message, kwargs["results_file"], kwargs["table_name"], kwargs["limit"]
        )


def on_message(message, backlog):
    """Process the message and write to the database."""
    asyncio.run(process_message(message))


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


async def connect_and_stream():
    """Connect to the WebSocket and stream data to file."""
    symbol = kwargs.pop("symbol", "lobby")
    symbol = ["lobby"] if "*" in symbol else symbol.split(",")
    asyncio.create_task(read_stdin_and_queue_commands())
    client.connect()
    client.join(symbol)
    asyncio.create_task(process_stdin_queue(client))


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
        msg = f"PROVIDER ERROR:    {e.__class__.__name__}: {e}"
        logger.error(msg)

    finally:
        client.disconnect()
        sys.exit(0)
