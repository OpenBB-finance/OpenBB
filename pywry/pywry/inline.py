"""FastAPI-based inline notebook rendering for PyWry.

Like Dash, this runs a local server and displays via IFrame.
Supports ALL PyWry features: HTML content, Plotly, AG Grid, callbacks.
"""
# pylint: disable=too-many-lines,wrong-import-position
# mypy: disable-error-code="import-untyped,no-untyped-call,no-any-return"

from __future__ import annotations

import asyncio
import json
import os
import queue
import threading
import time
import uuid

from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING, Any, Literal


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from .grid import GridConfig

    try:
        from plotly.graph_objects import Figure

        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

# Check for debug mode environment variable
PYWRY_DEBUG = os.environ.get("PYWRY_DEBUG", "").lower() in ("1", "true", "yes", "on")

try:
    import uvicorn

    from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    from IPython.display import HTML, display  # noqa: F401  # pylint: disable=unused-import
    from ipywidgets import Output

    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False
    # Stub for type hints when IPython not available
    Output = None

from .assets import (  # noqa: E402
    get_aggrid_css,
    get_aggrid_defaults_js,
    get_aggrid_js,
    get_plotly_js,
    get_plotly_templates_js,
    get_pywry_css,
)
from .config import get_settings  # noqa: E402
from .models import ThemeMode  # noqa: E402
from .templates import build_toolbar_html  # noqa: E402
from .widget_protocol import BaseWidget  # noqa: E402, TC001


# Global server state
class _ServerState:
    def __init__(self) -> None:
        self.server: Any = None
        self.server_thread: threading.Thread | None = None
        self.server_loop: Any = None
        self.app: FastAPI | None = None
        self.port: int | None = None
        self.host: str | None = None
        self.widgets: dict[str, dict[str, Any]] = {}
        self.event_queues: dict[str, asyncio.Queue[Any]] = {}
        self.connections: dict[str, WebSocket] = {}
        self.callback_queue: queue.Queue[Any] = queue.Queue()
        self.shutdown_event: asyncio.Event | None = None


_state = _ServerState()


def _get_pywry_bridge_js(widget_id: str) -> str:
    """Generate the pywry JavaScript bridge with bidirectional communication.

    Supports:
    - JS → Python via WebSocket
    - Python → JS via WebSocket
    """
    return f"""
<script>
(function() {{
    const widgetId = '{widget_id}';
    // Use window.location to get current host/port (same as IFrame)
    const protocol = window.location.protocol;
    const host = window.location.hostname;
    const port = window.location.port;
    const apiUrl = protocol + '//' + host + (port ? ':' + port : '');

    // WebSocket connection
    const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = wsProtocol + '//' + host + (port ? ':' + port : '') + '/ws/' + widgetId;
    let socket = null;
    let reconnectAttempts = 0;

    window.pywry = {{
        _ready: false,
        _handlers: {{}},
        _pending: [],
        _msgQueue: [],
        _widgetId: widgetId,

        result: function(data) {{
            this.emit('pywry:result', data);
        }},

        // Send event to Python via WebSocket
        emit: function(type, data) {{
            const msg = {{ type: type, data: data, widgetId: widgetId, ts: Date.now() }};

            if (!socket || socket.readyState !== WebSocket.OPEN) {{
                console.warn('[PyWry] WebSocket not ready, queueing emit:', type);
                this._msgQueue.push(msg);
                return;
            }}

            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Sending via WS:', msg);
            }}
            socket.send(JSON.stringify(msg));
        }},

        // Register listener for events from Python
        on: function(type, callback) {{
            if (!this._handlers[type]) this._handlers[type] = [];
            this._handlers[type].push(callback);
            // Call with any pending events
            const pending = this._pending.filter(p => p.type === type);
            this._pending = this._pending.filter(p => p.type !== type);
            pending.forEach(p => callback(p.data));
        }},

        // Internal: Fire event to registered handlers
        _fire: function(type, data) {{
            const handlers = this._handlers[type] || [];
            if (handlers.length === 0) {{
                this._pending.push({{type: type, data: data}});
            }} else {{
                handlers.forEach(h => h(data));
            }}
        }},

        send: function(data) {{
            this.emit('pywry:message', data);
        }}
    }};

    function connect() {{
        if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {{
            return;
        }}

        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Connecting to WebSocket:', wsUrl);
        }}

        socket = new WebSocket(wsUrl);

        socket.onopen = function() {{
            console.log('[PyWry] WebSocket connected');
            reconnectAttempts = 0;

            // Flush pending outgoing messages
            if (window.pywry._msgQueue && window.pywry._msgQueue.length > 0) {{
                if ({str(PYWRY_DEBUG).lower()}) {{
                    console.log('[PyWry] Flushing ' + window.pywry._msgQueue.length + ' queued messages');
                }}
                window.pywry._msgQueue.forEach(function(msg) {{
                    socket.send(JSON.stringify(msg));
                }});
                window.pywry._msgQueue = [];
            }}

            window.pywry._ready = true;
            window.pywry._fire('pywry:ready', {{}});
        }};

        socket.onmessage = function(event) {{
            try {{
                const msg = JSON.parse(event.data);
                if ({str(PYWRY_DEBUG).lower()}) {{
                    console.log('[PyWry] WebSocket received:', msg);
                }}

                // Handle single event or list of events
                const events = msg.events || [msg];
                events.forEach(e => {{
                    if (e && e.type) {{
                        window.pywry._fire(e.type, e.data);
                    }}
                }});
            }} catch (err) {{
                console.error('[PyWry] Error parsing message:', err);
            }}
        }};

        socket.onclose = function(e) {{
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] WebSocket closed. Code:', e.code, 'Reason:', e.reason);
            }}
            window.pywry._ready = false;

            // Reconnect with backoff
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
            reconnectAttempts++;
            setTimeout(connect, delay);
        }};

        socket.onerror = function(err) {{
            console.error('[PyWry] WebSocket error:', err);
            socket.close();
        }};
    }}

    // Connect immediately
    connect();
    window.pywry._ready = true;
    if ({str(PYWRY_DEBUG).lower()}) {{
        console.log('[PyWry] Bridge ready! widgetId:', widgetId);
        console.log('[PyWry] window.pywry object:', window.pywry);
    }}

    // Register handler for theme updates - update grid theme class
    window.pywry.on('pywry:update_theme', function(data) {{
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Received theme update:', data.theme);
        }}

        // Update document theme class for CSS variables (Toolbar, etc.)
        if (data.theme && data.theme.includes('light')) {{
            document.documentElement.className = 'light';
            document.documentElement.classList.add('light');
            document.documentElement.classList.remove('dark');
        }} else {{
            document.documentElement.className = 'dark';
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        }}

        const gridDiv = document.getElementById('grid');
        if (gridDiv && data.theme) {{
            // Remove all ag-theme-* classes
            gridDiv.className = gridDiv.className.replace(/ag-theme-[\\w-]+/g, '').trim();
            // Add new theme class
            gridDiv.className = (gridDiv.className + ' ' + data.theme).trim();
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Updated grid theme class to:', data.theme);
            }}
        }}
    }});

    // Register handler for HTML content updates - reload the page to get new content
    window.pywry.on('pywry:update_html', function(data) {{
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Received HTML update, reloading page');
        }}
        // Add small delay to ensure server state is updated before reload
        setTimeout(function() {{
            window.location.reload();
        }}, 50);
    }});

    // Register handler for Plotly figure updates - use Plotly.react for smooth updates
    window.pywry.on('pywry:update_plotly', function(data) {{
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Received Plotly update:', data);
        }}
        const chartEl = document.getElementById('chart');
        if (chartEl && data.figure && typeof Plotly !== 'undefined') {{
            const figData = data.figure;
            const config = data.config || {{}};

            // Process modebar button click handlers (convert string to function)
            if (config.modeBarButtonsToAdd) {{
                config.modeBarButtonsToAdd = config.modeBarButtonsToAdd.map(function(btn) {{
                    if (typeof btn.click === 'string') {{
                        try {{
                            btn.click = eval('(' + btn.click + ')');
                        }} catch(e) {{
                            console.error('[PyWry] Failed to parse button click:', e);
                        }}
                    }}
                    return btn;
                }});
            }}

            Plotly.react(chartEl, figData.data, figData.layout, config).then(function() {{
                if ({str(PYWRY_DEBUG).lower()}) {{
                    console.log('[PyWry] Plotly chart updated successfully');
                }}
            }});
        }}
    }});

    window.pywry._fire('pywry:ready', {{}});

    if ({str(PYWRY_DEBUG).lower()}) {{
        console.log('[PyWry] Bridge initialized for widget:', widgetId);
        console.log('[PyWry] API URL:', apiUrl);
    }}
}})();
</script>
"""


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:  # pylint: disable=unused-argument
    _state.shutdown_event = asyncio.Event()
    yield


