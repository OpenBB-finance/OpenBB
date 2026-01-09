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

    from plotly.graph_objects import Figure

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
        self.event_queues: dict[str, queue.Queue[Any]] = {}
        self.connections: dict[str, list[WebSocket]] = {}
        self.callback_queue: queue.Queue[Any] = queue.Queue()
        self.shutdown_event: asyncio.Event | None = None


_state = _ServerState()


def _get_pywry_bridge_js(widget_id: str) -> str:
    """Generate the pywry JavaScript bridge with bidirectional communication.

    Supports:
    - JS → Python via HTTP POST to /emit/{widget_id}
    - Python → JS via polling /poll/{widget_id} endpoint
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
    let pollInterval = null;

    window.pywry = {{
        _ready: false,
        _handlers: {{}},
        _pending: [],
        _widgetId: widgetId,

        result: function(data) {{
            this.emit('pywry:result', data);
        }},

        // Send event to Python
        emit: function(type, data) {{
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] emit() called with type:', type, 'data:', data);
            }}
            const msg = {{ type: type, data: data, widgetId: widgetId, ts: Date.now() }};
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Sending POST to:', apiUrl + '/emit/' + widgetId);
                console.log('[PyWry] Message body:', msg);
            }}

            fetch(apiUrl + '/emit/' + widgetId, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(msg),
                mode: 'cors'
            }})
            .then(response => {{
                if ({str(PYWRY_DEBUG).lower()}) {{
                    console.log('[PyWry] Emit response status:', response.status);
                }}
                return response.json();
            }})
            .then(data => {{
                if ({str(PYWRY_DEBUG).lower()}) {{
                    console.log('[PyWry] Emit response data:', data);
                }}
            }})
            .catch(err => {{
                console.error('[PyWry] Emit error:', err);
            }});
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

    // Start polling for events from Python
    function pollEvents() {{
        fetch(apiUrl + '/poll/' + widgetId, {{
            method: 'GET',
            mode: 'cors'
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.events && Array.isArray(data.events)) {{
                if (data.events.length > 0) {{
                     if ({str(PYWRY_DEBUG).lower()}) {{
                        console.log('[PyWry] Polled events:', data.events);
                     }}
                }}
                data.events.forEach(event => {{
                     if ({str(PYWRY_DEBUG).lower()}) {{
                        console.log('[PyWry] Firing event:', event.type, event.data);
                     }}
                    window.pywry._fire(event.type, event.data);
                }});
            }}
        }})
        .catch(err => {{
            // Poll errors are silent - network issues are normal
        }});
    }}

    // Poll every 100ms for events from Python
    pollInterval = setInterval(pollEvents, 100);
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
    """Lifespan context manager for graceful shutdown."""
    # Startup: create shutdown event
    _state.shutdown_event = asyncio.Event()
    yield
    # Shutdown: nothing special needed, event loop will stop


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
        await websocket.accept()

        if widget_id not in _state.connections:
            _state.connections[widget_id] = []
        _state.connections[widget_id].append(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)

                # Put callback in queue for processing
                if widget_id in _state.widgets:
                    callbacks = _state.widgets[widget_id].get("callbacks", {})
                    event_type = msg.get("type", "")
                    if event_type in callbacks:
                        _state.callback_queue.put(
                            (callbacks[event_type], msg.get("data", {}), widget_id)
                        )
        except WebSocketDisconnect:
            if widget_id in _state.connections:
                _state.connections[widget_id].remove(websocket)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/poll/{widget_id}")
    async def poll_events(widget_id: str) -> dict[str, list[Any]]:
        """Poll endpoint for Python→JS events (bidirectional communication)."""
        if widget_id not in _state.event_queues:
            return {"events": []}

        events = []
        event_q = _state.event_queues[widget_id]
        try:
            # Collect all pending events (non-blocking)
            while True:
                event = event_q.get_nowait()
                events.append(event)
        except queue.Empty:
            pass

        return {"events": events}

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
            _state.event_queues[widget_id] = queue.Queue()

            return {"status": "registered", "widget_id": widget_id}  # noqa: TRY300
        except Exception as e:
            return {"error": str(e)}

    @app.post("/emit/{widget_id}")
    async def emit_event(widget_id: str, request: Request) -> dict[str, Any]:
        """HTTP POST endpoint for JavaScript callbacks."""
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}

        if widget_id not in _state.widgets:
            return {"error": "Widget not found"}

        callbacks = _state.widgets[widget_id].get("callbacks", {})
        event_type = body.get("type", "")

        if event_type in callbacks:
            _state.callback_queue.put(
                (callbacks[event_type], body.get("data", {}), event_type, widget_id)
            )
            return {"status": "ok", "queued": True}

        return {"status": "ok", "queued": False, "reason": f"No callback for {event_type}"}

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

        # Reuse existing event queue if widget_id already exists, otherwise create new one
        if self._widget_id in _state.event_queues:
            self._event_queue = _state.event_queues[self._widget_id]
        else:
            self._event_queue = queue.Queue()
            _state.event_queues[self._widget_id] = self._event_queue

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
        self._event_queue.put(event)

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
        url = self._build_iframe_url()
        return f'<iframe src="{url}" width="{self._width}" height="{self._height}" style="border:none;border-radius:8px;"></iframe>'

    def _repr_mimebundle_(self, **kwargs: Any) -> dict[str, str]:  # pylint: disable=unused-argument
        """Return mimebundle for rich display with Output widget."""
        from IPython.display import display as ipy_display

        # Display Output widget for callbacks
        ipy_display(self._output)

        # Return HTML mimebundle for IFrame
        url = self._build_iframe_url()
        iframe_html = f'<iframe src="{url}" width="{self._width}" height="{self._height}" style="border:none;border-radius:8px;"></iframe>'
        return {"text/html": iframe_html}

    def _build_iframe_url(self) -> str:
        """Build the IFrame URL for the widget with cache-busting parameter."""
        import time  # pylint: disable=redefined-outer-name,reimported

        settings = get_settings().server
        protocol = "https" if settings.ssl_certfile else "http"
        host = _state.host or settings.host
        port = _state.port or settings.port
        # Add timestamp to prevent browser caching when cell is re-run
        timestamp = int(time.time() * 1000)
        return f"{protocol}://{host}:{port}/widget/{self._widget_id}?_t={timestamp}"

    def display(self) -> None:
        """Display the widget in the current output context.

        For Jupyter notebooks, displays the IFrame and output widget for callback messages.
        """
        from IPython.display import IFrame, display as ipy_display

        url = self._build_iframe_url()

        # Display IFrame first, then Output widget below it for callback output
        ipy_display(IFrame(src=url, width=self._width, height=self._height))
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

        # Send update via Plotly.react (no page reload needed)
        self.emit("pywry:update_plotly", {"figure": fig_dict, "config": stored_config or {}})

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

        Examples
        --------
        >>> widget.update_grid(new_df, new_columns)
        >>> widget.update_grid(new_df, new_columns, preserve_state=False)  # Reset state
        """
        payload: dict[str, Any] = {"preserveState": preserve_state}
        if data is not None:
            payload["rows"] = self._normalize_data(data)
        if columns is not None:
            payload["columnDefs"] = columns
        if payload:
            self.emit("pywry:update_grid", payload)

    def save_state(self) -> None:
        """Request the grid to save its current state.

        The grid will emit a 'grid_state_saved' event with the state data.
        Register a callback for 'grid_state_saved' to receive the state.
        """
        self.emit("pywry:save_state", {})

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


