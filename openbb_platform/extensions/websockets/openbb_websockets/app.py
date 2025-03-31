import asyncio
import contextlib
import json
import logging
import queue
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import uvicorn
import websockets
from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

logger = logging.getLogger("uvicorn-error")


class ConnectionManager:
    def __init__(
        self,
        ws_uri: str = "wss://test.deribit.com/ws/api/v2",
        connection_msg: Optional[Dict] = None,
        process_message: Optional[Callable[[Dict], List[Dict]]] = None,
        format_subscribe: Optional[Callable[[List[str]], Dict]] = None,
        format_unsubscribe: Optional[Callable[[List[str]], Dict]] = None,
        connection_timeout: float = 15.0,
        retry_delay: float = 5.0,
        max_retries: int = 3,
    ):
        """Initialize a WebSocket connection manager

        Args:
            app: The FastAPI app instance to configure
            ws_uri: URI for the external WebSocket service
            connection_msg: Optional message to send on connection
            process_message: Function to process incoming messages
            format_subscribe: Function to format subscription requests
            format_unsubscribe: Function to format unsubscription requests
            connection_timeout: Timeout in seconds for connection attempts
            retry_delay: Delay in seconds between connection retries
            max_retries: Maximum number of connection retry attempts
        """
        # Create the FastAPI app
        self.app = FastAPI()

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Client connections and subscriptions
        self.active_connections: Set[WebSocket] = set()
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.symbol_subscribers: Dict[str, Set[WebSocket]] = {}

        # External WebSocket connection
        self.external_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.external_task: Optional[asyncio.Task] = None

        # Threading and queuing
        self.message_queue = queue.Queue()
        self.processor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.lock = asyncio.Lock()
        self.thread_running = False
        self.loop = None

        # Configuration
        self.ws_uri = ws_uri
        self.connection_msg = connection_msg
        self.connection_timeout = connection_timeout
        self.retry_delay = retry_delay
        self.max_retries = max_retries

        # Message handling functions
        self.process_message = process_message or self._default_process_message
        self.format_subscribe = format_subscribe or self._default_format_subscribe
        self.format_unsubscribe = format_unsubscribe or self._default_format_unsubscribe

        # Register endpoints with the app
        self._setup_app_routes()

    def _setup_app_routes(self):
        """Configure the FastAPI app with routes and event handlers"""

        @self.app.get("/")
        def read_root():
            return {
                "Info": "Live Grid Widget Example For OpenBB Workspace Custom Backend"
            }

        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.stop_master_connection()

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connect(websocket)
            try:
                while True:
                    try:
                        data = await websocket.receive_text()
                        symbols = json.loads(data).get("params", {}).get("symbol", [])
                        await self.update_client_symbols(websocket, symbols)
                    except (WebSocketDisconnect, ConnectionClosedOK):
                        break
                    except Exception as e:
                        logger.error(
                            f"Error handling client message: {e}", exc_info=True
                        )
            finally:
                await self.disconnect(websocket)

        @self.app.get("/control/subscribe")
        async def control_subscribe(symbols: str):
            """Subscribe to symbols from external control"""
            symbols = symbols.split(",") if isinstance(symbols, str) else symbols
            if not symbols:
                return {"success": False, "message": "No symbols provided"}

            if not self.external_ws:
                # Start the master connection if not already running
                if not self.is_running:
                    await self.start_master_connection()

                if not self.external_ws:
                    return {
                        "success": False,
                        "message": "Failed to establish external connection",
                    }

            # Add the symbols to a special control subscriber
            for symbol in symbols:
                if symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()

            # Subscribe to the symbols on the external service
            await self.subscribe_symbols(symbols)

            return {"success": True, "subscribed": symbols}

        @self.app.get("/master_stream")
        async def master_stream_endpoint():
            """Stream raw data directly from the master connection"""

            async def event_generator():
                async for message in self.get_master_stream():
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps(message)}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                },
            )

        @self.app.get("/control/status")
        async def control_status():
            """Get the status of the WebSocket connection"""
            return {
                "connected": self.is_running and self.external_ws is not None,
                "active_clients": len(self.active_connections),
                "subscribed_symbols": list(self.symbol_subscribers.keys()),
            }

        @self.app.get("/get_ws_data")
        async def get_messages(symbol: str = None) -> list:
            await asyncio.sleep(0.1)  # Quick response
            symbols = symbol.split(",") if isinstance(symbol, str) else symbol
            msg = []
            if symbols:
                for sym in symbols:
                    msg.append({"date": None, "symbol": sym, "price": 0})
            return msg

        @self.app.get("/widgets.json")
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
                                {
                                    "field": "symbol",
                                    "headerName": "Symbol",
                                    "type": "text",
                                },
                                {
                                    "field": "price",
                                    "headerName": "Price",
                                    "type": "number",
                                },
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

        @self.app.get("/templates.json")
        async def get_templates():
            """Get templates."""
            return []

        @self.app.get("/control/unsubscribe")
        async def control_unsubscribe(symbols: str):
            """Unsubscribe from symbols from external control"""
            symbols = symbols.split(",") if isinstance(symbols, str) else symbols
            if not symbols or not self.external_ws:
                return {
                    "success": False,
                    "message": "No symbols or no external connection",
                }

            to_unsubscribe = []
            for symbol in symbols:
                if (
                    symbol in self.symbol_subscribers
                    and not self.symbol_subscribers[symbol]
                ):
                    to_unsubscribe.append(symbol)

            if to_unsubscribe:
                await self.unsubscribe_symbols(to_unsubscribe)

                # Clean up the symbol subscribers dictionary
                for symbol in to_unsubscribe:
                    if (
                        symbol in self.symbol_subscribers
                        and not self.symbol_subscribers[symbol]
                    ):
                        del self.symbol_subscribers[symbol]

            return {"success": True, "unsubscribed": to_unsubscribe}

    async def get_master_stream(self):
        """
        Creates an async generator that yields messages directly from the master connection.
        This can be used to create streaming endpoints.

        Yields:
            Dict: Raw messages from the external WebSocket after parsing from JSON
        """
        if not self.external_ws:
            # Start the master connection if not already running
            if not self.is_running:
                await self.start_master_connection()

            if not self.external_ws:
                raise RuntimeError("Failed to establish external connection")

        # Create a message queue specifically for this stream
        stream_queue = asyncio.Queue()
        stream_id = str(uuid.uuid4())

        # Register this stream in a dictionary of active streams
        if not hasattr(self, "active_streams"):
            self.active_streams = {}
        self.active_streams[stream_id] = stream_queue

        try:
            while self.is_running and self.external_ws:
                try:
                    # Wait for a message to be added to this stream's queue
                    message = await asyncio.wait_for(stream_queue.get(), timeout=30.0)

                    # Parse and yield the message
                    if isinstance(message, str):
                        try:
                            yield json.loads(message)
                        except json.JSONDecodeError:
                            yield {"error": "Invalid JSON", "raw": message}
                    else:
                        yield message

                    # Mark as processed
                    stream_queue.task_done()

                except asyncio.TimeoutError:
                    # Send a heartbeat to keep the connection alive
                    yield {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                except Exception as e:
                    logger.error(f"Error in master stream: {e}", exc_info=True)
                    yield {"error": str(e)}
                    await asyncio.sleep(1)
        finally:
            # Clean up when the stream ends
            if hasattr(self, "active_streams") and stream_id in self.active_streams:
                del self.active_streams[stream_id]

    def _default_process_message(self, message_data: Dict) -> List[Dict]:
        """Default message processor for Deribit format"""
        results = []

        # Extract data from Deribit message format
        data = message_data.get("result") or message_data.get("params", {}).get(
            "data", {}
        )
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
                results.append(msg)

        return results

    def _default_format_subscribe(self, symbols: List[str]) -> Dict:
        """Default subscription formatter for Deribit"""
        channels = [f"deribit_price_index.{sym}" for sym in symbols]
        return {
            "jsonrpc": "2.0",
            "id": 3600,
            "method": "public/subscribe",
            "params": {
                "channels": channels,
            },
        }

    def _default_format_unsubscribe(self, symbols: List[str]) -> Dict:
        """Default unsubscription formatter for Deribit"""
        channels = [f"deribit_price_index.{sym}" for sym in symbols]
        return {
            "jsonrpc": "2.0",
            "id": 3600,
            "method": "public/unsubscribe",
            "params": {
                "channels": channels,
            },
        }

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

                        # If no more subscribers for this symbol, unsubscribe from external service
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
                    # Parse JSON message
                    message_data = (
                        json.loads(message) if isinstance(message, str) else message
                    )

                    # Process the message using the custom processor
                    processed_messages = self.process_message(message_data)

                    # Send each processed message to its subscribers
                    for msg in processed_messages:
                        symbol = msg.get("symbol")
                        if symbol:
                            subscribers = self.symbol_subscribers.get(
                                symbol, set()
                            ).copy()
                            if subscribers:
                                asyncio.run_coroutine_threadsafe(
                                    self.broadcast_to_subscribers(subscribers, msg),
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

    async def broadcast_to_subscribers(self, subscribers: Set[WebSocket], msg: Dict):
        """Broadcast a message to all specified subscribers"""
        for client in subscribers:
            try:
                await client.send_json(msg)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")

    async def start_master_connection(self):
        """Start a single master connection to the external WebSocket service"""
        # Clean up any existing connection first
        await self.stop_master_connection()

        retries = 0
        while retries <= self.max_retries:
            try:
                # Establish the WebSocket connection with timeout
                logger.info(
                    f"Connecting to {self.ws_uri} (attempt {retries + 1}/{self.max_retries + 1})"
                )
                self.external_ws = await asyncio.wait_for(
                    websockets.connect(self.ws_uri), timeout=self.connection_timeout
                )
                self.is_running = True

                # Send connection message if provided
                if self.connection_msg and self.external_ws:
                    await self.external_ws.send(json.dumps(self.connection_msg))

                # Start task to receive messages from external service
                self.external_task = asyncio.create_task(self.receive_from_external())

                # Store the event loop for the thread to use
                self.loop = asyncio.get_event_loop()

                # Start thread to process messages from the queue
                self.thread_running = True
                self.processor_thread = threading.Thread(
                    target=self.process_messages_thread, daemon=True
                )
                self.processor_thread.start()

                logger.info(f"Master connection to {self.ws_uri} established")

                # Resubscribe to all active symbols after reconnection
                await self.resubscribe_active_symbols()

                # Connection successful, exit retry loop
                break

            except asyncio.TimeoutError:
                retries += 1
                if retries <= self.max_retries:
                    logger.warning(
                        f"Connection attempt timed out, retrying in {self.retry_delay} seconds..."
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to connect after {self.max_retries + 1} attempts, giving up"
                    )
                    self.is_running = False

            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    logger.warning(
                        f"Connection error: {e}, retrying in {self.retry_delay} seconds..."
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to establish master connection: {e}", exc_info=True
                    )
                    self.is_running = False
                    break

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
        """Stop the master connection to the external WebSocket service"""
        self.is_running = False

        # Stop the message processing thread
        if self.processor_thread and self.processor_thread.is_alive():
            self.thread_running = False
            self.processor_thread.join(timeout=2.0)
            self.processor_thread = None

        # Cancel the task that receives messages from external service
        if self.external_task:
            self.external_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.external_task
            self.external_task = None

        # Close the WebSocket connection
        if self.external_ws:
            with contextlib.suppress(Exception):
                await self.external_ws.close()
            self.external_ws = None

        # Clear the message queue
        while True:
            try:
                self.message_queue.get_nowait()
                self.message_queue.task_done()
            except queue.Empty:
                break

        logger.info(f"Master connection to {self.ws_uri} closed")

    async def receive_from_external(self):
        """Receive messages from the external WebSocket and put them in the queue"""
        while self.is_running and self.external_ws:
            try:
                response = await asyncio.wait_for(
                    self.external_ws.recv(), timeout=30.0  # Add reasonable timeout
                )
                # Put the raw message in the queue for processing
                self.message_queue.put(response)

                if hasattr(self, "active_streams") and self.active_streams:
                    for stream_queue in self.active_streams.values():
                        await stream_queue.put(response)

            except asyncio.TimeoutError:
                # Just a timeout, not necessarily an error, try again
                continue
            except (ConnectionClosedOK, ConnectionClosedError, WebSocketDisconnect):
                logger.warning(
                    f"Connection to {self.ws_uri} closed, attempting to reconnect..."
                )
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
        await asyncio.sleep(self.retry_delay)

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
            to_add_to_external = []
            to_remove_from_external = []

            for symbol in to_subscribe:
                # Check if symbol exists but has no subscribers
                if (
                    symbol in self.symbol_subscribers
                    and not self.symbol_subscribers[symbol]
                ):
                    to_add_to_external.append(symbol)
                # Check if symbol doesn't exist at all
                elif symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()
                    to_add_to_external.append(symbol)
                self.symbol_subscribers[symbol].add(websocket)

            for symbol in to_unsubscribe:
                if symbol in self.symbol_subscribers:
                    self.symbol_subscribers[symbol].discard(websocket)
                    if not self.symbol_subscribers[symbol]:
                        to_remove_from_external.append(symbol)
                        # Don't delete the key here, we'll do it after unsubscribing

            # Make the actual subscription changes on external service
            if to_add_to_external and self.external_ws:
                await self.subscribe_symbols(to_add_to_external)

            if to_remove_from_external and self.external_ws:
                await self.unsubscribe_symbols(to_remove_from_external)
                # Now we can safely remove empty subscriber sets
                for symbol in to_remove_from_external:
                    if (
                        symbol in self.symbol_subscribers
                        and not self.symbol_subscribers[symbol]
                    ):
                        del self.symbol_subscribers[symbol]

    async def subscribe_symbols(self, symbols: list):
        """Subscribe to symbols on external service"""
        if not symbols or not self.external_ws:
            return

        # Format the subscription message using the configured formatter
        msg = self.format_subscribe(symbols)

        try:
            await self.external_ws.send(json.dumps(msg))
            logger.info(f"Subscribed to: {symbols}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}", exc_info=True)

    async def unsubscribe_symbols(self, symbols: list):
        """Unsubscribe from symbols on external service"""
        if not symbols or not self.external_ws:
            return

        # Format the unsubscription message using the configured formatter
        msg = self.format_unsubscribe(symbols)

        try:
            await self.external_ws.send(json.dumps(msg))
            logger.info(f"Unsubscribed from: {symbols}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}", exc_info=True)


def create_deribit_manager():
    """Create a ConnectionManager configured for Deribit"""

    # Create the Deribit message processor
    def process_deribit_message(message_data):
        results = []

        # Extract data from Deribit message format
        data = message_data.get("result") or message_data.get("params", {}).get(
            "data", {}
        )
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
                results.append(msg)

        return results

    # Create and return the connection manager
    return ConnectionManager(
        ws_uri="wss://test.deribit.com/ws/api/v2",
        process_message=process_deribit_message,
        connection_timeout=60,
        retry_delay=3,
        max_retries=2,
    )


def create_binance_manager():
    """Create a ConnectionManager configured for Binance"""

    # Create the Binance message processor and formatters
    def process_binance_message(message_data):
        results = []

        # For kline/candlestick data
        if "k" in message_data:
            symbol = message_data.get("s", "").lower()
            candle = message_data.get("k", {})

            if symbol and candle:
                msg = {
                    "date": datetime.fromtimestamp(
                        message_data.get("E", 0) / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "price": float(candle.get("c", 0)),
                }
                results.append(msg)

        return results

    def format_binance_subscribe(symbols):
        streams = [f"{sym.lower()}@kline_1m" for sym in symbols]
        return {"method": "SUBSCRIBE", "params": streams, "id": 1}

    def format_binance_unsubscribe(symbols):
        streams = [f"{sym.lower()}@kline_1m" for sym in symbols]
        return {"method": "UNSUBSCRIBE", "params": streams, "id": 1}

    # Create and return the connection manager
    return ConnectionManager(
        ws_uri="wss://stream.binance.com:9443/ws",
        process_message=process_binance_message,
        format_subscribe=format_binance_subscribe,
        format_unsubscribe=format_binance_unsubscribe,
        connection_timeout=10.0,
        retry_delay=3.0,
        max_retries=2,
    )


def run_websocket_server(manager_factory_func=create_deribit_manager, port: int = 6940):
    """Run a WebSocket server with the specified manager factory function"""
    manager = manager_factory_func()
    uvicorn.run(manager.app, host="0.0.0.0", port=port)


def start_server_subprocess(
    manager_factory_name: str = "create_deribit_manager", port: int = 6940
) -> tuple[subprocess.Popen, str]:
    """Start a WebSocket server in a subprocess and return a controller for it

    Args:
        manager_factory_name: Name of the manager factory function to use
        port: Port number to run the server on

    Returns:
        Tuple of (subprocess object, base URL for server)
    """
    import time

    # Get the path to this script
    script_path = Path(__file__).resolve()

    # Start the server in a subprocess
    cmd = [
        sys.executable,
        str(script_path),
        "--factory",
        manager_factory_name,
        "--port",
        str(port),
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give the server a moment to start
    time.sleep(1.0)

    # Return the process and the base URL for communicating with it
    base_url = f"http://localhost:{port}"
    return process, base_url


# When running this file directly
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start a WebSocket server")
    parser.add_argument(
        "--factory",
        default="create_deribit_manager",
        help="Name of the manager factory function to use",
    )
    parser.add_argument(
        "--port", type=int, default=6940, help="Port to run the server on"
    )
    args = parser.parse_args()

    # Select the factory function based on the argument
    factory_map = {
        "create_deribit_manager": create_deribit_manager,
        "create_binance_manager": create_binance_manager,
    }

    selected_factory = factory_map.get(args.factory)
    if not selected_factory:
        print(f"Unknown factory function: {args.factory}")
        sys.exit(1)

    # Run the server
    run_websocket_server(selected_factory, args.port)