async def _ws_sender_loop(
    event_queue: asyncio.Queue[Any], websocket: WebSocket, widget_id: str
) -> None:
    """Pump events from queue to websocket until cancelled."""
    try:
        while True:
            event = await event_queue.get()
            if PYWRY_DEBUG:
                print(f"[SERVER] Sending event to {widget_id}: {event}")
            await websocket.send_json(event)
            event_queue.task_done()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        if PYWRY_DEBUG:
            print(f"[SERVER] Sender error for {widget_id}: {e}")


def _route_ws_message(widget_id: str, msg: dict[str, Any]) -> None:
    """Route incoming websocket message to callback queue if handler exists."""
    if widget_id not in _state.widgets:
        return
    callbacks = _state.widgets[widget_id].get("callbacks", {})
    event_type = msg.get("type", "")
    if event_type in callbacks:
        _state.callback_queue.put(
            (callbacks[event_type], msg.get("data", {}), event_type, widget_id)
        )


def _get_app() -> FastAPI:  # noqa: C901, PLR0915  # pylint: disable=too-many-statements
    """Get or create the FastAPI app."""
    if _state.app is not None:
        return _state.app

    app = FastAPI(lifespan=_lifespan)
    settings = get_settings().server

    # CORS middleware with configurable settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    _state.app = app

    @app.get("/widget/{widget_id}", response_class=HTMLResponse)
    async def get_widget(widget_id: str) -> HTMLResponse:
        import time  # pylint: disable=redefined-outer-name,reimported

        if PYWRY_DEBUG:
            print(f"[SERVER] /widget/{widget_id} accessed at {time.time()}")
        if widget_id not in _state.widgets:
            return HTMLResponse("<h1>Widget not found</h1>", status_code=404)

        widget_data = _state.widgets[widget_id]
        if PYWRY_DEBUG:
            print(f"[SERVER] Serving HTML for {widget_id}, length: {len(widget_data['html'])}")

        # Add headers to prevent browser caching
        return HTMLResponse(
            widget_data["html"],
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.websocket("/ws/{widget_id}")
    async def websocket_endpoint(websocket: WebSocket, widget_id: str) -> None:
        if PYWRY_DEBUG:
            print(f"[SERVER] WebSocket connection request for {widget_id}")

        await websocket.accept()

        if widget_id in _state.connections:
            if PYWRY_DEBUG:
                print(f"[SERVER] Closing existing connection for {widget_id}")
            with suppress(Exception):
                await _state.connections[widget_id].close(
                    code=1000, reason="New connection replaced old one"
                )

        _state.connections[widget_id] = websocket

        if widget_id not in _state.event_queues:
            _state.event_queues[widget_id] = asyncio.Queue()

        event_queue = _state.event_queues[widget_id]
        sender = asyncio.create_task(_ws_sender_loop(event_queue, websocket, widget_id))

        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if PYWRY_DEBUG:
                    print(f"[SERVER] Received from {widget_id}: {msg}")
                _route_ws_message(widget_id, msg)
        except WebSocketDisconnect:
            if PYWRY_DEBUG:
                print(f"[SERVER] WebSocket disconnected for {widget_id}")
            if widget_id in _state.connections and _state.connections[widget_id] == websocket:
                del _state.connections[widget_id]
        finally:
            sender.cancel()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/register_widget")
    async def register_widget(request: Request) -> dict[str, str]:
        """Register a widget with the running server (for kernel restart scenarios)."""
        try:
            data = await request.json()
            widget_id = data.get("widget_id")
            html = data.get("html")

            if not widget_id or not html:
                return {"error": "Missing widget_id or html"}

            _state.widgets[widget_id] = {"html": html, "callbacks": {}}
            _state.event_queues[widget_id] = asyncio.Queue()

            return {"status": "registered", "widget_id": widget_id}  # noqa: TRY300
        except Exception as e:
            return {"error": str(e)}

    return app


def _process_callbacks() -> None:
    """Background thread to process callbacks."""
    while True:
        try:
            callback, data, event_type, widget_id = _state.callback_queue.get(timeout=0.1)
            try:
                # Get the output widget for this widget if it exists
                widget_data = _state.widgets.get(widget_id, {})
                output_widget = widget_data.get("output")

                if output_widget is not None:
                    # MUST manually capture stdout - ipywidgets context manager
                    # doesn't work from background threads!
                    import io
                    import sys

                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    captured_stdout = io.StringIO()
                    captured_stderr = io.StringIO()

                    try:
                        sys.stdout = captured_stdout
                        sys.stderr = captured_stderr
                        callback(data, event_type, widget_id)
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr

                    # Append captured output to the widget
                    stdout_text = captured_stdout.getvalue()
                    stderr_text = captured_stderr.getvalue()

                    if stdout_text:
                        output_widget.append_stdout(stdout_text)
                    if stderr_text:
                        output_widget.append_stderr(stderr_text)
                else:
                    # No output widget - just call directly
                    callback(data, event_type, widget_id)
            except Exception as e:
                if output_widget is not None:
                    output_widget.append_stderr(f"[PyWry] Callback error: {e}\n")
                else:
                    print(f"[PyWry] Callback error: {e}")
        except queue.Empty:
            pass
        except Exception:  # noqa: S110
            pass


def _start_server(port: int | None = None, host: str | None = None) -> None:  # noqa: C901, PLR0915  # pylint: disable=too-many-statements
    """Start the FastAPI server in a background thread.

    Parameters
    ----------
    port : int, optional
        Server port. Defaults to settings.server.port.
    host : str, optional
        Server host. Defaults to settings.server.host.
    """
    settings = get_settings().server

    _state.port = port or settings.port
    _state.host = host or settings.host

    if _state.server_thread is not None and _state.server_thread.is_alive():
        return  # Already running

    app = _get_app()

    # Build uvicorn config from settings
    config_kwargs: dict[str, Any] = {
        "app": app,
        "host": _state.host,
        "port": _state.port,
        "log_level": "critical",  # Suppress all but critical errors during shutdown
        "access_log": settings.access_log,
        "timeout_keep_alive": settings.timeout_keep_alive,
        "backlog": settings.backlog,
    }

    # Optional settings (only add if set)
    if settings.timeout_graceful_shutdown is not None:
        config_kwargs["timeout_graceful_shutdown"] = settings.timeout_graceful_shutdown
    if settings.limit_concurrency is not None:
        config_kwargs["limit_concurrency"] = settings.limit_concurrency
    if settings.limit_max_requests is not None:
        config_kwargs["limit_max_requests"] = settings.limit_max_requests

    # SSL settings
    if settings.ssl_certfile:
        config_kwargs["ssl_certfile"] = settings.ssl_certfile
    if settings.ssl_keyfile:
        config_kwargs["ssl_keyfile"] = settings.ssl_keyfile
    if settings.ssl_keyfile_password:
        config_kwargs["ssl_keyfile_password"] = settings.ssl_keyfile_password
    if settings.ssl_ca_certs:
        config_kwargs["ssl_ca_certs"] = settings.ssl_ca_certs

    config = uvicorn.Config(**config_kwargs)
    _state.server = uvicorn.Server(config)

    # Store the loop so we can shut it down properly
    _state.server_loop = None

    def run() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _state.server_loop = loop
        try:
            loop.run_until_complete(_state.server.serve())
        except RuntimeError as e:
            # Expected when loop.stop() is called from stop_server()
            if "Event loop stopped before Future completed" not in str(e):
                raise
        except asyncio.CancelledError:
            # Expected when tasks are cancelled during shutdown
            pass
        finally:
            # Clean up any pending tasks - suppress all errors during cleanup
            with suppress(RuntimeError):
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
            with suppress(RuntimeError):
                loop.close()

    _state.server_thread = threading.Thread(target=run, daemon=True)
    _state.server_thread.start()

    # Start callback processor
    callback_thread = threading.Thread(target=_process_callbacks, daemon=True)
    callback_thread.start()

    # Wait for server to start
    import requests

    protocol = "https" if settings.ssl_certfile else "http"
    health_url = f"{protocol}://{_state.host}:{_state.port}/health"

    for _ in range(50):
        try:
            r = requests.get(health_url, timeout=0.1, verify=False)  # noqa: S501
            if r.status_code == 200:
                break
        except Exception:  # noqa: S110
            pass
        time.sleep(0.1)


def stop_server(timeout: float = 5.0) -> None:
    """Stop the FastAPI server and wait for it to fully release the port.

    Parameters
    ----------
    timeout : float
        Maximum time to wait for server to stop, in seconds.
    """
    if _state.server is not None:
        # Signal the server to exit
        _state.server.should_exit = True

        # Send a request to wake up the server so it checks should_exit
        if _state.port is not None and _state.host is not None:
            import requests

            with suppress(Exception):
                requests.get(
                    f"http://{_state.host}:{_state.port}/health",
                    timeout=0.5,
                )

        # Wait for graceful shutdown
        if _state.server_thread is not None and _state.server_thread.is_alive():
            _state.server_thread.join(timeout=timeout)

        # Give OS time to release the socket
        time.sleep(0.3)

        _state.server = None
        _state.server_thread = None
        _state.server_loop = None
        _state.port = None
        _state.app = None
        _state.shutdown_event = None


class InlineWidget:
    """Base inline widget that renders via FastAPI server and IFrame.

    Implements BaseWidget protocol for unified API across rendering backends.
    """

    def __init__(
        self,
        html: str,
        callbacks: dict[str, Callable[..., Any]] | None = None,
        width: str = "100%",
        height: int = 500,
        port: int | None = None,
        widget_id: str | None = None,
    ) -> None:
        if not HAS_FASTAPI:
            raise ImportError("fastapi and uvicorn required: pip install fastapi uvicorn")
        if not HAS_IPYTHON:
            raise ImportError("IPython required for notebook display")

        self._widget_id = widget_id or uuid.uuid4().hex
        self._width = width
        self._height = height
        self._port = port or get_settings().server.port
        self._callbacks = callbacks or {}

        # Create an Output widget to capture callback output in the correct cell
        self._output = Output()

        # Register widget with output
        _state.widgets[self._widget_id] = {
            "html": html,
            "callbacks": self._callbacks,
            "output": self._output,
        }

        # Check if server is already running (e.g., after kernel restart)
        server_already_running = False
        try:
            import requests

            response = requests.get(f"http://127.0.0.1:{self._port}/health", timeout=0.5)
            if response.status_code == 200:
                server_already_running = True
        except Exception:  # noqa: S110
            pass

        # Check if server is running in THIS process (internal server)
        # If so, we don't need to register via HTTP because we already updated _state.widgets directly
        is_internal_server = _state.server_thread is not None and _state.server_thread.is_alive()

        # If server is already running AND NOT internal, register widget via HTTP
        # (This handles kernel restarts where the server process is still alive but state is lost)
        if server_already_running and not is_internal_server:
            try:
                import requests

                response = requests.post(
                    f"http://127.0.0.1:{port}/register_widget",
                    json={"widget_id": self._widget_id, "html": html},
                    timeout=1.0,
                )
                if response.status_code == 200:
                    # Successfully registered with running server
                    pass
            except Exception:  # noqa: S110
                # If registration fails, fall back to starting new server
                pass

        # Start server if not already running
        _start_server(port)

        # Initialize event queue on the server loop
        if _state.server_loop and _state.server_loop.is_running():

            async def _init_queue() -> None:
                if self._widget_id not in _state.event_queues:
                    _state.event_queues[self._widget_id] = asyncio.Queue()

            future = asyncio.run_coroutine_threadsafe(_init_queue(), _state.server_loop)
            with suppress(Exception):
                future.result(timeout=1.0)

    @property
    def widget_id(self) -> str:
        """Get the widget ID."""
        return self._widget_id

    @property
    def output(self) -> Output:
        """Get the Output widget for callback output."""
        return self._output

    def on(
        self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
    ) -> InlineWidget:
        """Register a callback for events from JavaScript.

        Parameters
        ----------
        event_type : str
            Event name (e.g., 'plotly_click', 'toggle', 'cell_click').
        callback : Callable[[dict[str, Any], str, str], Any]
            Handler function receiving (data, event_type, label).

        Returns
        -------
        InlineWidget
            Self for method chaining.
        """
        self._callbacks[event_type] = callback
        _state.widgets[self._widget_id]["callbacks"] = self._callbacks
        return self

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Send an event from Python to JavaScript.

        Parameters
        ----------
        event_type : str
            Event name that JS listeners can subscribe to.
        data : dict[str, Any]
            JSON-serializable payload to send to JavaScript.
        """
        event = {"type": event_type, "data": data, "ts": uuid.uuid4().hex}

        if _state.server_loop and _state.server_loop.is_running():

            async def _send() -> None:
                if self._widget_id not in _state.event_queues:
                    _state.event_queues[self._widget_id] = asyncio.Queue()
                await _state.event_queues[self._widget_id].put(event)

            asyncio.run_coroutine_threadsafe(_send(), _state.server_loop)

    def send(self, event_type: str, data: Any) -> None:
        """Alias for emit().

        Parameters
        ----------
        event_type : str
            The event type (e.g., 'update_theme', 'custom_event').
        data : Any
            The event data (will be JSON-serialized and sent to JS).
        """
        self.emit(event_type, data)

    def update(self, html: str) -> None:
        """Update the widget's HTML content.

        Parameters
        ----------
        html : str
            New HTML content to render. Should include necessary <script> tags.
        """
        _state.widgets[self._widget_id]["html"] = html

        # Send update event to JavaScript to refresh the IFrame content
        self.emit("pywry:update_html", {"html": html})

    def update_html(self, html: str) -> None:
        """Alias for update()."""
        self.update(html)

    def _repr_html_(self) -> str:
        """HTML representation with IFrame.

        Note: This only returns the IFrame. For callback output, use display() method
        or access the .output property directly.
        """
        from IPython.display import IFrame

        # Add cache busting to prevent caching issues
        host = get_settings().server.host
        url = f"http://{host}:{self._port}/widget/{self._widget_id}?ts={uuid.uuid4().hex}"

        return IFrame(url, width=self._width, height=self._height)._repr_html_()

    def _repr_mimebundle_(self, **kwargs: Any) -> dict[str, str]:  # pylint: disable=unused-argument
        """Return mimebundle for rich display with Output widget."""
        # This is used when the object is returned by a cell
        from IPython.display import display as ipy_display

        # Display Output widget first (side effect)
        if self._output:
            ipy_display(self._output)

        # Return HTML for the main display
        return {"text/html": self._repr_html_()}

    def display(self) -> None:
        """Display the widget in the current output context.

        For Jupyter notebooks, displays the IFrame and output widget for callback messages.
        """
        from IPython.display import IFrame, display as ipy_display

        # Add cache busting to prevent caching issues
        host = get_settings().server.host
        url = f"http://{host}:{self._port}/widget/{self._widget_id}?ts={uuid.uuid4().hex}"

        # Display IFrame directly using IPython's class to avoid warnings
        ipy_display(IFrame(url, width=self._width, height=self._height))

        # Display Output widget below it for callback output
        if self._output:
            ipy_display(self._output)

    def update_figure(self, figure: Figure) -> None:
        """Update the Plotly figure without manual HTML generation.

        Parameters
        ----------
        figure : plotly.graph_objects.Figure
            New Plotly figure to display.

        Examples
        --------
        >>> widget.update_figure(new_fig)  # Clean API!
        """
        # Convert figure to dict
        fig_dict = json.loads(figure.to_json())
        stored_config = getattr(self, "_plotly_config", None)

        # NOTE: For InlineWidget, we send an update event for the partial plot update.
        # This keeps the rest of the page (including toolbar) intact.
        # If we wanted to replace the toolbar, we'd need to reload the whole HTML.
        # For full replacement, see update_html.

        # Send update via Plotly.react (no page reload needed)
        self.emit("pywry:update_plotly", {"figure": fig_dict, "config": stored_config or {}})

    def update_cell(self, row_index: int, col_id: str, value: Any) -> None:
        """Update a single cell value in the grid.

        This is more efficient than update_data() when changing just one cell,
        as it uses AG Grid's transaction API to update in-place without
        replacing the entire dataset.

        Parameters
        ----------
        row_index : int
            The row index (0-based) of the cell to update.
        col_id : str
            The column field name (colId) of the cell to update.
        value : Any
            The new value for the cell.

        Examples
        --------
        >>> widget.update_cell(0, "price", 29.99)
        >>> widget.update_cell(2, "status", "active")
        """
        self.emit("pywry:update_cell", {"rowIndex": row_index, "colId": col_id, "value": value})

    def update_data(self, data: Any) -> None:
        """Update the grid's row data.

        Parameters
        ----------
        data : DataFrame | list[dict] | dict[str, list]
            New data to display. Can be pandas DataFrame, list of row dicts,
            or dict of columns.

        Examples
        --------
        >>> widget.update_data(new_df)
        >>> widget.update_data([{"a": 1}, {"a": 2}])
        """
        row_data = self._normalize_data(data)
        self.emit("pywry:update_rows", {"rows": row_data})

    def update_columns(self, columns: list[dict[str, Any]]) -> None:
        """Update the grid's column definitions.

        Parameters
        ----------
        columns : list[dict]
            List of AG Grid column definitions.

        Examples
        --------
        >>> widget.update_columns(
        ...     [
        ...         {"field": "name", "headerName": "Name"},
        ...         {"field": "value", "headerName": "Value", "type": "numericColumn"},
        ...     ]
        ... )
        """
        self.emit("pywry:update_columns", {"columnDefs": columns})

    def update_grid(
        self,
        data: Any = None,
        columns: list[dict[str, Any]] | None = None,
        preserve_state: bool = True,
        restore_state: dict[str, Any] | None = None,
    ) -> None:
        """Update both row data and column definitions atomically.

        Parameters
        ----------
        data : DataFrame | list[dict] | dict[str, list], optional
            New row data.
        columns : list[dict], optional
            New column definitions.
        preserve_state : bool, default True
            If True, preserve column visibility, pinning, width, and order
            for columns that exist in both old and new definitions.
            Ignored if restore_state is provided.
        restore_state : dict, optional
            Explicit state to restore after updating. Use this when switching
            between views with different column structures. The state should
            have been saved from a previous view with the same columns.

        Examples
        --------
        >>> widget.update_grid(new_df, new_columns)
        >>> widget.update_grid(new_df, new_columns, preserve_state=False)  # Reset state
        >>> widget.update_grid(
        ...     new_df, new_columns, restore_state=saved_state
        ... )  # Restore specific state
        """
        payload: dict[str, Any] = {"preserveState": preserve_state}
        if data is not None:
            payload["rows"] = self._normalize_data(data)
        if columns is not None:
            payload["columnDefs"] = columns
        if restore_state is not None:
            payload["restoreState"] = restore_state
        if payload:
            self.emit("pywry:update_grid", payload)

    def request_grid_state(self, context: dict[str, Any] | None = None) -> None:
        """Request the grid's current state.

        The grid will emit a 'grid:state_response' event with the state data.
        Register a callback for 'grid:state_response' to receive the state.

        Parameters
        ----------
        context : dict, optional
            Additional context to include in the response for correlation.

        Examples
        --------
        >>> def on_state(data, event_type, label):
        ...     print(f"Got state: {data}")
        >>> widget.on("grid:state_response", on_state)
        >>> widget.request_grid_state({"view": "current_view"})
        """
        payload: dict[str, Any] = {}
        if context:
            payload["context"] = context
        self.emit("grid:request_state", payload)

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously saved grid state.

        Parameters
        ----------
        state : dict
            State object from a previous 'grid_state_saved' event.
        """
        self.emit("pywry:restore_state", {"state": state})

    def reset_state(self) -> None:
        """Reset grid to its default state.

        Clears all column customizations (width, order, visibility, pinning)
        and removes all filters.
        """
        self.emit("pywry:reset_state", {})

    # =========================================================================
    # Toolbar State Methods
    # =========================================================================

    def request_toolbar_state(
        self, toolbar_id: str | None = None, context: dict[str, Any] | None = None
    ) -> None:
        """Request the current state of toolbar components.

        The widget will emit a 'toolbar:state_response' event with the state data.
        Register a callback for 'toolbar:state_response' to receive the state.

        Parameters
        ----------
        toolbar_id : str, optional
            Specific toolbar ID to query. If None, returns state of all toolbars.
        context : dict, optional
            Additional context to include in the response for correlation.

        Examples
        --------
        >>> def on_state(data, event_type, label):
        ...     print(f"Toolbar state: {data}")
        >>> widget.on("toolbar:state_response", on_state)
        >>> widget.request_toolbar_state()
        """
        payload: dict[str, Any] = {}
        if toolbar_id:
            payload["toolbarId"] = toolbar_id
        if context:
            payload["context"] = context
        self.emit("toolbar:request_state", payload)

    def get_toolbar_value(self, component_id: str, context: dict[str, Any] | None = None) -> None:
        """Request the current value of a specific toolbar component.

        The widget will emit a 'toolbar:state_response' event with the value.
        Register a callback for 'toolbar:state_response' to receive it.

        Parameters
        ----------
        component_id : str
            The component_id of the toolbar item to query.
        context : dict, optional
            Additional context to include in the response.

        Examples
        --------
        >>> def on_value(data, event_type, label):
        ...     print(f"Component value: {data['value']}")
        >>> widget.on("toolbar:state_response", on_value)
        >>> widget.get_toolbar_value("my-select")
        """
        payload: dict[str, Any] = {"componentId": component_id}
        if context:
            payload["context"] = context
        self.emit("toolbar:request_state", payload)

    def set_toolbar_value(self, component_id: str, value: Any) -> None:
        """Set the value of a specific toolbar component.

        Parameters
        ----------
        component_id : str
            The component_id of the toolbar item to update.
        value : Any
            The new value for the component.
            - For Select: string value
            - For MultiSelect: list of string values
            - For TextInput: string
            - For NumberInput/RangeInput: number
            - For DateInput: string (YYYY-MM-DD format)

        Examples
        --------
        >>> widget.set_toolbar_value("theme-select", "dark")
        >>> widget.set_toolbar_value("columns-multiselect", ["name", "age"])
        >>> widget.set_toolbar_value("search-input", "query text")
        """
        self.emit("toolbar:set_value", {"componentId": component_id, "value": value})

    def set_toolbar_values(self, values: dict[str, Any]) -> None:
        """Set multiple toolbar component values at once.

        Parameters
        ----------
        values : dict[str, Any]
            Mapping of component_id to value.

        Examples
        --------
        >>> widget.set_toolbar_values(
        ...     {
        ...         "theme-select": "dark",
        ...         "columns-multiselect": ["name", "age"],
        ...         "limit-number": 50,
        ...     }
        ... )
        """
        self.emit("toolbar:set_values", {"values": values})

    def _normalize_data(self, data: Any) -> list[dict[str, Any]]:
        """Convert various data formats to list of row dicts.

        Parameters
        ----------
        data : DataFrame | list[dict] | dict[str, list]
            Input data in any supported format.

        Returns
        -------
        list[dict]
            Normalized row data as list of dictionaries.
        """
        # Handle pandas DataFrame (duck typing)
        if hasattr(data, "to_dict") and hasattr(data, "columns"):
            return data.to_dict(orient="records")
        # Handle list of dicts
        if isinstance(data, list):
            return data
        # Handle dict of lists
        if isinstance(data, dict):
            cols = list(data.keys())
            if cols:
                length = len(data[cols[0]])
                return [{col: data[col][i] for col in cols} for i in range(length)]
        return []


def show(  # noqa: C901, PLR0912, PLR0915  # pylint: disable=too-many-arguments,too-many-branches,too-many-statements
    content: str,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: Literal["dark", "light"] = "dark",
    callbacks: dict[str, Callable[..., Any]] | None = None,
    include_plotly: bool = False,
    include_aggrid: bool = False,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    toolbars: list[dict[str, Any]] | None = None,
    port: int | None = None,
) -> InlineWidget:
    """Show HTML content inline in a notebook.

    This is the notebook-compatible version of PyWry.show().
    Renders content via local FastAPI server + IFrame with WebSocket callbacks.

    Parameters
    ----------
    content : str
        HTML content to display.
    title : str
        Page title.
    width : str
        IFrame width (CSS value).
    height : int
        IFrame height in pixels.
    theme : 'dark' or 'light'
        Color theme.
    callbacks : dict[str, Callable]
        Event callbacks: {event_type: handler_function}.
    include_plotly : bool
        Include Plotly.js library.
    include_aggrid : bool
        Include AG Grid library.
    aggrid_theme : str
        AG Grid theme name.
    toolbars : list[dict], optional
        List of toolbar configurations, each with:
        - position: "top", "bottom", "left", "right", "inside"
        - items: list of item configs (button, select, text, number, date, range, multiselect)
    port : int, optional
        Server port (defaults to settings.server.port).

    Returns
    -------
    InlineWidget
        Widget instance for registering additional callbacks.
    """
    from .templates import (  # pylint: disable=redefined-outer-name,reimported
        ThemeMode,
        build_toolbar_html,
    )

    widget_id = uuid.uuid4().hex

    # Generate toolbar HTML from toolbars config
    mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
    if toolbars:
        # Group toolbars by position
        top_html_parts = []
        bottom_html_parts = []
        left_html_parts = []
        right_html_parts = []
        inside_html_parts = []

        for toolbar in toolbars:
            position = toolbar.get("position", "top")
            items = toolbar.get("items", [])
            if not items:
                continue
            toolbar_html = build_toolbar_html(items, mode, position)
            if position == "top":
                top_html_parts.append(toolbar_html)
            elif position == "bottom":
                bottom_html_parts.append(toolbar_html)
            elif position == "left":
                left_html_parts.append(toolbar_html)
            elif position == "right":
                right_html_parts.append(toolbar_html)
            elif position == "inside":
                inside_html_parts.append(toolbar_html)

        # Wrap content with toolbars
        if inside_html_parts:
            content = (
                f"<div class='pywry-wrapper-inside'>{''.join(inside_html_parts)}{content}</div>"
            )
        if left_html_parts or right_html_parts:
            left_html = "".join(left_html_parts)
            right_html = "".join(right_html_parts)
            content = f"<div class='pywry-wrapper-left'>{left_html}<div class='pywry-content'>{content}</div>{right_html}</div>"
        if top_html_parts or bottom_html_parts:
            top_html = "".join(top_html_parts)
            bottom_html = "".join(bottom_html_parts)
            content = f"<div class='pywry-wrapper-top'>{top_html}<div class='pywry-content'>{content}</div>{bottom_html}</div>"

    # Build head with optional libraries
    pywry_css = get_pywry_css()
    head_parts = [
        '<meta charset="utf-8">',
        f"<title>{title}</title>",
        f"<style>{pywry_css}</style>" if pywry_css else "",
        """<style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: var(--pywry-bg-primary);
                color: var(--pywry-text-primary);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 16px;
            }
        </style>""",
    ]

    if include_plotly:
        plotly_js = get_plotly_js()
        if plotly_js:
            head_parts.append(f"<script>{plotly_js}</script>")
        else:
            head_parts.append('<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>')

    if include_aggrid:
        aggrid_js = get_aggrid_js()
        aggrid_css = get_aggrid_css(
            aggrid_theme, ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
        )
        if aggrid_js:
            head_parts.append(f"<script>{aggrid_js}</script>")
        if aggrid_css:
            head_parts.append(f"<style>{aggrid_css}</style>")

    # Build full HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    {"".join(head_parts)}
</head>
<body>
    {content}
    {_get_pywry_bridge_js(widget_id)}
</body>
</html>"""

    widget = InlineWidget(
        html, callbacks=callbacks, width=width, height=height, port=port, widget_id=widget_id
    )

    widget.display()
    return widget


def generate_plotly_html(
    figure_json: str,
    widget_id: str,
    title: str = "PyWry",
    theme: Literal["dark", "light"] = "dark",
    full_document: bool = True,
    toolbars: list[dict[str, Any]] | None = None,
) -> str:
    """Generate HTML for a Plotly figure from JSON.

    This is the pure HTML generation function - no display, no IPython required,
    no Plotly import required. Used internally by show_plotly() and for testing.

    Parameters
    ----------
    figure_json : str
        Plotly figure as JSON string (from figure.to_json()).
        Should include 'config' key if custom config is needed.
    widget_id : str
        Widget ID for the pywry bridge.
    title : str
        Page title.
    theme : 'dark' or 'light'
        Color theme.
    full_document : bool
        If True, return complete HTML document with <!DOCTYPE>, <html>, etc.
        If False, return only content fragment (for anywidget).
    toolbars : list[dict], optional
        List of toolbar configurations, each with:
        - position: "top", "bottom", "left", "right", "inside"
        - items: list of item configs

    Returns
    -------
    str
        Complete HTML document or content fragment.
    """
    plotly_js = get_plotly_js()
    plotly_script = (
        f"<script>{plotly_js}</script>"
        if plotly_js
        else '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
    )

    # Include Plotly templates (plotly_dark, plotly_white, etc.) for theme switching
    templates_js = get_plotly_templates_js()
    templates_script = f"<script>{templates_js}</script>" if templates_js else ""

    # Generate toolbar HTML from toolbars config
    toolbar_html = ""
    mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
    if toolbars:
        for toolbar in toolbars:
            position = toolbar.get("position", "top")
            items = toolbar.get("items", [])
            if items:
                toolbar_html += build_toolbar_html(items, mode, position)

    # Plotly event handlers script
    # Use window.Plotly for anywidget compatibility (ESM scope)
    plotly_handlers_script = f"""<script>
    (function() {{
        // Debug: Check Plotly availability
        console.log('[PyWry] Checking Plotly availability...');
        console.log('[PyWry] window.Plotly:', typeof window.Plotly);
        console.log('[PyWry] typeof Plotly:', typeof Plotly !== 'undefined' ? typeof Plotly : 'undefined');

        // Wait for Plotly to be available in window
        function waitForPlotly(callback, maxAttempts = 50) {{
            let attempts = 0;
            function check() {{
                if (typeof window.Plotly !== 'undefined') {{
                    console.log('[PyWry] Plotly found after', attempts, 'attempts');
                    callback(window.Plotly);
                }} else if (attempts < maxAttempts) {{
                    attempts++;
                    setTimeout(check, 100);
                }} else {{
                    console.error('[PyWry] Plotly not available after', maxAttempts, 'attempts');
                    const chartEl = document.getElementById('chart');
                    if (chartEl) {{
                        chartEl.innerHTML = '<div style="background:#ff4444;color:white;padding:20px;border-radius:8px;text-align:center;">' +
                            '<h3>ERROR: Plotly.js not loaded</h3>' +
                            '<p>window.Plotly is undefined</p>' +
                            '<p>This is an ES6 module scope isolation issue</p>' +
                            '</div>';
                    }}
                }}
            }}
            check();
        }}

        const figData = {figure_json};
        const plotlyConfig = figData.config || {{}};

        // Convert string functions to actual functions in modeBarButtonsToAdd
        if (plotlyConfig.modeBarButtonsToAdd) {{
            plotlyConfig.modeBarButtonsToAdd = plotlyConfig.modeBarButtonsToAdd.map(function(btn) {{
                if (btn.click && typeof btn.click === 'string') {{
                    try {{
                        // Convert string function to actual function
                        btn.click = eval('(' + btn.click + ')');
                    }} catch(e) {{
                        console.error('[PyWry] Failed to parse button click function:', e);
                    }}
                }}
                return btn;
            }});
        }}

        const finalConfig = Object.assign({{responsive: true}}, plotlyConfig);

        waitForPlotly(function(PlotlyLib) {{
            // Register handler for figure updates - cleaner than full re-render
            window.pywry.on('pywry:update_plotly', function(data) {{
                const chartEl = document.getElementById('chart');
                if (chartEl && data.figure) {{
                    const figData = data.figure;
                    const config = data.config || {{}};
                    // Process modebar button click handlers
                    if (config.modeBarButtonsToAdd) {{
                        config.modeBarButtonsToAdd = config.modeBarButtonsToAdd.map(function(btn) {{
                            if (typeof btn.click === 'string') {{
                                try {{
                                    btn.click = eval('(' + btn.click + ')');
                                }} catch(e) {{}}
                            }}
                            return btn;
                        }});
                    }}
                    PlotlyLib.react(chartEl, figData.data, figData.layout, config);
                }}
            }});

            PlotlyLib.newPlot('chart', figData.data, figData.layout, finalConfig).then(function() {{
        const chartEl = document.getElementById('chart');

        chartEl.on('plotly_click', function(data) {{
            const points = data.points.map(p => ({{
                curveNumber: p.curveNumber,
                pointNumber: p.pointNumber,
                pointIndex: p.pointIndex,
                x: p.x,
                y: p.y,
                text: p.text,
                customdata: p.customdata
            }}));
            window.pywry.emit('plotly_click', {{ points: points }});
        }});

        chartEl.on('plotly_hover', function(data) {{
            const points = data.points.map(p => ({{
                curveNumber: p.curveNumber,
                pointNumber: p.pointNumber,
                x: p.x,
                y: p.y
            }}));
            window.pywry.emit('plotly_hover', {{ points: points }});
        }});

        chartEl.on('plotly_selected', function(data) {{
            if (data) {{
                const points = data.points.map(p => ({{
                    curveNumber: p.curveNumber,
                    pointNumber: p.pointNumber,
                    x: p.x,
                    y: p.y
                }}));
                window.pywry.emit('plotly_selected', {{ points: points, range: data.range }});
            }}
        }});
    }});
        }});
    }})();
</script>"""

    pywry_css = get_pywry_css()
    pywry_style = f"<style>{pywry_css}</style>" if pywry_css else ""

    widget_theme_class = "pywry-theme-dark" if theme == "dark" else "pywry-theme-light"

    # For anywidget: content fragment WITHOUT pywry bridge (widget provides it)
    # For IFrame: full document WITH pywry bridge
    if not full_document:
        # Content fragment for anywidget - NO bridge, widget already has window.pywry
        # Return simpler structure without hardcoded wrapper to allow flexible layout composition
        return f"""<div id="chart" class="pywry-content" style="height: 100%; width: 100%;"></div>
{plotly_handlers_script}"""

    # Build wrapper structure for toolbars
    chart_div = '<div id="chart"></div>'
    widget_content = chart_div
    if toolbar_html:
        # Simple layout: toolbar on top, chart below
        widget_content = f"<div class='pywry-wrapper-top'>{toolbar_html}<div class='pywry-content'>{chart_div}</div></div>"

    # Full document for IFrame - INCLUDE bridge
    # Structure matches AG Grid IFrame for visual consistency
    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {plotly_script}
    {templates_script}
    {pywry_style}
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            /* Match toolbar background for seamless look */
            background: var(--pywry-bg-primary);
        }}
        .pywry-widget {{
            --pywry-widget-width: 100%;
            --pywry-widget-height: 100%;
            border: none;
            border-radius: 0;
            /* Match toolbar background */
            background-color: var(--pywry-bg-primary);
        }}
        /* Remove toolbar borders in IFrame context */
        .pywry-toolbar {{
            border: none;
        }}
        #chart {{
            height: 100%;
            width: 100%;
        }}
        .pywry-wrapper-top {{
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
        }}
        .pywry-wrapper-bottom {{
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
        }}
        .pywry-content {{
            flex: 1;
            min-height: 0;
        }}
    </style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id)}
    {plotly_handlers_script}
    <script>
        // Listen for theme updates (background/container AND Plotly figure)
        window.pywry.on('pywry:update_theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;

            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}

            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            // Read background from CSS variable (set by theme class)
            const bgColor = getComputedStyle(widgetEl || document.documentElement).getPropertyValue('--pywry-bg-primary').trim();
            bodyEl.style.background = bgColor || '';

            // Update Plotly figure template using PYWRY_PLOTLY_TEMPLATES
            const plotDiv = document.querySelector('.js-plotly-plot');
            if (plotDiv && window.Plotly && plotDiv.data) {{
                const templateName = isLight ? 'plotly_white' : 'plotly_dark';
                const template = window.PYWRY_PLOTLY_TEMPLATES?.[templateName];
                if (template) {{
                    // Use newPlot to fully re-render with new template
                    const newLayout = Object.assign({{}}, plotDiv.layout || {{}}, {{ template: template }});
                    window.Plotly.newPlot(plotDiv, plotDiv.data, newLayout, plotDiv._fullLayout?._config || {{}});
                }}
            }}

            console.log('[PyWry Plotly IFrame] Theme updated, isLight:', isLight);
        }});
    </script>
</body>
</html>"""


def show_plotly(
    figure: Figure,
    callbacks: dict[str, Callable[..., Any]] | None = None,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: Literal["dark", "light"] = "dark",
    port: int | None = None,
    config: dict[str, Any] | None = None,
    toolbars: list[dict[str, Any]] | None = None,
) -> BaseWidget:
    """Show a Plotly figure inline in a notebook with automatic event handling.

    This function automatically wires up Plotly events (click, hover, selected)
    and uses the best available widget backend (anywidget or InlineWidget).

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        Plotly figure to display.
    callbacks : dict[str, Callable], optional
        Event callbacks. Keys are event names (e.g., 'plotly_click', 'plotly_hover',
        'plotly_selected'), values are handler functions receiving (data, event_type, label).
        The function signature should be: callback(data: dict, event_type: str, label: str).
    title : str
        Page title.
    width : str
        Widget width (CSS format).
    height : int
        Widget height in pixels.
    theme : 'dark' or 'light'
        Color theme.
    port : int, optional
        Server port (only used if InlineWidget fallback is needed).
    config : dict, optional
        Plotly config dictionary (e.g., {'modeBarButtonsToAdd': [...]}).
    toolbars : list[dict], optional
        List of toolbar configurations, each with:
        - position: "top", "bottom", "left", "right", "inside"
        - items: list of item configs

    Returns
    -------
    BaseWidget
        Widget implementing BaseWidget protocol (PyWryPlotlyWidget or InlineWidget).

    Examples
    --------
    >>> import plotly.graph_objects as go
    >>> fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
    >>> widget = show_plotly(
    ...     fig,
    ...     callbacks={
    ...         "plotly_click": lambda d, t, l: print(f"Clicked: {d['points']}"),
    ...         "plotly_hover": lambda d, t, l: print(f"Hover: {d['points']}"),
    ...     },
    ... )
    """
    from .notebook import create_plotly_widget

    widget_id = uuid.uuid4().hex

    # Convert figure to dict and merge config
    fig_dict = json.loads(figure.to_json())
    if config:
        fig_dict["config"] = config
    fig_json = json.dumps(fig_dict)

    # Create widget using auto-backend selection
    widget = create_plotly_widget(
        figure_json=fig_json,
        widget_id=widget_id,
        title=title,
        theme=theme,
        width=width,
        height=height,
        port=port,
        toolbars=toolbars,
    )

    # Store config and toolbars for updates
    widget._plotly_config = config  # pylint: disable=attribute-defined-outside-init
    widget._toolbars = toolbars  # pylint: disable=attribute-defined-outside-init

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display automatically
    widget.display()
    return widget


_AGGRID_IFRAME_CSS = """
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: var(--pywry-bg-primary);
}
.pywry-widget {
    --pywry-widget-width: 100%;
    --pywry-widget-height: 100%;
    border: none;
    border-radius: 0;
    background-color: var(--pywry-bg-primary);
}
.pywry-toolbar {
    border: none;
}
.pywry-grid {
    height: 100%;
    width: 100%;
}
"""


def _load_all_aggrid_theme_css() -> str:
    css_parts = []
    for theme_name in ["alpine", "quartz", "balham", "material"]:
        for mode in [ThemeMode.DARK, ThemeMode.LIGHT]:
            theme_css = get_aggrid_css(theme_name, mode)
            if theme_css:
                css_parts.append(theme_css)
    return "\n".join(css_parts)


def _build_aggrid_assets(aggrid_theme: str, theme_mode: ThemeMode) -> dict[str, str]:
    aggrid_js = get_aggrid_js()
    aggrid_defaults_js = get_aggrid_defaults_js()
    all_css = _load_all_aggrid_theme_css()
    aggrid_css = all_css if all_css else get_aggrid_css(aggrid_theme, theme_mode)
    pywry_css = get_pywry_css()

    return {
        "script": (
            f"<script>{aggrid_js}</script>"
            if aggrid_js
            else '<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@35.0.0/dist/ag-grid-community.min.js"></script>'
        ),
        "defaults_script": f"<script>{aggrid_defaults_js}</script>" if aggrid_defaults_js else "",
        "style": f"<style>{aggrid_css}</style>" if aggrid_css else "",
        "pywry_style": f"<style>{pywry_css}</style>" if pywry_css else "",
    }


def _build_grid_layout(toolbars_html: dict[str, str], header_html: str, theme_class: str) -> str:
    """Build grid layout with multiple toolbars.

    Parameters
    ----------
    toolbars_html : dict[str, str]
        Dict mapping position ('top', 'bottom', etc.) to toolbar HTML.
    header_html : str
        Custom header HTML (inserted at top).
    theme_class : str
        AG Grid theme class.

    Returns
    -------
    str
        The complete layout HTML.
    """
    grid_div = f"<div id='grid' class='pywry-grid {theme_class}'></div>"

    # Simple layout: top toolbar + header, then grid, then bottom toolbar
    top_content = header_html + toolbars_html.get("top", "")
    bottom_content = toolbars_html.get("bottom", "")

    if top_content and bottom_content:
        # Both top and bottom
        return f"""<div class='pywry-wrapper-top'>
            {top_content}
            <div class='pywry-content'>{grid_div}</div>
            {bottom_content}
        </div>"""
    if top_content:
        return f"<div class='pywry-wrapper-top'>{top_content}<div class='pywry-content'>{grid_div}</div></div>"
    if bottom_content:
        return f"<div class='pywry-wrapper-bottom'><div class='pywry-content'>{grid_div}</div>{bottom_content}</div>"
    return f"<div class='pywry-content'>{grid_div}</div>"


def generate_dataframe_html(
    row_data: list[dict[str, Any]],
    columns: list[str],
    widget_id: str,
    title: str = "PyWry",
    theme: Literal["dark", "light"] = "dark",
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    grid_options: dict[str, Any] | None = None,
    toolbars: list[dict[str, Any]] | None = None,
) -> str:
    """Generate HTML for AG Grid widget.

    This is the pure HTML generation function - no display, no IPython required,
    no pandas import required. Used internally by show_dataframe() and for testing.

    Parameters
    ----------
    row_data : list[dict]
        List of row dictionaries (from df.to_dict(orient="records")).
    columns : list[str]
        List of column names.
    widget_id : str
        Widget ID for the pywry bridge.
    title : str
        Page title.
    theme : 'dark' or 'light'
        Color theme.
    aggrid_theme : str
        AG Grid theme name.
    header_html : str, optional
        Custom HTML to insert above the grid (e.g., buttons).
    grid_options : dict, optional
        Custom AG Grid options to merge with defaults.
    toolbars : list[dict], optional
        List of toolbar configs. Each toolbar has 'position' and 'items' keys.

    Returns
    -------
    str
        Complete HTML document.
    """
    theme_mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT

    # Build toolbar HTML for each position
    toolbars_html: dict[str, str] = {}
    if toolbars:
        for toolbar in toolbars:
            position = toolbar.get("position", "top")
            items = toolbar.get("items", [])
            if items:
                html = build_toolbar_html(items, theme_mode, position)
                toolbars_html[position] = toolbars_html.get(position, "") + html

    grid_config: dict[str, Any] = {
        "columnDefs": [{"field": col} for col in columns],
        "rowData": row_data,
        "domLayout": "normal",
    }
    if grid_options:
        grid_config.update(grid_options)
        if "rowData" not in grid_config:
            grid_config["rowData"] = row_data

    assets = _build_aggrid_assets(aggrid_theme, theme_mode)
    theme_class = f"ag-theme-{aggrid_theme}{'-dark' if theme == 'dark' else ''}"
    widget_theme_class = f"pywry-theme-{theme}"
    widget_content = _build_grid_layout(toolbars_html, header_html, theme_class)

    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {assets["script"]}
    {assets["defaults_script"]}
    {assets["style"]}
    {assets["pywry_style"]}
    <style>{_AGGRID_IFRAME_CSS}</style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id)}
    <script>
        const gridId = '{widget_id}';
        const gridConfig = {json.dumps(grid_config)};
        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId);
        const gridDiv = document.getElementById('grid');
        const gridApi = agGrid.createGrid(gridDiv, gridOptions);

        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
        }}

        window.pywry.on('pywry:update_theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;
            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}
            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            const bgColor = getComputedStyle(widgetEl || document.documentElement).getPropertyValue('--pywry-bg-primary').trim();
            bodyEl.style.background = bgColor || '';

            if (gridDiv && data.theme && data.theme.startsWith('ag-theme-')) {{
                const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                gridDiv.className = classes.join(' ') + ' ' + data.theme;
            }}
            console.log('[PyWry IFrame] Theme updated to:', data.theme, 'isLight:', isLight);
        }});
    </script>