def show(  # noqa: C901, PLR0912  # pylint: disable=too-many-arguments,too-many-branches
    content: str,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: Literal["dark", "light"] = "dark",
    callbacks: dict[str, Callable[..., Any]] | None = None,
    include_plotly: bool = False,
    include_aggrid: bool = False,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    buttons: list[dict[str, str]] | None = None,
    toolbar_position: str = "top",
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
    buttons : list[dict], optional
        List of button configs to generate a toolbar.
        Each dict should have: {'label': str, 'event': str, 'style': str (optional)}.
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
    bg_color = "#1e1e1e" if theme == "dark" else "#ffffff"
    text_color = "#ffffff" if theme == "dark" else "#000000"

    # Generate toolbar HTML from buttons if provided
    toolbar_html = ""
    if buttons:
        mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
        toolbar_html = build_toolbar_html(buttons, mode, toolbar_position)

    if toolbar_html:
        if toolbar_position == "bottom":
            content = f'<div class="pywry-wrapper-bottom"><div class="pywry-content">{content}</div>{toolbar_html}</div>'
        elif toolbar_position == "top":
            content = f'<div class="pywry-wrapper-top">{toolbar_html}<div class="pywry-content">{content}</div></div>'
        elif toolbar_position == "left":
            content = f'<div class="pywry-wrapper-left">{toolbar_html}<div class="pywry-content">{content}</div></div>'
        elif toolbar_position == "right":
            content = f'<div class="pywry-wrapper-right"><div class="pywry-content">{content}</div>{toolbar_html}</div>'
        elif toolbar_position == "inside":
            content = f'<div class="pywry-wrapper-inside">{toolbar_html}{content}</div>'

    # Build head with optional libraries
    pywry_css = get_pywry_css()
    head_parts = [
        '<meta charset="utf-8">',
        f"<title>{title}</title>",
        f"<style>{pywry_css}</style>" if pywry_css else "",
        f"""<style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: {bg_color};
                color: {text_color};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 16px;
            }}
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
    buttons: list[dict[str, str]] | None = None,
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
    buttons : list[dict], optional
        List of button configs to generate a toolbar.

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

    # Generate toolbar HTML from buttons if provided
    toolbar_html = ""
    if buttons:
        # Internal generation defaults to top position
        toolbar_html = build_toolbar_html(
            buttons, ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT, "top"
        )

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

    # For anywidget: content fragment WITHOUT pywry bridge (widget provides it)
    # For IFrame: full document WITH pywry bridge
    if not full_document:
        # Content fragment for anywidget - NO bridge, widget already has window.pywry
        return f"""<div class="pywry-wrapper-top">
        {toolbar_html}
        <div id="chart" class="pywry-content"></div>
        </div>
{plotly_handlers_script}"""

    # Full document for IFrame - INCLUDE bridge
    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {plotly_script}
    {pywry_style}
    <style>
        body {{ display: flex; flex-direction: column; height: 100vh; width: 100vw; margin: 0; }}
        #chart {{ flex-grow: 1; min-height: 0; }}
    </style>
</head>
<body>
    {toolbar_html}
    <div id="chart"></div>
    {_get_pywry_bridge_js(widget_id)}
    {plotly_handlers_script}
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
    buttons: list[dict[str, str]] | None = None,
    toolbar_position: str = "top",
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
    buttons : list[dict], optional
        List of button configs to generate a toolbar.

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
        buttons=buttons,
        toolbar_position=toolbar_position,
    )

    # Store config for updates
    widget._plotly_config = config  # pylint: disable=attribute-defined-outside-init

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display automatically
    widget.display()
    return widget


def generate_dataframe_html(
    row_data: list[dict[str, Any]],
    columns: list[str],
    widget_id: str,
    title: str = "PyWry",
    theme: Literal["dark", "light"] = "dark",
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    grid_options: dict[str, Any] | None = None,
    buttons: list[dict[str, str]] | None = None,
) -> str:
    """Generate HTML for tabular data using AG Grid.

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
    buttons : list[dict], optional
        List of button configs to generate a toolbar.
        Each dict should have: {'label': str, 'event': str, 'style': str (optional)}.

    Returns
    -------
    str
        Complete HTML document.
    """
    theme_mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT

    # Generate toolbar HTML from buttons if provided
    if buttons:
        toolbar = build_toolbar_html(buttons, theme_mode, "top")
        # Append to existing header_html or use as header
        header_html = header_html + toolbar if header_html else toolbar

    # Grid config - just the data, defaults come from aggrid-defaults.js
    grid_config = {
        "columnDefs": [{"field": col} for col in columns],
        "rowData": row_data,
    }

    # Merge/Override with provided options
    if grid_options:
        grid_config.update(grid_options)
        # Ensure rowData is set if not provided in grid_options
        if "rowData" not in grid_config:
            grid_config["rowData"] = row_data

    aggrid_js = get_aggrid_js()
    aggrid_defaults_js = get_aggrid_defaults_js()

    # Load CSS for ALL themes so JavaScript can switch between them
    all_themes_css = []
    for theme_name in ["alpine", "quartz", "balham", "material"]:
        for mode in [ThemeMode.DARK, ThemeMode.LIGHT]:
            theme_css = get_aggrid_css(theme_name, mode)
            if theme_css:
                all_themes_css.append(theme_css)

    aggrid_css = (
        "\n".join(all_themes_css) if all_themes_css else get_aggrid_css(aggrid_theme, theme_mode)
    )

    aggrid_script = (
        f"<script>{aggrid_js}</script>"
        if aggrid_js
        else '<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@35.0.0/dist/ag-grid-community.min.js"></script>'
    )
    aggrid_style = f"<style>{aggrid_css}</style>" if aggrid_css else ""
    aggrid_defaults_script = f"<script>{aggrid_defaults_js}</script>" if aggrid_defaults_js else ""

    theme_class = f"ag-theme-{aggrid_theme}-{'dark' if theme == 'dark' else 'light'}"

    pywry_css = get_pywry_css()
    pywry_style = f"<style>{pywry_css}</style>" if pywry_css else ""

    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {aggrid_script}
    {aggrid_defaults_script}
    {aggrid_style}
    {pywry_style}
    <style>
        body {{ display: flex; flex-direction: column; height: 100vh; width: 100vw; margin: 0; }}
        #grid {{ flex: 1; min-height: 0; width: 100%; }}
    </style>
</head>
<body>
    {header_html}
    <div id="grid" class="{theme_class}"></div>
    {_get_pywry_bridge_js(widget_id)}
    <script>
        // Build grid options using centralized defaults (scoped by widget_id)
        const gridId = '{widget_id}';
        const gridConfig = {json.dumps(grid_config)};
        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId);

        const gridDiv = document.getElementById('grid');
        const gridApi = agGrid.createGrid(gridDiv, gridOptions);

        // Register Python event listeners + context menu using centralized function (scoped by gridId)
        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
        }}
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
    buttons: list[dict[str, str]] | None = None,
    toolbar_position: str = "top",
    port: int | None = None,
    widget_id: str | None = None,
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
    buttons : list[dict], optional
        List of button configs to generate a toolbar.
    port : int, optional
        Server port (only used if InlineWidget fallback is needed).

    Returns
    -------
    BaseWidget
        Widget implementing BaseWidget protocol.
    """
    from .notebook import create_dataframe_widget

    # Normalize input to row_data and columns
    row_data = []
    columns = []

    # Handle pandas DataFrame (duck typing)
    if hasattr(df, "to_dict") and hasattr(df, "columns"):
        row_data = df.to_dict(orient="records")
        columns = list(df.columns)
    # Handle list of dicts: [{'a': 1}, {'a': 2}]
    elif isinstance(df, list):
        if df:
            row_data = df
            columns = list(df[0].keys()) if isinstance(df[0], dict) else []
    # Handle dict of lists: {'a': [1, 2], 'b': [3, 4]}
    elif isinstance(df, dict):
        columns = list(df.keys())
        if columns:
            length = len(df[columns[0]])
            for i in range(length):
                row = {col: df[col][i] for col in columns}
                row_data.append(row)

    # Use provided widget_id or generate new one
    if widget_id is None:
        widget_id = uuid.uuid4().hex

    # Create widget using auto-backend selection
    widget = create_dataframe_widget(
        row_data=row_data,
        columns=columns,
        widget_id=widget_id,
        title=title,
        theme=theme,
        aggrid_theme=aggrid_theme,
        width=width,
        height=height,
        header_html=header_html,
        grid_options=grid_options,
        buttons=buttons,
        toolbar_position=toolbar_position,
        port=port,
    )

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display automatically
    widget.display()
    return widget
