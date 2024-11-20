"""FMP WebSocket server."""

import asyncio
import json
import os
import signal
import sys

import websockets
import websockets.exceptions
from openbb_fmp.models.websocket_connection import FmpWebSocketData
from openbb_websockets.helpers import (
    MessageQueue,
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
    write_to_db,
)
from pydantic import ValidationError

logger = get_logger("openbb.websocket.fmp")
kwargs = parse_kwargs()
queue = MessageQueue()
command_queue = MessageQueue()
CONNECT_KWARGS = kwargs.pop("connect_kwargs", {})


async def login(websocket, api_key):
    login_event = {
        "event": "login",
        "data": {
            "apiKey": api_key,
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
        msg = f"PROVIDER ERROR:     {e.__class__.__name__}: {e}"
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
        await asyncio.sleep(1)
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


async def process_stdin_queue(websocket):
    """Process the command queue."""
    while True:
        command = await command_queue.dequeue()
        symbol = command.get("symbol")
        event = command.get("event")
        if symbol and event:
            await subscribe(websocket, symbol, event)


async def process_message(message, results_path, table_name, limit):
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
                await write_to_db(result, results_path, table_name, limit)


async def connect_and_stream(url, symbol, api_key, results_path, table_name, limit):
    """Connect to the WebSocket and stream data to file."""

    handler_task = asyncio.create_task(
        queue.process_queue(
            lambda message: process_message(message, results_path, table_name, limit)
        )
    )

    stdin_task = asyncio.create_task(read_stdin_and_queue_commands())

    try:
        websocket = await websockets.connect(url, **CONNECT_KWARGS)
        await login(websocket, api_key)
        await subscribe(websocket, symbol, "subscribe")

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
                    await asyncio.shield(queue.enqueue(json.loads(message)))

    except websockets.ConnectionClosed as e:
        msg = f"PROVIDER INFO:      The WebSocket connection was closed -> {e}"
        logger.info(msg)
        # Attempt to reopen the connection
        logger.info("PROVIDER INFO:      Attempting to reconnect after five seconds.")
        await asyncio.sleep(5)
        await connect_and_stream(url, symbol, api_key, results_path, table_name, limit)

    except websockets.WebSocketException as e:
        logger.error(e)
        sys.exit(1)

    except Exception as e:
        msg = f"PROVIDER ERROR:     Unexpected error -> {e.__class__.__name__}: {e}"
        logger.error(msg)
        sys.exit(1)

    finally:
        await websocket.close()
        handler_task.cancel()
        stdin_task.cancel()
        await asyncio.gather(handler_task, stdin_task, return_exceptions=True)
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
        msg = f"PROVIDER ERROR:    {e.__class__.__name__}: {e}"
        logger.error(msg)

    finally:
        sys.exit(0)