</body>
</html>"""


def generate_dataframe_html_from_config(
    config: GridConfig,
    widget_id: str,
    title: str = "PyWry",
    theme: Literal["dark", "light"] = "dark",
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    toolbars: list[dict[str, Any]] | None = None,
) -> str:
    """Generate HTML for AG Grid widget from GridConfig.

    This version accepts a GridConfig from the unified grid module
    instead of raw row_data/columns. Supports both client-side and
    server-side modes.

    Parameters
    ----------
    config : GridConfig
        Grid configuration from grid.build_grid_config().
    widget_id : str
        Widget ID for the pywry bridge.
    title : str
        Page title.
    theme : 'dark' or 'light'
        Color theme.
    aggrid_theme : str
        AG Grid theme name.
    header_html : str, optional
        Custom HTML to insert above the grid.
    toolbars : list[dict], optional
        List of toolbar configs. Each toolbar has 'position' and 'items' keys.

    Returns
    -------
    str
        Complete HTML document.
    """
    theme_mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT

    # Build toolbar HTML for each position
    toolbars_html: dict[str, str] = {}
    if toolbars:
        for toolbar in toolbars:
            position = toolbar.get("position", "top")
            items = toolbar.get("items", [])
            if items:
                html = build_toolbar_html(items, theme_mode, position)
                toolbars_html[position] = toolbars_html.get(position, "") + html

    # Get grid config dict from GridConfig.options (Pydantic model)
    grid_config = config.options.to_dict()

    # Add PyWry metadata for IPC if needed
    if config.options.row_model_type != "clientSide":
        grid_config["_pywry"] = {
            "gridId": config.context.grid_id,
            "totalRows": config.context.total_rows,
            "blockSize": config.options.cache_block_size,
        }

    assets = _build_aggrid_assets(aggrid_theme, theme_mode)
    theme_class = config.context.theme_class
    widget_theme_class = f"pywry-theme-{theme}"
    widget_content = _build_grid_layout(toolbars_html, header_html, theme_class)

    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {assets["script"]}
    {assets["defaults_script"]}
    {assets["style"]}
    {assets["pywry_style"]}
    <style>{_AGGRID_IFRAME_CSS}</style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id)}
    <script>
        const gridId = '{widget_id}';
        const gridConfig = {json.dumps(grid_config)};
        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId);
        const gridDiv = document.getElementById('grid');
        const gridApi = agGrid.createGrid(gridDiv, gridOptions);

        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
        }}

        window.pywry.on('pywry:update_theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;
            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}
            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            const bgColor = getComputedStyle(widgetEl || document.documentElement).getPropertyValue('--pywry-bg-primary').trim();
            bodyEl.style.background = bgColor || '';

            if (gridDiv && data.theme && data.theme.startsWith('ag-theme-')) {{
                const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                gridDiv.className = classes.join(' ') + ' ' + data.theme;
            }}
            console.log('[PyWry IFrame] Theme updated to:', data.theme, 'isLight:', isLight);
        }});
    </script>
</body>
</html>"""


