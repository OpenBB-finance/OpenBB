import asyncio
import contextlib
import json
import logging
import queue
import threading
from datetime import datetime
from typing import Dict, Optional, Set

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn-error")


@app.get("/")
def read_root():
    return {"Info": "Live Grid Widget Example For OpenBB Workspace Custom Backend"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.symbol_subscribers: Dict[str, Set[WebSocket]] = {}
        self.external_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.external_task: Optional[asyncio.Task] = None
        self.message_queue = queue.Queue()
        self.processor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.lock = asyncio.Lock()
        self.thread_running = False
        self.loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.client_subscriptions[websocket] = set()

        # Start the master connection if not already running
        if not self.is_running:
            await self.start_master_connection()

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

            # Remove client subscriptions
            if websocket in self.client_subscriptions:
                subscribed_symbols = self.client_subscriptions.pop(websocket)

                # Update symbol subscribers
                for symbol in subscribed_symbols:
                    if symbol in self.symbol_subscribers:
                        self.symbol_subscribers[symbol].discard(websocket)

                        # If no more subscribers for this symbol, unsubscribe from Deribit
                        if not self.symbol_subscribers[symbol] and self.external_ws:
                            await self.unsubscribe_symbols([symbol])

            if websocket.application_state == 1:
                await websocket.close(reason="Client disconnected")

            # If no more clients, stop the master connection
            if not self.active_connections and self.is_running:
                await self.stop_master_connection()

    def process_messages_thread(self):
        """Thread function to process messages from the queue"""
        asyncio.set_event_loop(self.loop)
        self.thread_running = True

        while self.thread_running:
            try:
                # Get message from queue with timeout to allow checking thread_running
                try:
                    message = self.message_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # Check if this is a reconnection signal
                if isinstance(message, dict) and message.get("_reconnect"):
                    asyncio.run_coroutine_threadsafe(self.reconnect(), self.loop)
                    self.message_queue.task_done()
                    continue

                # Process normal message
                try:
                    message_data = json.loads(message)

                    # Process the message
                    data = message_data.get("result") or message_data.get(
                        "params", {}
                    ).get("data", {})
                    if data and isinstance(data, dict):
                        symbol = data.get("index_name")
                        if symbol:
                            # Format message
                            msg = {
                                "date": datetime.fromtimestamp(
                                    data.get("timestamp") / 1000
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                                "symbol": symbol,
                                "price": data.get("price"),
                            }

                            # Broadcast to subscribers - must be done in the event loop
                            subscribers = self.symbol_subscribers.get(
                                symbol, set()
                            ).copy()
                            if subscribers:
                                asyncio.run_coroutine_threadsafe(
                                    self.broadcast_to_subscribers(symbol, msg),
                                    self.loop,
                                )
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                finally:
                    # Mark the message as processed
                    self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Error in message processor thread: {e}")

    async def broadcast_to_subscribers(self, symbol, msg):
        """Broadcast a message to all subscribers of a symbol"""
        subscribers = self.symbol_subscribers.get(symbol, set())
        for client in subscribers:
            try:
                await client.send_json(msg)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")

    async def start_master_connection(self):
        """Start a single master connection to Deribit"""
        # Clean up any existing connection first
        await self.stop_master_connection()

        try:
            # Establish the WebSocket connection
            self.external_ws = await websockets.connect(
                "wss://test.deribit.com/ws/api/v2"
            )
            self.is_running = True

            # Start task to receive messages from Deribit and put them in the queue
            self.external_task = asyncio.create_task(self.receive_from_external())

            # Store the event loop for the thread to use
            self.loop = asyncio.get_event_loop()

            # Start thread to process messages from the queue
            self.thread_running = True
            self.processor_thread = threading.Thread(
                target=self.process_messages_thread, daemon=True
            )
            self.processor_thread.start()

            logger.info("Master connection to Deribit established")

            # Resubscribe to all active symbols after reconnection
            await self.resubscribe_active_symbols()
        except Exception as e:
            logger.error(f"Failed to establish master connection: {e}", exc_info=True)
            self.is_running = False

    async def resubscribe_active_symbols(self):
        """Resubscribe to all symbols that have active subscribers after reconnection"""
        active_symbols = [
            symbol
            for symbol, subscribers in self.symbol_subscribers.items()
            if subscribers  # Only include symbols with active subscribers
        ]

        if active_symbols and self.external_ws:
            await self.subscribe_symbols(active_symbols)
            logger.info(
                f"Resubscribed to {len(active_symbols)} symbols after reconnection"
            )

    async def stop_master_connection(self):
        """Stop the master connection to Deribit"""
        self.is_running = False

        # Stop the message processing thread
        if self.processor_thread and self.processor_thread.is_alive():
            self.thread_running = False
            self.processor_thread.join(timeout=2.0)
            self.processor_thread = None

        # Cancel the task that receives messages from Deribit
        if self.external_task:
            self.external_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.external_task
            self.external_task = None

        # Close the WebSocket connection
        if self.external_ws:
            await self.external_ws.close()
            self.external_ws = None

        # Clear the message queue
        while True:
            try:
                self.message_queue.get_nowait()
                self.message_queue.task_done()
            except queue.Empty:
                break

        logger.info("Master connection to Deribit closed")

    async def receive_from_external(self):
        """Receive messages from the external WebSocket and put them in the queue"""
        while self.is_running and self.external_ws:
            try:
                response = await self.external_ws.recv()
                # Put the raw message in the queue for processing
                self.message_queue.put(response)
            except (ConnectionClosedOK, ConnectionClosedError, WebSocketDisconnect):
                logger.warning("Deribit connection closed, attempting to reconnect...")
                # Add a special reconnect message to the queue
                self.message_queue.put({"_reconnect": True})
                break
            except Exception as e:
                logger.error(f"Error in master connection handler: {e}", exc_info=True)
                await asyncio.sleep(1)  # Prevent tight loop on errors

    async def reconnect(self):
        """Handle reconnection after a connection failure"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait a bit before reconnecting
        await asyncio.sleep(5)

        # Only reconnect if we still have clients
        if self.active_connections:
            await self.start_master_connection()

    async def update_client_symbols(self, websocket: WebSocket, symbols: list):
        """Update the symbols a client is subscribed to"""
        async with self.lock:
            if websocket not in self.active_connections:
                return

            old_symbols = self.client_subscriptions.get(websocket, set())
            new_symbols = set(symbols)

            # Symbols to subscribe to
            to_subscribe = new_symbols - old_symbols

            # Symbols to unsubscribe from
            to_unsubscribe = old_symbols - new_symbols

            # Update client subscriptions
            self.client_subscriptions[websocket] = new_symbols

            # Update symbol subscribers and subscribe/unsubscribe as needed
            to_add_to_deribit = []
            to_remove_from_deribit = []

            for symbol in to_subscribe:
                # Check if symbol exists but has no subscribers
                if (
                    symbol in self.symbol_subscribers
                    and not self.symbol_subscribers[symbol]
                ):
                    to_add_to_deribit.append(symbol)
                # Check if symbol doesn't exist at all
                elif symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()
                    to_add_to_deribit.append(symbol)
                self.symbol_subscribers[symbol].add(websocket)

            for symbol in to_unsubscribe:
                if symbol in self.symbol_subscribers:
                    self.symbol_subscribers[symbol].discard(websocket)
                    if not self.symbol_subscribers[symbol]:
                        to_remove_from_deribit.append(symbol)
                        # Don't delete the key here, we'll do it after unsubscribing

            # Make the actual subscription changes on Deribit
            if to_add_to_deribit and self.external_ws:
                await self.subscribe_symbols(to_add_to_deribit)

            if to_remove_from_deribit and self.external_ws:
                await self.unsubscribe_symbols(to_remove_from_deribit)
                # Now we can safely remove empty subscriber sets
                for symbol in to_remove_from_deribit:
                    if (
                        symbol in self.symbol_subscribers
                        and not self.symbol_subscribers[symbol]
                    ):
                        del self.symbol_subscribers[symbol]

    async def subscribe_symbols(self, symbols: list):
        """Subscribe to symbols on Deribit"""
        if not symbols or not self.external_ws:
            return

        channels = [f"deribit_price_index.{sym}" for sym in symbols]

        msg = {
            "jsonrpc": "2.0",
            "id": 3600,
            "method": "public/subscribe",
            "params": {
                "channels": channels,
            },
        }

        try:
            await self.external_ws.send(json.dumps(msg))
            logger.info(f"Subscribed to: {symbols}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}", exc_info=True)

    async def unsubscribe_symbols(self, symbols: list):
        """Unsubscribe from symbols on Deribit"""
        if not symbols or not self.external_ws:
            return

        channels = [f"deribit_price_index.{sym}" for sym in symbols]

        msg = {
            "jsonrpc": "2.0",
            "id": 3600,
            "method": "public/unsubscribe",
            "params": {
                "channels": channels,
            },
        }

        try:
            await self.external_ws.send(json.dumps(msg))
            logger.info(f"Unsubscribed from: {symbols}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}", exc_info=True)


# Initialize the connection manager
manager = ConnectionManager()


async def shutdown_event():
    await manager.stop_master_connection()


app.add_event_handler("shutdown", shutdown_event)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_text()
                symbols = json.loads(data).get("params", {}).get("symbol", [])
                await manager.update_client_symbols(websocket, symbols)
            except (WebSocketDisconnect, ConnectionClosedOK):
                break
            except Exception as e:
                logger.error(f"Error handling client message: {e}", exc_info=True)
    finally:
        await manager.disconnect(websocket)


@app.get("/get_ws_data")
async def get_messages(symbol: str = None) -> list:
    await asyncio.sleep(1)
    symbols = symbol.split(",") if isinstance(symbol, str) else symbol
    msg = []
    if symbols:
        for sym in symbols:
            msg.append({"date": None, "symbol": sym, "price": 0})

    return msg


@app.get("/widgets.json")
async def get_widgets():
    """Get widgets."""
    return {
        "live_grid_example": {
            "name": "Live Grid",
            "description": "Live Grid",
            "type": "live_grid",
            "endpoint": "get_ws_data",
            "wsEndpoint": "ws",
            "data": {
                "wsRowIdColumn": "symbol",
                "table": {
                    "showAll": True,
                    "columnsDefs": [
                        {"field": "date", "headerName": "Date", "type": "date"},
                        {"field": "symbol", "headerName": "Symbol", "type": "text"},
                        {"field": "price", "headerName": "Price", "type": "number"},
                    ],
                },
            },
            "params": [
                {
                    "paramName": "symbol",
                    "description": "The symbol to get details for",
                    "value": None,
                    "label": "Symbol",
                    "type": "text",
                    "multiSelect": True,
                    "options": [
                        {"label": "BTC/USD", "value": "btc_usd"},
                        {"label": "ETH/USD", "value": "eth_usd"},
                        {"label": "SOL/USD", "value": "sol_usd"},
                        {"label": "XRP/USD", "value": "xrp_usd"},
                        {"label": "BNB/USD", "value": "bnb_usd"},
                        {"label": "MATIC/USD", "value": "matic_usd"},
                        {"label": "STETH/USD", "value": "steth_usd"},
                        {"label": "USYC/USD", "value": "usyc_usd"},
                        {"label": "USDC/USD", "value": "usdc_usd"},
                        {"label": "USDT/USD", "value": "usdt_usd"},
                        {"label": "USDE/USD", "value": "usde_usd"},
                        {"label": "PAXG/USD", "value": "paxg_usd"},
                    ],
                }
            ],
            "gridData": {"w": 15, "h": 9},
        }
    }


@app.get("/templates.json")
async def get_templates():
    """Get templates."""
    return []


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=6940)
