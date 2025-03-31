import asyncio
import contextlib
import importlib.util
import json
import logging
import sys
from datetime import datetime
from typing import Annotated

import websockets
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.sql import text
from websockets.exceptions import ConnectionClosedOK

# Dynamically import the database module
database_path = "/Users/darrenlee/github/OpenBB/openbb_platform/extensions/websockets/openbb_websockets/database.py"
spec = importlib.util.spec_from_file_location("database", database_path)
database = importlib.util.module_from_spec(spec)
sys.modules["database"] = database
spec.loader.exec_module(database)

app = FastAPI()
logger = logging.getLogger("uvicorn-error")

message_queue = asyncio.Queue()

SUBSCRIBED_SYMBOLS = []


class ConnectedClients:

    def __init__(self):
        self.clients = set()

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)


ConnectedWebsocketClients = ConnectedClients()


def get_connected_clients():
    return ConnectedWebsocketClients


ActiveClients = Annotated[ConnectedClients, Depends(get_connected_clients)]


DbSessionLocal = database.WebSocketDatabaseSession(
    host="sqlite+aiosqlite:///sqlite.db",
    batch_size=100,
    batch_interval=1,
    logger=logger,
)


@app.on_event("startup")
async def startup_event():
    # Create the database tables
    await DbSessionLocal.create_all()

    # Start the task to write messages to the database
    asyncio.create_task(await asyncio.to_thread(DbSessionLocal.start_writer_task))


@app.on_event("shutdown")
async def shutdown_event():
    # Dispose of the database connection
    await DbSessionLocal.stop_writer_task()
    await DbSessionLocal.close()


async def symbol_handler(symbols: str, external_ws):
    unsubscribe_channels = []
    channels = []
    for sym in list(set(symbols)):
        if sym not in SUBSCRIBED_SYMBOLS:
            SUBSCRIBED_SYMBOLS.append(sym)
        channels.append(f"deribit_price_index.{sym}")

    UNSUBSCRIBE_SYMBOLS = list(set(SUBSCRIBED_SYMBOLS) - set(symbols))
    print(f"Subscribed Symbols: {SUBSCRIBED_SYMBOLS}")
    print(f"Unsubscribed Symbols: {UNSUBSCRIBE_SYMBOLS}")

    for sym in UNSUBSCRIBE_SYMBOLS:
        SUBSCRIBED_SYMBOLS.remove(sym)
        unsubscribe_channels.append(f"deribit_price_index.{sym}")

    if unsubscribe_channels:
        msg = {
            "jsonrpc": "2.0",
            "id": 3600,
            "method": "public/unsubscribe",
            "params": {
                "channels": unsubscribe_channels,
            },
        }
        print(msg)
        await external_ws.send(json.dumps(msg))

    print(f"Updating subscription to: {channels}")

    msg = {
        "jsonrpc": "2.0",
        "id": 3600,
        "method": "public/subscribe",
        "params": {
            "channels": channels,
        },
    }

    await external_ws.send(json.dumps(msg))


async def message_handler(external_ws, client_ws):
    while True:
        try:
            message = await message_queue.get()
            if not message:
                asyncio.sleep(0.1)
                continue
            message = message.get("result") or message.get("params", {}).get("data", {})
            if message and isinstance(message, dict):
                msg = {
                    "date": datetime.fromtimestamp(
                        message.get("timestamp") / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": message.get("index_name"),
                    "price": message.get("price"),
                }
                await DbSessionLocal.queue.put(msg)

                try:
                    await client_ws.send_json(msg)
                except RuntimeError:
                    break

                except (WebSocketDisconnect, ConnectionClosedOK):
                    return  # Exit the entire function on disconnect
            else:
                continue

        except Exception as e:
            logger.error(f"Error in message handler: {e}", exc_info=True)
            # Continue to the next iteration of the outer loop


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    msg = {
        "jsonrpc": "2.0",
        "id": 3600,
        "method": "public/subscribe",
        "params": {"channels": []},
    }
    try:
        async with websockets.connect(
            "wss://test.deribit.com/ws/api/v2"
        ) as external_ws:

            handler_task = asyncio.create_task(
                await asyncio.to_thread(message_handler, external_ws, websocket)
            )

            async def receive_from_external_ws():
                while True:
                    try:
                        response = await external_ws.recv()
                        await message_queue.put(json.loads(response))
                    except (WebSocketDisconnect, ConnectionClosedOK):
                        break

            async def receive_from_client_ws():
                while True:
                    try:
                        data = await websocket.receive_text()
                        print(data)
                        _symbols = json.loads(data).get("params", {}).get("symbol", [])
                        await symbol_handler(_symbols, external_ws)

                    except (WebSocketDisconnect, ConnectionClosedOK):
                        break

            try:
                await external_ws.send(json.dumps(msg))

                external_task = asyncio.create_task(receive_from_external_ws())
                client_task = asyncio.create_task(receive_from_client_ws())

                done, pending = await asyncio.wait(
                    [external_task, client_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task
            except (WebSocketDisconnect, KeyboardInterrupt, ConnectionClosedOK):
                logger.info("WebSocket disconnected")
                pass
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        handler_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await handler_task
        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        if websocket.application_state == 1:
            await websocket.close(reason="WebSocket Disconnected")


@app.get("/get_ws_data")
async def get_messages(symbol: str = None) -> list:
    global SUBSCRIBED_SYMBOLS

    symbols = symbol.split(",") if isinstance(symbol, str) else symbol
    msg = []

    async with DbSessionLocal.get_read_session() as session:
        try:
            if symbols:
                for sym in symbols:
                    # Use JSON filtering with SQLite's json operator
                    if sym not in SUBSCRIBED_SYMBOLS:
                        SUBSCRIBED_SYMBOLS.append(sym)
                    result = await session.execute(
                        select(database.WebSocketMessages)
                        .where(text("message->>'symbol' = :sym"))
                        .limit(1)
                        .offset(-1)
                        .params(sym=sym)
                    )
                    messages = result.scalars().all()
                    msg.extend(
                        [m.message for m in messages]
                        if messages
                        else [{"date": None, "symbol": sym, "price": None}]
                    )
            else:
                msg.extend({})

            return msg
        except Exception as e:
            logger.error(f"Error querying database: {e}", exc_info=True)
            return []


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