def show_dataframe(  # pylint: disable=too-many-arguments
    df: Any,
    callbacks: dict[str, Callable[..., Any]] | None = None,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: Literal["dark", "light"] = "dark",
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    grid_options: dict[str, Any] | None = None,
    toolbars: list[Any] | None = None,
    port: int | None = None,
    widget_id: str | None = None,
    column_defs: list[Any] | None = None,
    row_selection: Any | bool = True,
    enable_cell_span: bool | None = None,
    pagination: bool | None = None,
    pagination_page_size: int = 100,
) -> BaseWidget:
    """Show a DataFrame (or dict/list) inline in a notebook with automatic event handling.

    This function automatically wires up AG Grid events (cell_click, row_selected)
    and uses the best available widget backend (anywidget or InlineWidget).

    Parameters
    ----------
    df : DataFrame | list[dict] | dict[str, list]
        Data to display. Can be pandas DataFrame, list of row dicts, or dict of columns.
    callbacks : dict[str, Callable], optional
        Event callbacks.
    title : str
        Page title.
    width : str
        Widget width (CSS format).
    height : int
        Widget height in pixels.
    theme : 'dark' or 'light'
        Color theme.
    aggrid_theme : str
        AG Grid theme.
    header_html : str, optional
        Custom HTML to display above the grid (e.g., buttons).
    grid_options : dict, optional
        Custom AG Grid options.
    toolbars : list[Toolbar | dict], optional
        List of toolbars. Each can be a Toolbar model or dict with:
        - position: "top", "bottom", "left", "right", "inside"
        - items: list of item configs (Button, Select, etc.)
    port : int, optional
        Server port (only used if InlineWidget fallback is needed).
    column_defs : list, optional
        Custom column definitions. Can be dicts or ColDef objects.
    row_selection : RowSelection | dict | bool
        Row selection config. True = multiRow with checkboxes.
    enable_cell_span : bool | None
        Enable row spanning for index columns. None = auto-detect from MultiIndex.
    pagination : bool | None
        Enable pagination. None = auto-enable for datasets > 10 rows.
    pagination_page_size : int
        Rows per page when pagination is enabled.

    Returns
    -------
    BaseWidget
        Widget implementing BaseWidget protocol.
    """
    from .grid import build_grid_config
    from .notebook import create_dataframe_widget

    # Use unified grid config builder
    config = build_grid_config(
        data=df,
        column_defs=column_defs,
        grid_options=grid_options,
        theme=theme,
        aggrid_theme=aggrid_theme,
        grid_id=widget_id,
        row_selection=row_selection,
        enable_cell_span=enable_cell_span,
        pagination=pagination,
        pagination_page_size=pagination_page_size,
    )

    # Use provided widget_id or the one from config
    wid = widget_id or config.context.grid_id

    # Create widget using auto-backend selection
    widget = create_dataframe_widget(
        config=config,
        widget_id=wid,
        title=title,
        theme=theme,
        aggrid_theme=aggrid_theme,
        width=width,
        height=height,
        header_html=header_html,
        toolbars=toolbars,
        port=port,
    )

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display automatically
    widget.display()
    return widget
