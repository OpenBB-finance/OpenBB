"""IFrame Rendering Path and WebSocket Bridge for PyWry Widgets."""
# pylint: disable=too-many-lines,wrong-import-position
# mypy: disable-error-code="import-untyped,no-untyped-call,no-any-return"
# flake8: noqa S608

from __future__ import annotations

import asyncio
import io
import json
import os
import queue
import sys
import threading
import time
import uuid

from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING, Any, Literal

from .assets import (
    get_aggrid_css,
    get_aggrid_defaults_js,
    get_aggrid_js,
    get_plotly_js,
    get_plotly_templates_js,
    get_pywry_css,
    get_toast_css,
    get_toast_notifications_js,
)
from .config import get_settings
from .models import ThemeMode
from .runtime import is_headless
from .state_mixins import (
    GridStateMixin,
    PlotlyStateMixin,
    ToolbarStateMixin,
    _normalize_figure,
)
from .toolbar import Toolbar, get_toolbar_script, wrap_content_with_toolbars
from .widget_protocol import BaseWidget  # noqa: TC001

# Explicitly export BaseWidget to satisfy mypy explicit re-export check
__all__ = ["BaseWidget", "InlineWidget"]


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from .grid import GridConfig
    from .plotly_config import PlotlyConfig

    try:
        from plotly.graph_objects import Figure

        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

# Check for debug mode environment variable
PYWRY_DEBUG = os.environ.get("PYWRY_DEBUG", "").lower() in ("1", "true", "yes", "on")

# Theme type for server vs desktop mode
# In headless/server mode, default to "system" to follow browser preferences
# In desktop mode, default to "dark" for native windows
ThemeLiteral = Literal["dark", "light", "system"]


def _get_default_theme() -> ThemeLiteral:
    """Get the default theme based on execution mode.

    Returns "system" in headless/server mode to follow browser preferences.
    Returns "dark" in desktop mode for native windows.
    """
    return "system" if is_headless() else "dark"


try:
    import uvicorn

    from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, Response

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


# Global server state
class _ServerState:  # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        self.server: Any = None
        self.server_thread: threading.Thread | None = None
        self.server_loop: Any = None
        self.app: FastAPI | None = None
        self.port: int | None = None
        self.host: str | None = None
        self.widget_prefix: str = "/widget"  # Configurable URL prefix

        # === Local-only state (not externalized) ===
        # Callbacks and output widgets must stay in-process (not serializable)
        self.local_widgets: dict[str, dict[str, Any]] = {}
        # WebSocket handles are process-specific
        self.connections: dict[str, WebSocket] = {}
        self.event_queues: dict[str, asyncio.Queue[Any]] = {}
        self.callback_queue: queue.Queue[Any] = queue.Queue()
        self.shutdown_event: asyncio.Event | None = None
        # Event signaled when all widgets disconnect (for block())
        self.disconnect_event: threading.Event = threading.Event()

        # === Local mode state ===
        # Widget state for single-process (non-deploy) mode
        self.widgets: dict[str, dict[str, Any]] = {}
        self.widget_tokens: dict[str, str] = {}
        # Internal API token for protecting HTTP endpoints
        self.internal_api_token: str | None = None

        # === Pluggable backends (lazily initialized) ===
        self._widget_store: Any | None = None
        self._callback_registry: Any | None = None
        self._connection_router: Any | None = None
        self._worker_id: str | None = None

    @property
    def worker_id(self) -> str:
        """Get unique worker identifier."""
        if self._worker_id is None:
            self._worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        return self._worker_id

    def get_widget_store(self) -> Any:
        """Get the configured widget store (lazy initialization)."""
        if self._widget_store is None:
            from .state import get_widget_store as _get_store

            self._widget_store = _get_store()
        return self._widget_store

    def get_callback_registry(self) -> Any:
        """Get the local callback registry."""
        if self._callback_registry is None:
            from .state.callbacks import CallbackRegistry

            self._callback_registry = CallbackRegistry()
        return self._callback_registry

    def get_connection_router(self) -> Any:
        """Get the configured connection router (lazy initialization)."""
        if self._connection_router is None:
            from .state import get_connection_router as _get_router

            self._connection_router = _get_router()
        return self._connection_router

    # === Unified Widget Access (works in both modes) ===

    def register_widget(
        self,
        widget_id: str,
        html: str,
        callbacks: dict[str, Any] | None = None,
        output: Any = None,
        token: str | None = None,
    ) -> None:
        """Register a widget with HTML content and optional callbacks.

        In deploy mode, HTML/token are stored externally; callbacks stay local.
        In normal mode, everything is stored in self.widgets dict.
        """
        from .state import is_deploy_mode

        # Always store local-only data (callbacks, output widget)
        self.local_widgets[widget_id] = {
            "callbacks": callbacks or {},
            "output": output,
        }

        if is_deploy_mode():
            # Store HTML externally via async store
            from .state import run_async

            store = self.get_widget_store()
            run_async(store.register(widget_id, html, token=token))

            # Register callbacks in local registry
            registry = self.get_callback_registry()
            for event_type, callback in (callbacks or {}).items():
                run_async(registry.register(widget_id, event_type, callback))
        else:
            # Local mode: store everything in widgets dict
            self.widgets[widget_id] = {
                "html": html,
                "callbacks": callbacks or {},
                "output": output,
            }
            if token:
                self.widget_tokens[widget_id] = token

    def get_widget_html(self, widget_id: str) -> str | None:
        """Get widget HTML content."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            return run_async(store.get_html(widget_id))
        widget = self.widgets.get(widget_id)
        return widget["html"] if widget else None

    def widget_exists(self, widget_id: str) -> bool:
        """Check if widget exists."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            return run_async(store.exists(widget_id))
        return widget_id in self.widgets

    def get_widget_callbacks(self, widget_id: str) -> dict[str, Any]:
        """Get callbacks for a widget (always local)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            local = self.local_widgets.get(widget_id, {})
            return local.get("callbacks", {})
        widget = self.widgets.get(widget_id, {})
        return widget.get("callbacks", {})

    def get_widget_token(self, widget_id: str) -> str | None:
        """Get widget authentication token (sync version)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            return run_async(store.get_token(widget_id))
        return self.widget_tokens.get(widget_id)

    def set_widget_token(self, widget_id: str, token: str) -> None:
        """Set widget authentication token."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            # In deploy mode, token is set during register
            # For updates, we'd need store.update_token - for now just store locally
            self.widget_tokens[widget_id] = token
        else:
            self.widget_tokens[widget_id] = token

    def update_widget_html(self, widget_id: str, html: str) -> None:
        """Update widget HTML content."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            run_async(store.update_html(widget_id, html))
        else:
            if widget_id in self.widgets:
                self.widgets[widget_id]["html"] = html

    def update_widget_callbacks(self, widget_id: str, callbacks: dict[str, Any]) -> None:
        """Update widget callbacks."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            self.local_widgets.setdefault(widget_id, {})["callbacks"] = callbacks
            # Update registry
            registry = self.get_callback_registry()
            for event_type, callback in callbacks.items():
                registry.register(widget_id, event_type, callback)
        else:
            if widget_id in self.widgets:
                self.widgets[widget_id]["callbacks"] = callbacks

    def delete_widget(self, widget_id: str) -> None:
        """Delete a widget and all associated data."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async_fire_and_forget

            # Delete from external store
            store = self.get_widget_store()
            run_async_fire_and_forget(store.delete(widget_id))

            # Delete from local registry (unregister all events for this widget)
            registry = self.get_callback_registry()
            registry.unregister(widget_id, event_type=None)

            # Clean up local data
            self.local_widgets.pop(widget_id, None)
        else:
            self.widgets.pop(widget_id, None)

        # Always clean up these
        self.widget_tokens.pop(widget_id, None)
        self.event_queues.pop(widget_id, None)

    def get_active_widget_ids(self) -> list[str]:
        """Get list of active widget IDs."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            return run_async(store.list_active())
        return list(self.widgets.keys())

    def widget_count(self) -> int:
        """Get count of active widgets."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            from .state import run_async

            store = self.get_widget_store()
            return run_async(store.count())
        return len(self.widgets)

    # ═══════════════════════════════════════════════════════════
    # ASYNC METHODS - Use these from async FastAPI route handlers
    # ═══════════════════════════════════════════════════════════

    async def get_widget_html_async(self, widget_id: str) -> str | None:
        """Get widget HTML content (async version).

        Use this from async route handlers to avoid deadlock.
        """
        from .state import is_deploy_mode

        if is_deploy_mode():
            store = self.get_widget_store()
            return await store.get_html(widget_id)
        widget = self.widgets.get(widget_id)
        return widget["html"] if widget else None

    async def widget_exists_async(self, widget_id: str) -> bool:
        """Check if widget exists (async version)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            store = self.get_widget_store()
            return await store.exists(widget_id)
        return widget_id in self.widgets

    async def get_widget_token_async(self, widget_id: str) -> str | None:
        """Get widget authentication token (async version)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            store = self.get_widget_store()
            return await store.get_token(widget_id)
        return self.widget_tokens.get(widget_id)

    async def get_active_widget_ids_async(self) -> list[str]:
        """Get list of active widget IDs (async version)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            store = self.get_widget_store()
            return await store.list_active()
        return list(self.widgets.keys())

    async def widget_count_async(self) -> int:
        """Get count of active widgets (async version)."""
        from .state import is_deploy_mode

        if is_deploy_mode():
            store = self.get_widget_store()
            return await store.count()
        return len(self.widgets)


_state = _ServerState()


def _generate_widget_token(widget_id: str) -> str | None:
    """Generate or retrieve a widget authentication token.

    Returns the token if authentication is enabled, None otherwise.
    The token is cached in _state.widget_tokens for reuse.

    Parameters
    ----------
    widget_id : str
        The unique widget identifier.

    Returns
    -------
    str | None
        The authentication token, or None if auth is disabled.
    """
    server_settings = get_settings().server

    if not server_settings.websocket_require_token:
        return None

    # Check local cache first
    if widget_id in _state.widget_tokens:
        return _state.widget_tokens[widget_id]

    # Generate new token
    import secrets

    token = secrets.token_urlsafe(32)
    _state.widget_tokens[widget_id] = token
    return token


def _get_pywry_bridge_js(widget_id: str, widget_token: str | None = None) -> str:
    """Generate the pywry JavaScript bridge with bidirectional communication.

    Supports:
    - JS → Python via WebSocket
    - Python → JS via WebSocket
    - WebSocket security with per-widget token authentication

    Parameters
    ----------
    widget_id : str
        The unique widget identifier.
    widget_token : str | None
        The per-widget token for WebSocket authentication.
        If None, no token auth header is included.
    """
    # Build token header
    if widget_token:
        ws_token_header = f"const WS_AUTH_TOKEN = '{widget_token}';"
    else:
        ws_token_header = "const WS_AUTH_TOKEN = null;"

    return f"""
<script>
(function() {{
    const widgetId = '{widget_id}';
    {ws_token_header}
    
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
    let authFailures = 0;  // Track auth failures for auto-refresh

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

        // Create WebSocket with authentication token in subprotocol if present
        // This keeps the token out of URLs/logs while still being sent in the handshake
        if (WS_AUTH_TOKEN) {{
            socket = new WebSocket(wsUrl, ['pywry.token.' + WS_AUTH_TOKEN]);
        }} else {{
            socket = new WebSocket(wsUrl);
        }}

        socket.onopen = function() {{
            console.log('[PyWry] WebSocket connected');
            reconnectAttempts = 0;
            authFailures = 0;  // Reset auth failure counter on successful connection

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
            console.log('[PyWry] ===== WebSocket CLOSED =====');
            console.log('[PyWry] Close code:', e.code);
            console.log('[PyWry] Close reason:', e.reason);
            console.log('[PyWry] Auth failures before increment:', authFailures);
            window.pywry._ready = false;

            // Don't reconnect if connection was replaced (code 1000 with this reason)
            if (e.code === 1000 && e.reason === 'New connection replaced old one') {{
                console.log('[PyWry] Connection replaced by newer instance, not reconnecting');
                return;
            }}

            // Track authentication failures (code 4001 or 1006 likely means auth issue)
            if (e.code === 4001 || e.code === 1006) {{
                authFailures++;
                console.log('[PyWry] Auth failure detected! New count:', authFailures);
                
                // After 2 auth failures, refresh the page to get new token
                if (authFailures >= 2) {{
                    console.log('[PyWry] ===== REFRESHING PAGE NOW =====');
                    setTimeout(function() {{
                        console.log('[PyWry] Calling window.location.reload()...');
                        window.location.reload();
                    }}, 500);
                    return;
                }}
            }}

            // Don't reconnect if intentional disconnect
            if (window.pywry._intentionalDisconnect) {{
                console.log('[PyWry] Intentional disconnect, not reconnecting');
                return;
            }}

            // Reconnect with backoff
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
            reconnectAttempts++;
            console.log('[PyWry] Reconnecting in', delay, 'ms... (attempt', reconnectAttempts, ')');
            setTimeout(connect, delay);
        }};

        socket.onerror = function(err) {{
            console.error('[PyWry] ===== WebSocket ERROR =====');
            console.error('[PyWry] Error:', err);
            console.error('[PyWry] Socket readyState:', socket.readyState);
            socket.close();
        }};
    }}

    // --- Disconnect handling for page close/refresh/navigate ---
    let disconnectSent = false;

    function sendDisconnect(reason) {{
        if (disconnectSent) return;
        disconnectSent = true;
        window.pywry._intentionalDisconnect = true;

        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Sending disconnect, reason:', reason);
        }}

        // Try WebSocket first
        if (socket && socket.readyState === WebSocket.OPEN) {{
            socket.send(JSON.stringify({{
                type: 'pywry:disconnect',
                data: {{ reason: reason }},
                widgetId: widgetId
            }}));
            socket.close(1000, reason);
        }}

        // Fallback: sendBeacon for reliable delivery on page unload
        try {{
            navigator.sendBeacon(apiUrl + '/disconnect/' + widgetId + '?reason=' + encodeURIComponent(reason));
        }} catch (e) {{
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] sendBeacon failed:', e);
            }}
        }}
    }}

    // Page is being unloaded (close tab, refresh, navigate away)
    window.addEventListener('beforeunload', function() {{
        sendDisconnect('beforeunload');
    }});

    // Fallback for mobile/Safari - fires when page is hidden
    window.addEventListener('pagehide', function() {{
        sendDisconnect('pagehide');
    }});

    // Optional: detect when tab becomes hidden (not closing, just backgrounded)
    // We don't disconnect here, but could add heartbeat logic in the future
    document.addEventListener('visibilitychange', function() {{
        if (document.visibilityState === 'hidden') {{
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Page hidden (visibility change)');
            }}
        }}
    }});

    // Connect immediately
    connect();
    window.pywry._ready = true;
    if ({str(PYWRY_DEBUG).lower()}) {{
        console.log('[PyWry] Bridge ready! widgetId:', widgetId);
        console.log('[PyWry] window.pywry object:', window.pywry);
    }}

    // Register handler for theme updates - update grid theme class
    window.pywry.on('pywry:update-theme', function(data) {{
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Received theme update:', data.theme);
        }}

        const isDark = data.theme && data.theme.includes('dark');
        const isLight = !isDark;

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

        // Update ALL toolbar elements (they're part of the same document in browser mode!)
        document.querySelectorAll('.pywry-toolbar').forEach(function(toolbar) {{
            toolbar.classList.remove('pywry-theme-dark', 'pywry-theme-light');
            toolbar.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
        }});

        // Update all wrapper elements
        document.querySelectorAll('[class*="pywry-wrapper"]').forEach(function(wrapper) {{
            wrapper.classList.remove('pywry-theme-dark', 'pywry-theme-light');
            wrapper.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
        }});

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
    window.pywry.on('pywry:update-html', function(data) {{
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Received HTML update, reloading page');
        }}
        // Add small delay to ensure server state is updated before reload
        setTimeout(function() {{
            window.location.reload();
        }}, 50);
    }});

    // Register handler for client-side navigation
    window.pywry.on('pywry:navigate', function(data) {{
        if (data.url) {{
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Navigating to:', data.url);
            }}
            window.location.href = data.url;
        }}
    }});

    // Register handler for showing alerts - uses PYWRY_TOAST for typed notifications
    window.pywry.on('pywry:alert', function(data) {{
        const message = data.message || data.text || '';
        const type = data.type || 'info';
        // Get the widget container for scoped toast positioning
        const container = document.querySelector('.pywry-widget') || document.body;
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Alert:', type, message);
        }}

        // Use toast system if available
        if (window.PYWRY_TOAST) {{
            if (type === 'confirm') {{
                window.PYWRY_TOAST.confirm({{
                    message: message,
                    title: data.title,
                    position: data.position,
                    container: container,
                    onConfirm: function() {{
                        if (data.callback_event) {{
                            window.pywry.emit(data.callback_event, {{ confirmed: true }});
                        }}
                    }},
                    onCancel: function() {{
                        if (data.callback_event) {{
                            window.pywry.emit(data.callback_event, {{ confirmed: false }});
                        }}
                    }}
                }});
            }} else {{
                window.PYWRY_TOAST.show({{
                    message: message,
                    title: data.title,
                    type: type,
                    duration: data.duration,
                    position: data.position,
                    container: container
                }});
            }}
        }} else {{
            // Fallback to browser alert
            alert(message);
        }}
    }});

    // Register handler for CSS injection - inject or update a style element
    // For notebook widgets, also duplicate :root rules to .pywry-widget for proper scoping
    window.pywry.on('pywry:inject-css', function(data) {{
        if (!data.css) {{
            console.error('[PyWry] inject-css requires css property');
            return;
        }}
        // Rewrite :root selectors to also target .pywry-widget for notebook scoping
        // This ensures CSS variables work in both native windows and notebook widgets
        let css = data.css;
        if (css.includes(':root')) {{
            css = css.replace(/:root\\s*\\{{/g, ':root, .pywry-widget, .pywry-theme-dark, .pywry-theme-light {{');
        }}
        const id = data.id || 'pywry-injected-style';
        let style = document.getElementById(id);
        if (style) {{
            style.textContent = css;
        }} else {{
            style = document.createElement('style');
            style.id = id;
            style.textContent = css;
            document.head.appendChild(style);
        }}
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Injected CSS with id:', id);
        }}
    }});

    // Register handler for CSS removal
    window.pywry.on('pywry:remove-css', function(data) {{
        if (!data.id) {{
            console.error('[PyWry] remove-css requires id property');
            return;
        }}
        const style = document.getElementById(data.id);
        if (style) {{
            style.remove();
            if ({str(PYWRY_DEBUG).lower()}) {{
                console.log('[PyWry] Removed CSS with id:', data.id);
            }}
        }}
    }});

    // Register handler for setting inline styles on elements
    // Usage: emit('pywry:set-style', {{selector: '.my-class', styles: {{fontWeight: 'bold', color: 'red'}}}})
    // Or target by id: emit('pywry:set-style', {{id: 'my-element', styles: {{fontSize: '20px'}}}})
    window.pywry.on('pywry:set-style', function(data) {{
        if (!data.styles) {{
            console.error('[PyWry] set_style requires styles property');
            return;
        }}
        let elements = [];
        if (data.id) {{
            const el = document.getElementById(data.id);
            if (el) elements.push(el);
        }} else if (data.selector) {{
            elements = Array.from(document.querySelectorAll(data.selector));
        }} else {{
            console.error('[PyWry] set_style requires id or selector property');
            return;
        }}
        elements.forEach(function(el) {{
            Object.keys(data.styles).forEach(function(prop) {{
                el.style[prop] = data.styles[prop];
            }});
        }});
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Set styles on', elements.length, 'elements:', data.styles);
        }}
    }});

    // Built-in handler for updating element content (innerHTML or textContent)
    // Usage: emit('pywry:set-content', {{id: 'my-element', html: '<b>Bold</b>'}})
    // Or: emit('pywry:set-content', {{selector: '.my-class', text: 'Plain text'}})
    window.pywry.on('pywry:set-content', function(data) {{
        let elements = [];
        if (data.id) {{
            const el = document.getElementById(data.id);
            if (el) elements.push(el);
        }} else if (data.selector) {{
            elements = Array.from(document.querySelectorAll(data.selector));
        }} else {{
            console.error('[PyWry] set_content requires id or selector property');
            return;
        }}
        elements.forEach(function(el) {{
            if ('html' in data) {{
                el.innerHTML = data.html;
            }} else if ('text' in data) {{
                el.textContent = data.text;
            }}
        }});
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Set content on', elements.length, 'elements');
        }}
    }});

    // Register handler for file downloads - triggers browser save dialog
    window.pywry.on('pywry:download', function(data) {{
        if (!data.content || !data.filename) {{
            console.error('[PyWry] Download requires content and filename');
            return;
        }}
        const mimeType = data.mimeType || 'application/octet-stream';
        const blob = new Blob([data.content], {{ type: mimeType }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        if ({str(PYWRY_DEBUG).lower()}) {{
            console.log('[PyWry] Downloaded:', data.filename);
        }}
    }});

    // Register handler for Plotly figure updates - use Plotly.react for smooth updates
    window.pywry.on('plotly:update-figure', function(data) {{
        const chartEl = document.getElementById('chart');

        if (chartEl && (typeof Plotly !== 'undefined' || typeof window.Plotly !== 'undefined')) {{
            const PlotlyLib = typeof Plotly !== 'undefined' ? Plotly : window.Plotly;

            // Handle both formats: {{figure: {{data, layout}}}} or {{data, layout}} directly
            const figureData = data.figure || data;
            const traceData = figureData.data || [];
            const layout = figureData.layout || {{}};
            const config = data.config || {{}};

            // Process modebar button click handlers (convert event to function or string to function)
            if (config.modeBarButtonsToAdd) {{
                config.modeBarButtonsToAdd = config.modeBarButtonsToAdd.map(function(btn) {{
                    // If button has 'event' but no 'click', generate a click handler
                    if (btn.event && !btn.click) {{
                        const eventName = btn.event;
                        const eventData = btn.data || {{}};
                        btn.click = function(gd) {{
                            window.pywry.emit(eventName, eventData);
                        }};
                    }} else if (typeof btn.click === 'string') {{
                        try {{
                            btn.click = eval('(' + btn.click + ')');
                        }} catch(e) {{
                            console.error('[PyWry] Failed to parse button click:', e);
                        }}
                    }}
                    return btn;
                }});
            }}

            PlotlyLib.react(chartEl, traceData, layout, config);
        }} else {{
            console.error('[PyWry] Cannot update: chartEl or Plotly not available');
        }}
    }});

    // Register handler for Plotly layout updates (partial updates like axis type, title, etc.)
    window.pywry.on('plotly:update-layout', function(data) {{
        const chartEl = document.getElementById('chart');
        if (chartEl && (typeof Plotly !== 'undefined' || typeof window.Plotly !== 'undefined')) {{
            const PlotlyLib = typeof Plotly !== 'undefined' ? Plotly : window.Plotly;
            const layout = data.layout || {{}};
            PlotlyLib.relayout(chartEl, layout);
        }}
    }});

    window.pywry._fire('pywry:ready', {{}});

    if ({str(PYWRY_DEBUG).lower()}) {{
        console.log('[PyWry] Bridge initialized for widget:', widgetId);
        console.log('[PyWry] API URL:', apiUrl);
    }}
}})();
</script>
<script>
{get_toast_notifications_js()}
</script>
"""


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:  # pylint: disable=unused-argument
    # Capture the running event loop for emit() to use
    _state.server_loop = asyncio.get_running_loop()
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
    from .state import is_deploy_mode

    event_type = msg.get("type", "")
    if PYWRY_DEBUG:
        print(f"[SERVER] Routing event: {event_type} for widget {widget_id[:8]}...")

    # Handle disconnect message specially
    if event_type == "pywry:disconnect":
        reason = msg.get("data", {}).get("reason", "client")
        _handle_widget_disconnect(widget_id, reason)
        return

    # Get callbacks based on mode
    if is_deploy_mode():
        # In deploy mode, callbacks are stored in local_widgets
        local_data = _state.local_widgets.get(widget_id, {})
        callbacks = local_data.get("callbacks", {})
        if PYWRY_DEBUG and not callbacks:
            print(f"[SERVER] No callbacks in local_widgets for {widget_id[:8]}")
    else:
        # Local mode
        if widget_id not in _state.widgets:
            if PYWRY_DEBUG:
                print(f"[SERVER] Widget {widget_id} not in _state.widgets!")
            return
        callbacks = _state.widgets[widget_id].get("callbacks", {})

    if event_type in callbacks:
        if PYWRY_DEBUG:
            print(f"[SERVER] Found callback for {event_type}, queueing...")
        _state.callback_queue.put(
            (callbacks[event_type], msg.get("data", {}), event_type, widget_id)
        )


def _handle_widget_disconnect(  # pylint: disable=too-many-branches
    widget_id: str, reason: str = "unknown"
) -> None:
    """Handle widget disconnection: cleanup state and fire callback.

    Parameters
    ----------
    widget_id : str
        The widget ID that disconnected.
    reason : str
        Reason for disconnect: 'client', 'websocket_close', 'beacon', 'server_shutdown'.
    """
    from .state import is_deploy_mode

    if PYWRY_DEBUG:
        print(f"[SERVER] Widget disconnect: {widget_id}, reason: {reason}")

    # Get callbacks based on mode
    if is_deploy_mode():
        local_data = _state.local_widgets.get(widget_id, {})
        callbacks = local_data.get("callbacks", {})
    else:
        if widget_id not in _state.widgets:
            return
        widget_data = _state.widgets[widget_id]
        callbacks = widget_data.get("callbacks", {})

    # Fire pywry:disconnect callback if registered, using GenericEvent-style data
    if "pywry:disconnect" in callbacks:
        disconnect_data = {
            "reason": reason,
            "widget_id": widget_id,
        }
        _state.callback_queue.put(
            (callbacks["pywry:disconnect"], disconnect_data, "pywry:disconnect", widget_id)
        )

    # Clean up connection state (but NOT the widget itself for websocket_close)
    # This allows browser refreshes to work - the widget HTML stays registered
    if widget_id in _state.connections:
        del _state.connections[widget_id]

    # These reasons indicate the browser tab is actually closing/leaving
    # (not just a page refresh or websocket reconnect)
    _remove_widget_reasons = (
        "client",
        "beacon",
        "server_shutdown",
        "beforeunload",  # Browser tab closing
        "pagehide",  # Mobile/Safari tab closing
    )
    if reason in _remove_widget_reasons:
        if is_deploy_mode():
            if widget_id in _state.local_widgets:
                del _state.local_widgets[widget_id]
        else:
            if widget_id in _state.widgets:
                del _state.widgets[widget_id]
        if widget_id in _state.event_queues:
            del _state.event_queues[widget_id]
        # Clean up per-widget token
        if widget_id in _state.widget_tokens:
            del _state.widget_tokens[widget_id]

        # Signal disconnect_event if no widgets remain (for block())
        if is_deploy_mode():
            if len(_state.local_widgets) == 0:
                _state.disconnect_event.set()
        else:
            if len(_state.widgets) == 0:
                _state.disconnect_event.set()


def _validate_websocket_origin(headers: dict[str, str], expected_host: str) -> bool:
    """Validate WebSocket connection origin matches expected host.

    Parameters
    ----------
    headers : dict[str, str]
        The WebSocket request headers.
    expected_host : str
        The expected host (e.g., "127.0.0.1:8765" or "localhost:8765").

    Returns
    -------
    bool
        True if origin is valid, False otherwise.
    """
    # Check Origin header (WebSocket standard)
    origin = headers.get("origin")
    if origin:
        # Parse origin to extract host:port
        # Origin format: "http://host:port" or "https://host:port"
        try:
            from urllib.parse import urlparse

            parsed = urlparse(origin)
            origin_netloc = parsed.netloc  # host:port
            # Match against expected host
            if origin_netloc == expected_host:
                return True
            # Also accept without port if default ports
            origin_host = parsed.hostname
            expected_host_only = expected_host.split(":")[0]
            if origin_host == expected_host_only:
                return True
        except Exception:
            pass

    # Check Referer as fallback
    referer = headers.get("referer")
    if referer:
        try:
            from urllib.parse import urlparse

            parsed = urlparse(referer)
            referer_netloc = parsed.netloc
            if referer_netloc == expected_host:
                return True
            referer_host = parsed.hostname
            expected_host_only = expected_host.split(":")[0]
            if referer_host == expected_host_only:
                return True
        except Exception:
            pass

    # Check Host header (should match server)
    host = headers.get("host")
    if host and host == expected_host:
        return True

    return False


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
    _state.widget_prefix = settings.widget_prefix.rstrip("/")  # Store normalized prefix

    # Initialize internal API token for protecting internal HTTP endpoints (not widget serving)
    if settings.internal_api_token:
        _state.internal_api_token = settings.internal_api_token
    else:
        import secrets

        _state.internal_api_token = secrets.token_urlsafe(32)

    # Header name for internal API authentication
    internal_header = settings.internal_api_header

    def _check_internal_auth(request: Request) -> bool:
        """Check if request has valid internal API token. Returns False = 404."""
        token = request.headers.get(internal_header)
        return token == _state.internal_api_token

    # Capture strict_widget_auth setting for use in endpoint
    require_widget_header_auth = settings.strict_widget_auth

    @app.get(
        f"{settings.widget_prefix.rstrip('/')}/{{widget_id}}",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    async def get_widget(widget_id: str, request: Request) -> HTMLResponse:
        """Serve widget HTML.

        Security:
        - strict_widget_auth=True (browser mode): Requires internal API header
        - strict_widget_auth=False (notebook mode): Only checks widget exists (allows iframes)

        Deploy mode: Fetches HTML from Redis store instead of local dict.
        """
        import time  # pylint: disable=redefined-outer-name,reimported

        # In strict mode (browser), require header auth
        if require_widget_header_auth and not _check_internal_auth(request):
            return HTMLResponse(status_code=404)

        if PYWRY_DEBUG:
            print(f"[SERVER] {_state.widget_prefix}/{widget_id} accessed at {time.time()}")

        # Use deploy-mode aware async method to check widget existence and get HTML
        html = await _state.get_widget_html_async(widget_id)
        if html is None:
            return HTMLResponse(status_code=404)

        if PYWRY_DEBUG:
            print(f"[SERVER] Serving HTML for {widget_id}, length: {len(html)}")

        # Add headers to prevent browser caching
        return HTMLResponse(
            html,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.websocket("/ws/{widget_id}")
    async def websocket_endpoint(  # pylint: disable=too-many-branches,too-many-statements
        websocket: WebSocket, widget_id: str
    ) -> None:
        """WebSocket endpoint with security hardening.

        Security features:
        - Origin validation: Ensures connections only come from same-origin (auto-disabled with per-widget tokens)
        - Per-widget token authentication: Unique token per widget sent via WebSocket subprotocol

        Note: Token is sent via Sec-WebSocket-Protocol header to avoid exposure in logs/URLs
        """
        if PYWRY_DEBUG:
            print(f"[SERVER] WebSocket connection request for {widget_id}")

        # Security validation BEFORE accepting the connection
        server_settings = get_settings().server

        # 1. Origin validation (if allowed_origins is configured)
        # Empty list = allow any origin (rely on token auth only)
        # Non-empty list = only allow specified origins
        allowed_origins = server_settings.websocket_allowed_origins
        if allowed_origins:
            origin = websocket.headers.get("origin", "")
            if origin not in allowed_origins:
                if PYWRY_DEBUG:
                    print(f"[SERVER] WebSocket rejected: Origin '{origin}' not in allowed list")
                    print(f"[SERVER] Allowed origins: {allowed_origins}")
                await websocket.close(code=1008, reason="Origin not allowed")
                return

        # 2. Token validation (if token auth is required)
        # Extract token from Sec-WebSocket-Protocol header (sent as subprotocol)
        token = None
        accepted_subprotocol = None
        if server_settings.websocket_require_token:
            # Check for token in Sec-WebSocket-Protocol header
            # Client sends: new WebSocket(url, ['pywry.token.XXX'])
            # Server receives in sec-websocket-protocol header
            sec_websocket_protocol = websocket.headers.get("sec-websocket-protocol", "")
            if sec_websocket_protocol.startswith("pywry.token."):
                token = sec_websocket_protocol.replace("pywry.token.", "", 1)
                # Must accept the subprotocol in response
                accepted_subprotocol = sec_websocket_protocol

            # Check per-widget token (only supported mode)
            # Use async version to avoid blocking in async context
            expected_token = await _state.get_widget_token_async(widget_id)

            # If no token exists for this widget, reject - client needs to reload
            if not expected_token:
                if PYWRY_DEBUG:
                    print(f"[SERVER] No token found for widget: {widget_id}")
                    print("[SERVER] Client should refresh page to get new token")
                await websocket.close(code=4001, reason="Unknown widget - refresh page")
                return

            # Validate token - REJECT invalid tokens (client should refresh page)
            if not token or token != expected_token:
                if PYWRY_DEBUG:
                    print("[SERVER] WebSocket connection rejected: Invalid or missing token")
                    print(
                        f"[SERVER] Widget ID: {widget_id}, Expected token exists: {expected_token is not None}"
                    )
                    print("[SERVER] Client should refresh page to get new token")
                await websocket.close(code=4001, reason="Invalid token - refresh page")
                return

        # Security checks passed, accept connection with subprotocol if provided
        if accepted_subprotocol:
            await websocket.accept(subprotocol=accepted_subprotocol)
        else:
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
            # Only handle disconnect if this is still the active connection
            if widget_id in _state.connections and _state.connections[widget_id] == websocket:
                _handle_widget_disconnect(widget_id, "websocket_close")
        finally:
            sender.cancel()

    @app.get("/health", include_in_schema=False)
    async def health(request: Request) -> Response:
        # Health endpoint also requires auth - 404 if missing
        if not _check_internal_auth(request):
            return Response(status_code=404)
        return Response(content='{"status":"ok"}', media_type="application/json")

    @app.post("/register_widget", include_in_schema=False)
    async def register_widget(request: Request) -> Response:
        """Register a widget with the running server (for kernel restart scenarios)."""
        # Require internal API token - 404 if missing/invalid
        if not _check_internal_auth(request):
            return Response(status_code=404)

        try:
            data = await request.json()
            widget_id = data.get("widget_id")
            html = data.get("html")

            if not widget_id or not html:
                return Response(status_code=404)

            _state.widgets[widget_id] = {"html": html, "callbacks": {}}
            _state.event_queues[widget_id] = asyncio.Queue()

            return Response(
                content=json.dumps({"status": "registered", "widget_id": widget_id}),
                media_type="application/json",
            )
        except Exception:
            return Response(status_code=404)

    @app.post("/disconnect/{widget_id}", include_in_schema=False)
    async def disconnect_widget(
        widget_id: str, _request: Request, reason: str = "beacon"
    ) -> Response:
        """Handle widget disconnect via sendBeacon fallback.

        This endpoint is called from the browser on page unload.
        We don't require auth here since:
        1. It's just cleanup - no data is exposed
        2. sendBeacon can't set custom headers
        3. The worst case is premature cleanup which is harmless
        """
        _handle_widget_disconnect(widget_id, reason)
        return Response(
            content=json.dumps({"status": "disconnected", "widget_id": widget_id}),
            media_type="application/json",
        )

    return app


def _process_callbacks() -> None:  # pylint: disable=too-many-branches
    """Background thread to process callbacks."""
    while True:
        try:
            callback, data, event_type, widget_id = _state.callback_queue.get(timeout=0.1)
            try:
                # Get the output widget for this widget if it exists
                # In deploy mode, output is stored in local_widgets
                from .state import is_deploy_mode

                if is_deploy_mode():
                    widget_data = _state.local_widgets.get(widget_id, {})
                else:
                    widget_data = _state.widgets.get(widget_id, {})
                output_widget = widget_data.get("output")

                if output_widget is not None:
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


def _get_verification_settings(settings: Any) -> bool | str:
    """Determine SSL verification settings based on config and environment."""
    if not settings.ssl_certfile:
        return False

    if settings.ssl_ca_certs:
        return settings.ssl_ca_certs

    # Check for proxies - default to False if proxying
    import urllib.request

    proxies = urllib.request.getproxies()
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "PYWRY_HTTP_PROXY", "PYWRY_HTTPS_PROXY"]

    has_proxy = bool(proxies) or any(
        os.environ.get(var) or os.environ.get(var.lower()) for var in proxy_vars
    )

    return not has_proxy


def _make_server_request(
    method: str,
    endpoint: str,
    port: int | None = None,
    host: str | None = None,
    json_data: dict[str, Any] | None = None,
    timeout: float = 1.0,
    **kwargs: Any,
) -> Any:
    """Make an internal request to the PyWry server with authentication."""
    import requests

    settings = get_settings().server
    target_host = host or settings.host
    target_port = port or settings.port

    protocol = "https" if settings.ssl_certfile else "http"
    base_url = f"{protocol}://{target_host}:{target_port}"

    # Ensure endpoint starts with /
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    url = f"{base_url}{endpoint}"
    verify = _get_verification_settings(settings)

    # Add internal API auth header for protected endpoints
    headers = kwargs.pop("headers", {})
    if _state.internal_api_token:
        headers[settings.internal_api_header] = _state.internal_api_token

    return requests.request(
        method=method,
        url=url,
        json=json_data,
        timeout=timeout,
        verify=verify,
        headers=headers,
        **kwargs,
    )


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
        except SystemExit:
            # uvicorn calls sys.exit(1) when port bind fails - suppress it
            pass
        finally:
            # Clean up any pending tasks - suppress all errors during cleanup
            with suppress(RuntimeError, asyncio.CancelledError):
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                # Give tasks a chance to handle cancellation
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            with suppress(RuntimeError):
                loop.close()

    _state.server_thread = threading.Thread(target=run, daemon=True)
    _state.server_thread.start()

    # Start callback processor
    callback_thread = threading.Thread(target=_process_callbacks, daemon=True)
    callback_thread.start()

    # Wait for server to start
    for _ in range(50):
        try:
            r = _make_server_request(
                "GET",
                "/health",
                host=_state.host,
                port=_state.port,
                timeout=0.1,
            )
            if r.status_code == 200:
                break
        except Exception:  # noqa: S110
            pass
        time.sleep(0.1)


def stop_server(timeout: float = 5.0) -> None:
    """Stop the FastAPI server and wait for it to fully release the port.

    Fires disconnect callbacks for all active widgets before stopping.

    Parameters
    ----------
    timeout : float
        Maximum time to wait for server to stop, in seconds.
    """
    server = _state.server
    server_thread = _state.server_thread
    server_loop = _state.server_loop

    if server is not None:
        # Fire disconnect callbacks for all active widgets (clean shutdown)
        widget_ids = list(_state.widgets.keys())
        for widget_id in widget_ids:
            _handle_widget_disconnect(widget_id, "server_shutdown")

        # Close all WebSocket connections BEFORE shutting down
        connections_to_close = list(_state.connections.items())
        for widget_id, ws in connections_to_close:
            with suppress(Exception):
                if ws and ws.client_state.name == "CONNECTED":
                    # Use asyncio to properly close the websocket
                    if server_loop:
                        asyncio.run_coroutine_threadsafe(
                            ws.close(code=1000, reason="Server shutting down"), server_loop
                        ).result(timeout=1.0)

        # Clear connection state
        _state.connections.clear()
        _state.event_queues.clear()

        # Signal the server to exit
        server.should_exit = True

        # Send a request to wake up the server so it checks should_exit
        if _state.port is not None and _state.host is not None:
            with suppress(Exception):
                _make_server_request(
                    "GET",
                    "/health",
                    host=_state.host,
                    port=_state.port,
                    timeout=0.5,
                )

        # Wait for graceful shutdown
        if server_thread is not None and server_thread.is_alive():
            server_thread.join(timeout=timeout)

            # If thread is still alive after timeout, force-stop the loop
            if server_thread.is_alive() and server_loop is not None:
                with suppress(Exception):
                    server_loop.call_soon_threadsafe(server_loop.stop)
                server_thread.join(timeout=1.0)

        # Give OS time to release the socket
        time.sleep(0.3)

    # Always reset state, even if server was None (handles partial startup failures)
    _state.server = None
    _state.server_thread = None
    _state.server_loop = None
    _state.port = None
    _state.app = None
    _state.shutdown_event = None
    # Reset disconnect event for next server start
    _state.disconnect_event.clear()


def block() -> None:
    """Block until all widgets disconnect or KeyboardInterrupt.

    Use this in scripts using BROWSER mode to keep the server alive
    until all browser tabs are closed.

    Examples
    --------
    >>> widget = pywry.inline.show("<h1>Hello</h1>")
    >>> widget.open_in_browser()
    >>> pywry.inline.block()  # Wait until browser tab is closed
    """
    if _state.server_thread is None or not _state.server_thread.is_alive():
        return

    # If no widgets, return immediately
    if len(_state.widgets) == 0:
        return

    # Clear the event in case it was set from a previous run
    _state.disconnect_event.clear()

    try:
        # Wait until all widgets disconnect
        while len(_state.widgets) > 0:
            # Check every 0.5 seconds or when signaled
            _state.disconnect_event.wait(timeout=0.5)
            _state.disconnect_event.clear()
    except KeyboardInterrupt:
        print("\n[PyWry] Interrupted, stopping server...")
    finally:
        # Always stop the server when block() exits
        stop_server()


def deploy() -> None:
    """Deploy the PyWry server for production use.

    This is the recommended way to run PyWry as a standalone web server.
    All configuration is read from the central configuration system.

    Configuration is loaded from (in order of precedence):
    1. Built-in defaults (lowest priority)
    2. pyproject.toml [tool.pywry] section
    3. ./pywry.toml (project-level)
    4. ~/.config/pywry/config.toml (user-level)
    5. Environment variables with PYWRY_SERVER__ prefix (highest priority)

    Key environment variables:
    - PYWRY_SERVER__HOST: Server bind address (default: "127.0.0.1")
    - PYWRY_SERVER__PORT: Server port (default: 8765)
    - PYWRY_SERVER__LOG_LEVEL: Log level (default: "warning")
    - PYWRY_SERVER__WORKERS: Number of workers (default: 1)
    - PYWRY_SERVER__RELOAD: Enable auto-reload (default: false)
    - PYWRY_SERVER__SSL_KEYFILE: Path to SSL key file
    - PYWRY_SERVER__SSL_CERTFILE: Path to SSL certificate file

    Examples
    --------
    Basic deployment using config:

    >>> # Set config via environment:
    >>> # export PYWRY_SERVER__HOST=0.0.0.0
    >>> # export PYWRY_SERVER__PORT=8080
    >>>
    >>> from pywry.inline import deploy, get_server_app, show_plotly, get_widget_html
    >>> from fastapi.responses import HTMLResponse
    >>> import plotly.express as px
    >>>
    >>> app = get_server_app()
    >>>
    >>> @app.get("/chart")
    >>> def chart():
    ...     fig = px.bar(x=[1, 2, 3], y=[4, 5, 6])
    ...     widget = show_plotly(fig)  # Headless mode auto-detected
    ...     html = get_widget_html(widget.label)
    ...     return HTMLResponse(html)
    >>>
    >>> deploy()

    Or via pywry.toml:

    >>> # pywry.toml:
    >>> # [server]
    >>> # host = "0.0.0.0"
    >>> # port = 8080
    >>> # log_level = "info"
    """
    from pywry.config import get_settings  # pylint: disable=redefined-outer-name

    settings = get_settings()
    server = settings.server

    # Set headless mode to skip browser.open() calls in widget creation
    os.environ["PYWRY_HEADLESS"] = "1"

    # Configure server state for widget URL generation from config
    _state.port = server.port
    _state.host = server.host

    # Get/create the FastAPI app
    app = _get_app()

    # Start callback processor thread for handling events from JavaScript
    callback_thread = threading.Thread(target=_process_callbacks, daemon=True)
    callback_thread.start()

    # Build uvicorn config from central settings
    config_kwargs: dict[str, Any] = {
        "app": app,
        "host": server.host,
        "port": server.port,
        "log_level": server.log_level,
        "access_log": server.access_log,
        "timeout_keep_alive": server.timeout_keep_alive,
        "backlog": server.backlog,
    }

    # Optional settings
    if server.reload:
        config_kwargs["reload"] = True
    if server.workers > 1:
        config_kwargs["workers"] = server.workers
    if server.ssl_certfile:
        config_kwargs["ssl_certfile"] = server.ssl_certfile
    if server.ssl_keyfile:
        config_kwargs["ssl_keyfile"] = server.ssl_keyfile
    if server.ssl_keyfile_password:
        config_kwargs["ssl_keyfile_password"] = server.ssl_keyfile_password
    if server.ssl_ca_certs:
        config_kwargs["ssl_ca_certs"] = server.ssl_ca_certs
    if server.timeout_graceful_shutdown is not None:
        config_kwargs["timeout_graceful_shutdown"] = server.timeout_graceful_shutdown
    if server.limit_concurrency is not None:
        config_kwargs["limit_concurrency"] = server.limit_concurrency
    if server.limit_max_requests is not None:
        config_kwargs["limit_max_requests"] = server.limit_max_requests

    # Run the server (blocking)
    # If a server is already running (e.g., from widget creation), stop it first
    if _state.server_thread is not None and _state.server_thread.is_alive():
        stop_server(timeout=2.0)

    uvicorn.run(**config_kwargs)


def get_server_app() -> FastAPI:
    """Get the FastAPI app configured for server deployment.

    Use this to add custom routes before calling deploy().
    All configuration is read from the central configuration system.

    Configuration is loaded from (in order of precedence):
    1. Built-in defaults
    2. pyproject.toml [tool.pywry] section
    3. ./pywry.toml (project-level)
    4. ~/.config/pywry/config.toml (user-level)
    5. Environment variables with PYWRY_SERVER__ prefix

    Returns
    -------
    FastAPI
        The configured FastAPI application with PyWry routes.

    Examples
    --------
    >>> # Configure via environment or pywry.toml:
    >>> # export PYWRY_SERVER__HOST=0.0.0.0
    >>> # export PYWRY_SERVER__PORT=8080
    >>> # export PYWRY_SERVER__WIDGET_PREFIX=/charts
    >>>
    >>> from pywry.inline import get_server_app, deploy, show_plotly, get_widget_html
    >>> from fastapi.responses import HTMLResponse
    >>> import plotly.express as px
    >>>
    >>> app = get_server_app()
    >>>
    >>> @app.get("/")
    >>> def index():
    ...     return {"routes": ["/sales", "/inventory"]}
    >>>
    >>> @app.get("/sales")
    >>> def sales():
    ...     fig = px.bar(x=["Jan", "Feb"], y=[100, 150])
    ...     widget = show_plotly(fig)  # Headless mode auto-detected
    ...     html = get_widget_html(widget.label)
    ...     return HTMLResponse(html)
    >>>
    >>> if __name__ == "__main__":
    ...     deploy()
    """
    from pywry.config import get_settings  # pylint: disable=redefined-outer-name

    settings = get_settings()
    server = settings.server

    # Set headless mode
    os.environ["PYWRY_HEADLESS"] = "1"

    # Configure state for URL generation from config
    _state.port = server.port
    _state.host = server.host
    _state.widget_prefix = server.widget_prefix.rstrip("/")

    return _get_app()


def get_widget_url(widget_id: str) -> str:
    """Get the URL path for a widget using the configured prefix.

    Use this instead of hardcoding "/widget/{id}" to respect the
    user's configured widget_prefix setting.

    Parameters
    ----------
    widget_id : str
        The widget ID (from widget.label or widget.widget_id).

    Returns
    -------
    str
        The URL path (e.g., "/widget/abc123" or "/charts/abc123").

    Examples
    --------
    >>> from pywry.inline import show_plotly, get_widget_url
    >>> import plotly.express as px
    >>>
    >>> fig = px.bar(x=["A", "B"], y=[1, 2])
    >>> widget = show_plotly(fig)
    >>> url = get_widget_url(widget.label)  # "/widget/abc123"
    >>> return RedirectResponse(url)
    """
    prefix = _state.widget_prefix or "/widget"
    return f"{prefix}/{widget_id}"


def get_widget_html(widget_id: str) -> str | None:
    """Get the HTML content for a widget by ID.

    Use this to serve widget content directly at your own routes
    without redirecting to the widget URL (keeping clean URLs).

    Parameters
    ----------
    widget_id : str
        The widget ID (from widget.label or widget.widget_id).

    Returns
    -------
    str | None
        The widget HTML content, or None if widget not found.

    Examples
    --------
    >>> from fastapi.responses import HTMLResponse
    >>> from pywry.inline import show, get_widget_html
    >>>
    >>> # Register widget once at startup
    >>> show("<h1>Hello</h1>", widget_id="home", open_browser=False)
    >>>
    >>> @app.get("/home")
    >>> async def home():
    ...     html = get_widget_html("home")
    ...     if html:
    ...         return HTMLResponse(html)
    ...     return HTMLResponse("<h1>Not found</h1>", status_code=404)
    """
    return _state.get_widget_html(widget_id)


async def get_widget_html_async(widget_id: str) -> str | None:
    """Get the HTML content for a widget by ID (async version).

    Use this in async route handlers to avoid deadlock issues with
    deploy mode's async state stores (e.g., Redis).

    Parameters
    ----------
    widget_id : str
        The widget ID (from widget.label or widget.widget_id).

    Returns
    -------
    str | None
        The widget HTML content, or None if widget not found.

    Examples
    --------
    >>> from fastapi.responses import HTMLResponse
    >>> from pywry.inline import show, get_widget_html_async
    >>>
    >>> # Register widget once at startup
    >>> show("<h1>Hello</h1>", widget_id="home", open_browser=False)
    >>>
    >>> @app.get("/home")
    >>> async def home():
    ...     html = await get_widget_html_async("home")
    ...     if html:
    ...         return HTMLResponse(html)
    ...     return HTMLResponse("<h1>Not found</h1>", status_code=404)
    """
    return await _state.get_widget_html_async(widget_id)


class InlineWidget(GridStateMixin, PlotlyStateMixin, ToolbarStateMixin):
    """Base inline widget that renders via FastAPI server and IFrame.

    Implements BaseWidget protocol for unified API across rendering backends.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        html: str,
        callbacks: dict[str, Callable[..., Any]] | None = None,
        width: str = "100%",
        height: int = 500,
        port: int | None = None,
        widget_id: str | None = None,
        headers: dict[str, str] | None = None,
        auth: Any | None = None,
        browser_only: bool = False,
        token: str | None = None,
    ) -> None:
        super().__init__()
        if not HAS_FASTAPI:
            raise ImportError("fastapi and uvicorn required: pip install fastapi uvicorn")

        # For browser_only mode, we don't need IPython (just the server + browser)
        self._browser_only = browser_only
        if not browser_only and not HAS_IPYTHON:
            raise ImportError("IPython required for notebook display")

        settings = get_settings().server

        self._widget_id = widget_id or uuid.uuid4().hex
        # Generate token if not provided and token auth is required
        self._token = token if token is not None else _generate_widget_token(self._widget_id)
        self._width = width
        self._height = height
        self._port = port or settings.port
        self._host = settings.host
        self._protocol = "https" if settings.ssl_certfile else "http"
        self._callbacks = callbacks or {}

        self._headers = headers or {}
        self._auth = auth

        # Create an Output widget to capture callback output in the correct cell
        # (only if IPython is available, otherwise None for browser-only mode)
        self._output = Output() if HAS_IPYTHON else None

        # Register widget with proper state management (handles both memory and Redis backends)
        _state.register_widget(
            widget_id=self._widget_id,
            html=html,
            callbacks=self._callbacks,
            output=self._output,
            token=self._token,
        )

        # Check if server is already running (e.g., after kernel restart)
        server_already_running = False
        try:
            response = _make_server_request(
                "GET",
                "/health",
                port=self._port,
                host=self._host,
                timeout=0.5,
                headers=self._headers,
                auth=self._auth,
            )
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
                response = _make_server_request(
                    "POST",
                    "/register_widget",
                    port=self._port,
                    host=self._host,
                    json_data={"widget_id": self._widget_id, "html": html},
                    timeout=1.0,
                    headers=self._headers,
                    auth=self._auth,
                )
                if response.status_code == 200:
                    pass
            except Exception:  # noqa: S110
                # If registration fails, fall back to starting new server
                pass

        # Start server if not already running
        # Note: is_headless() only affects browser opening, not server startup
        # The server is needed for widget communication even in headless/test mode
        _start_server(self._port, self._host)

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
    def label(self) -> str:
        """Get the widget label (alias for widget_id for BaseWidget protocol consistency)."""
        return self._widget_id

    @property
    def output(self) -> Output:
        """Get the Output widget for callback output."""
        return self._output

    @property
    def url(self) -> str:
        """Get the widget URL using configured prefix."""
        return (
            f"{self._protocol}://{self._host}:{self._port}{_state.widget_prefix}/{self._widget_id}"
        )

    def open_in_browser(self) -> None:
        """Open the chart in a new browser tab."""
        import webbrowser

        # Ensure server is fully ready before opening browser
        for _ in range(20):
            try:
                response = _make_server_request(
                    "GET", "/health", host=self._host, port=self._port, timeout=0.2
                )
                if response.status_code == 200:
                    break
            except Exception:  # noqa: S110
                pass
            time.sleep(0.1)

        print(f"[PyWry] Opening browser: {self.url}")
        webbrowser.open(self.url)

    def on(
        self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
    ) -> InlineWidget:
        """Register a callback for events from JavaScript.

        Parameters
        ----------
        event_type : str
            Event name (e.g., 'plotly:click', 'toggle', 'grid:cell-click').
        callback : Callable[[dict[str, Any], str, str], Any]
            Handler function receiving (data, event_type, label).

        Returns
        -------
        InlineWidget
            Self for method chaining.
        """
        from .state import is_deploy_mode

        self._callbacks[event_type] = callback

        if is_deploy_mode():
            from .state import run_async

            # In deploy mode, update local widgets and callback registry
            if self._widget_id in _state.local_widgets:
                _state.local_widgets[self._widget_id]["callbacks"] = self._callbacks
            registry = _state.get_callback_registry()
            run_async(registry.register(self._widget_id, event_type, callback))
        else:
            # Local mode: update widgets dict
            if self._widget_id in _state.widgets:
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

    def alert(
        self,
        message: str,
        alert_type: str = "info",
        title: str | None = None,
        duration: int | None = None,
        callback_event: str | None = None,
        position: str = "top-right",
    ) -> None:
        """Show a toast notification.

        Parameters
        ----------
        message : str
            The message to display.
        alert_type : str
            Alert type: 'info', 'success', 'warning', 'error', or 'confirm'.
        title : str, optional
            Optional title for the toast.
        duration : int, optional
            Auto-dismiss duration in ms. Defaults based on type.
        callback_event : str, optional
            Event name to emit when confirm dialog is answered.
        position : str
            Toast position: 'top-right', 'top-left', 'bottom-right', 'bottom-left'.
        """
        payload: dict[str, Any] = {"message": message, "type": alert_type, "position": position}
        if title is not None:
            payload["title"] = title
        if duration is not None:
            payload["duration"] = duration
        if callback_event is not None:
            payload["callback_event"] = callback_event
        self.emit("pywry:alert", payload)

    def update(self, html: str) -> None:
        """Update the widget's HTML content.

        Parameters
        ----------
        html : str
            New HTML content to render. Should include necessary <script> tags.
        """
        _state.widgets[self._widget_id]["html"] = html

        # Send update event to JavaScript to refresh the IFrame content
        self.emit("pywry:update-html", {"html": html})

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
        url = f"{self.url}?ts={uuid.uuid4().hex}"

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
        url = f"{self.url}?ts={uuid.uuid4().hex}"

        # Display IFrame directly using IPython's class to avoid warnings
        ipy_display(IFrame(url, width=self._width, height=self._height))

        # Display Output widget below it for callback output
        if self._output:
            ipy_display(self._output)

    def update_figure(
        self,
        figure: Figure | dict[str, Any],
        chart_id: str | None = None,
        animate: bool = False,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Update the Plotly figure without manual HTML generation.

        Parameters
        ----------
        figure : plotly.graph_objects.Figure
            New Plotly figure to display.
        chart_id : str, optional
            Chart ID (if applicable, though here largely for Mixin compat/future).
        animate : bool, optional
            Whether to animate the update.
        config : dict, optional
            Configuration dictionary.

        Examples
        --------
        >>> widget.update_figure(new_fig)  # Clean API!
        """
        # Convert figure to dict
        fig_dict = _normalize_figure(figure)
        stored_config = getattr(self, "_plotly_config", None)

        # Resolve config - could be Pydantic model, dict, or None
        final_config: dict[str, Any] = {}
        cfg = config or stored_config
        if cfg is not None:
            if hasattr(cfg, "model_dump"):
                # Pydantic model - convert to dict with camelCase aliases
                final_config = cfg.model_dump(by_alias=True, exclude_none=True)
            elif isinstance(cfg, dict):
                final_config = cfg
            else:
                final_config = {}

        # NOTE: For InlineWidget, we send an update event for the partial plot update.
        # This keeps the rest of the page (including toolbar) intact.
        # If we wanted to replace the toolbar, we'd need to reload the whole HTML.
        # For full replacement, see update_html.

        # Send update via Plotly.react (no page reload needed)
        self.emit(
            "plotly:update-figure",
            {
                "figure": fig_dict,
                "config": final_config,
                "chartId": chart_id,
                "animate": animate,
            },
        )

    def update_cell(
        self,
        row_id: str | int,
        col_id: str,
        value: Any,
        grid_id: str | None = None,
    ) -> None:
        """Update a single cell value."""
        self.emit(
            "grid:update-cell",
            {"rowId": row_id, "colId": col_id, "value": value, "gridId": grid_id},
        )

    def update_data(
        self,
        data: list[dict[str, Any]],
        grid_id: str | None = None,
        strategy: str = "set",
    ) -> None:
        """Update grid data rows."""
        self.emit(
            "grid:update-data",
            {"data": data, "gridId": grid_id, "strategy": strategy},
        )

    def update_columns(
        self,
        column_defs: list[dict[str, Any]],
        grid_id: str | None = None,
    ) -> None:
        """Update the grid's column definitions.

        Parameters
        ----------
        column_defs : list of dict
            New column definitions.
        grid_id : str, optional
            Grid ID to update.
        """
        self.emit(
            "grid:update-columns",
            {"columnDefs": column_defs, "gridId": grid_id},
        )

    def update_grid(
        self,
        data: list[dict[str, Any]] | Any | None = None,
        columns: list[dict[str, Any]] | None = None,
        restore_state: dict[str, Any] | None = None,
        grid_id: str | None = None,
    ) -> None:
        """Update grid with new data, columns, and/or restore saved state."""
        payload: dict[str, Any] = {}
        if data is not None:
            if hasattr(data, "to_dict") and hasattr(data, "columns"):
                payload["data"] = data.to_dict(orient="records")
            else:
                payload["data"] = data
        if columns is not None:
            payload["columnDefs"] = columns
        if restore_state is not None:
            payload["restoreState"] = restore_state
        if grid_id:
            payload["gridId"] = grid_id
        self.emit("grid:update-grid", payload)

    def request_grid_state(
        self, context: dict[str, Any] | None = None, grid_id: str | None = None
    ) -> None:
        """Request the grid's current state.

        The grid will emit a 'grid:state-response' event with the state data.
        Register a callback for 'grid:state-response' to receive the state.

        Parameters
        ----------
        grid_id : str, optional
            Grid ID to query.
        context : dict, optional
            Additional context to include in the response.
        """
        payload: dict[str, Any] = {}
        if grid_id:
            payload["gridId"] = grid_id
        if context:
            payload["context"] = context
        self.emit("grid:request-state", payload)

    def restore_state(self, state: dict[str, Any], grid_id: str | None = None) -> None:
        """Restore a previously saved grid state.

        Parameters
        ----------
        state : dict
            State object from a previous 'grid:state-response' event.
        grid_id : str, optional
            Grid ID to restore state to.
        """
        self.emit(
            "grid:restore-state",
            {"state": state, "gridId": grid_id},
        )

    def reset_state(self, grid_id: str | None = None, hard: bool = False) -> None:
        """Reset grid to its default state.

        Clears all column customizations (width, order, visibility, pinning)
        and removes all filters.

        Parameters
        ----------
        grid_id : str, optional
            Grid ID to reset.
        hard : bool, optional
            If True, perform a hard reset.
        """
        self.emit("grid:reset-state", {"gridId": grid_id, "hard": hard})

    # =========================================================================
    # Toolbar State Methods
    # =========================================================================

    def request_toolbar_state(
        self, toolbar_id: str | None = None, context: dict[str, Any] | None = None
    ) -> None:
        """Request the current state of toolbar components.

        The widget will emit a 'toolbar:state-response' event with the state data.
        Register a callback for 'toolbar:state-response' to receive the state.

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
        >>> widget.on("toolbar:state-response", on_state)
        >>> widget.request_toolbar_state()
        """
        payload: dict[str, Any] = {}
        if toolbar_id:
            payload["toolbarId"] = toolbar_id
        if context:
            payload["context"] = context
        self.emit("toolbar:request-state", payload)

    def get_toolbar_value(self, component_id: str, context: dict[str, Any] | None = None) -> None:
        """Request the current value of a specific toolbar component.

        The widget will emit a 'toolbar:state-response' event with the value.
        Register a callback for 'toolbar:state-response' to receive it.

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
        >>> widget.on("toolbar:state-response", on_value)
        >>> widget.get_toolbar_value("my-select")
        """
        payload: dict[str, Any] = {"componentId": component_id}
        if context:
            payload["context"] = context
        self.emit("toolbar:request-state", payload)

    def set_toolbar_value(
        self, component_id: str, value: Any, toolbar_id: str | None = None
    ) -> None:
        """Set the value of a specific toolbar component.

        Parameters
        ----------
        component_id : str
            The component_id of the toolbar item to update.
        value : Any
            The new value for the component.
        toolbar_id : str, optional
            The toolbar ID (if applicable).
        """
        self.emit(
            "toolbar:set-value",
            {"componentId": component_id, "value": value, "toolbarId": toolbar_id},
        )

    def set_toolbar_values(self, values: dict[str, Any], toolbar_id: str | None = None) -> None:
        """Set multiple toolbar component values at once.

        Parameters
        ----------
        values : dict[str, Any]
            Mapping of component_id to value.
        toolbar_id : str, optional
            The toolbar ID (if applicable).
        """
        self.emit("toolbar:set-values", {"values": values, "toolbarId": toolbar_id})

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


def show(  # pylint: disable=too-many-arguments,too-many-branches,too-many-statements
    content: str,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: ThemeLiteral | None = None,
    callbacks: dict[str, Callable[..., Any]] | None = None,
    include_plotly: bool = False,
    include_aggrid: bool = False,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    port: int | None = None,
    open_browser: bool = False,
    widget_id: str | None = None,
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
    theme : 'dark', 'light', or 'system'
        Color theme. 'system' follows browser/OS preference.
        Default: 'system' in headless/server mode, 'dark' in desktop mode.
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
    open_browser : bool, optional
        If True, open in system browser instead of displaying IFrame in notebook.
        Used by BROWSER mode. Default: False.
    widget_id : str, optional
        Custom widget ID for stable URL routing. If not provided, a random UUID is generated.

    Returns
    -------
    InlineWidget
        Widget instance for registering additional callbacks.
    """
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    widget_id = widget_id or uuid.uuid4().hex

    # Wrap content with toolbars using the centralized function
    content = wrap_content_with_toolbars(content, toolbars)

    # Build head with optional libraries
    pywry_css = get_pywry_css()
    toast_css = get_toast_css()
    head_parts = [
        '<meta charset="utf-8">',
        f"<title>{title}</title>",
        f"<style>{pywry_css}</style>" if pywry_css else "",
        f"<style>{toast_css}</style>" if toast_css else "",
        """<style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html, body {
                height: 100%;
                width: 100%;
                overflow: hidden;
            }
            body {
                display: flex;
                flex-direction: column;
            }
            .pywry-widget {
                --pywry-widget-width: 100%;
                --pywry-widget-height: 100%;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                background: var(--pywry-bg-primary);
                color: var(--pywry-text-primary);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                position: relative;
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

    # Include toolbar script if toolbars are present
    toolbar_script = ""
    if toolbars:
        toolbar_script = f"<script>{get_toolbar_script(with_script_tag=False)}</script>"

    # Determine widget theme class based on theme
    if theme == "system":
        widget_theme_class = (
            "pywry-theme-system pywry-theme-dark"  # Default to dark, JS will update
        )
    elif theme == "light":
        widget_theme_class = "pywry-theme-light"
    else:
        widget_theme_class = "pywry-theme-dark"

    # Also set html class for CSS variable inheritance
    html_theme_class = "light" if theme == "light" else "dark"

    # Generate widget token FIRST - this will be stored with the widget
    widget_token = _generate_widget_token(widget_id)

    # Build full HTML - bridge MUST be in head so window.pywry exists before user scripts run
    # Note: wrap_content_with_toolbars already wraps content in pywry-content div
    html = f"""<!DOCTYPE html>
<html class="{html_theme_class}">
<head>
    {"".join(head_parts)}
    {_get_pywry_bridge_js(widget_id, widget_token)}
    {toolbar_script}
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {content}
    </div>
    <script>
        // System theme detection - follows browser/OS preference
        (function() {{
            const widgetEl = document.querySelector('.pywry-widget');
            if (widgetEl && widgetEl.classList.contains('pywry-theme-system')) {{
                function applySystemTheme() {{
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                    widgetEl.classList.add(prefersDark ? 'pywry-theme-dark' : 'pywry-theme-light');
                    document.documentElement.classList.remove('dark', 'light');
                    document.documentElement.classList.add(prefersDark ? 'dark' : 'light');
                }}
                applySystemTheme();
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applySystemTheme);
            }}
        }})();
    </script>
</body>
</html>"""

    widget = InlineWidget(
        html,
        callbacks=callbacks,
        width=width,
        height=height,
        port=port,
        widget_id=widget_id,
        token=widget_token,
    )

    # Display - either open in browser or show IFrame
    # Skip display entirely in headless mode (PYWRY_HEADLESS=1) for server deployments
    if is_headless():
        pass  # Server mode: widget is registered, no display needed
    elif open_browser:
        widget.open_in_browser()
    else:
        widget.display()  # Jupyter notebook mode: show IFrame
    return widget


def generate_plotly_html(
    figure_json: str,
    widget_id: str,
    title: str = "PyWry",
    theme: ThemeLiteral | None = None,
    full_document: bool = True,
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    token: str | None = None,
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
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    plotly_js = get_plotly_js()
    plotly_script = (
        f"<script>{plotly_js}</script>"
        if plotly_js
        else '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
    )

    # Include Plotly templates (plotly_dark, plotly_white, etc.) for theme switching
    templates_js = get_plotly_templates_js()
    templates_script = f"<script>{templates_js}</script>" if templates_js else ""

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
        // Also generate click handlers for buttons with 'event' property
        if (plotlyConfig.modeBarButtonsToAdd) {{
            plotlyConfig.modeBarButtonsToAdd = plotlyConfig.modeBarButtonsToAdd.map(function(btn) {{
                // If button has 'event' but no 'click', generate a click handler
                if (btn.event && !btn.click) {{
                    const eventName = btn.event;
                    const eventData = btn.data || {{}};
                    btn.click = function(gd) {{
                        window.pywry.emit(eventName, eventData);
                    }};
                }} else if (btn.click && typeof btn.click === 'string') {{
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
            window.pywry.on('plotly:update-figure', function(data) {{
                const chartEl = document.getElementById('chart');
                if (chartEl && data.figure) {{
                    const figData = data.figure;
                    const config = data.config || {{}};
                    // Process modebar button click handlers
                    if (config.modeBarButtonsToAdd) {{
                        config.modeBarButtonsToAdd = config.modeBarButtonsToAdd.map(function(btn) {{
                            // If button has 'event' but no 'click', generate a click handler
                            if (btn.event && !btn.click) {{
                                const eventName = btn.event;
                                const eventData = btn.data || {{}};
                                btn.click = function(gd) {{
                                    window.pywry.emit(eventName, eventData);
                                }};
                            }} else if (typeof btn.click === 'string') {{
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

            // Register handler for layout updates (partial updates like axis type, title, etc.)
            window.pywry.on('plotly:update-layout', function(data) {{
                const chartEl = document.getElementById('chart');
                if (chartEl) {{
                    const layout = data.layout || {{}};
                    PlotlyLib.relayout(chartEl, layout);
                }}
            }});

            PlotlyLib.newPlot('chart', figData.data, figData.layout, finalConfig).then(function() {{
        const chartEl = document.getElementById('chart');

        // Extract point data - include all primitive values and simple arrays
        function extractPointData(p) {{
            const point = {{}};
            for (const key in p) {{
                if (!Object.prototype.hasOwnProperty.call(p, key)) continue;
                if (key.startsWith('_')) continue;  // Skip internal Plotly props
                const val = p[key];
                if (val === null || val === undefined) continue;
                // Include primitives (string, number, boolean)
                if (typeof val !== 'object' && typeof val !== 'function') {{
                    point[key] = val;
                }}
                // Include simple arrays (customdata, etc) but not nested objects
                else if (Array.isArray(val) && val.length < 50) {{
                    point[key] = val;
                }}
            }}
            return point;
        }}

        chartEl.on('plotly_click', function(data) {{
            const points = data.points.map(extractPointData);
            window.pywry.emit('plotly_click', {{ points: points }});
        }});

        chartEl.on('plotly_hover', function(data) {{
            const points = data.points.map(extractPointData);
            window.pywry.emit('plotly_hover', {{ points: points }});
        }});

        chartEl.on('plotly_selected', function(data) {{
            if (data) {{
                const points = data.points.map(extractPointData);
                window.pywry.emit('plotly_selected', {{ points: points, range: data.range }});
            }}
        }});
    }});
        }});
    }})();
</script>"""

    pywry_css = get_pywry_css()
    toast_css = get_toast_css()
    pywry_style = f"<style>{pywry_css}</style>" if pywry_css else ""
    toast_style = f"<style>{toast_css}</style>" if toast_css else ""

    # Determine widget theme class - "system" follows browser preferences
    if theme == "system":
        widget_theme_class = "pywry-theme-system"
    elif theme == "dark":
        widget_theme_class = "pywry-theme-dark"
    else:
        widget_theme_class = "pywry-theme-light"

    # For anywidget: content fragment WITHOUT pywry bridge (widget provides it)
    # For IFrame: full document WITH pywry bridge
    if not full_document:
        # Content fragment for anywidget - return just the chart div
        # Caller (create_plotly_widget) will handle toolbar wrapping
        chart_div = '<div id="chart" class="pywry-plotly"></div>'
        wrapped_content = wrap_content_with_toolbars(chart_div, toolbars) if toolbars else chart_div
        return f"""{wrapped_content}
{plotly_handlers_script}"""

    # Build wrapper structure for toolbars using centralized function
    chart_div = '<div id="chart" class="pywry-plotly"></div>'
    widget_content = wrap_content_with_toolbars(chart_div, toolbars)

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
    {toast_style}
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
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            border: none;
            border-radius: 0;
            box-sizing: border-box;
            /* Match toolbar background */
            background-color: var(--pywry-bg-primary);
        }}
        /* Remove toolbar borders in IFrame context */
        .pywry-toolbar {{
            border: none;
        }}
        .pywry-content {{
            flex: 1;
            min-height: 0;
            padding: 16px;
            box-sizing: border-box;
        }}
        #chart {{
            flex: 1;
            min-height: 0;
            position: relative;
            box-sizing: border-box;
            border: 1px solid var(--pywry-border-color, #333);
            border-radius: var(--pywry-radius, 4px);
            overflow: hidden;
        }}
        /* Ensure modebar never causes scrollbars */
        .modebar-container {{
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
        }}
        .js-plotly-plot, .plot-container, .plotly {{
            width: 100% !important;
            height: 100% !important;
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
    </style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id, token)}
    {plotly_handlers_script}
    <script>
        // System theme detection - follows browser/OS preference
        (function() {{
            const widgetEl = document.querySelector('.pywry-widget');
            if (widgetEl && widgetEl.classList.contains('pywry-theme-system')) {{
                function applySystemTheme() {{
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                    widgetEl.classList.add(prefersDark ? 'pywry-theme-dark' : 'pywry-theme-light');
                    document.documentElement.classList.remove('dark', 'light');
                    document.documentElement.classList.add(prefersDark ? 'dark' : 'light');

                    // Update Plotly if present
                    const plotDiv = document.querySelector('.js-plotly-plot');
                    if (plotDiv && window.Plotly && plotDiv.data) {{
                        const templateName = prefersDark ? 'plotly_dark' : 'plotly_white';
                        const template = window.PYWRY_PLOTLY_TEMPLATES?.[templateName];
                        if (template) {{
                            const newLayout = Object.assign({{}}, plotDiv.layout || {{}}, {{ template: template }});
                            window.Plotly.newPlot(plotDiv, plotDiv.data, newLayout, plotDiv._fullLayout?._config || {{}});
                        }}
                    }}
                }}
                applySystemTheme();
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applySystemTheme);
            }}
        }})();
    </script>
    <script>
        // Listen for theme updates (background/container AND Plotly figure)
        window.pywry.on('pywry:update-theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;

            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            // Update HTML class FIRST (this controls CSS variables)
            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            // Update widget class
            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}

            // Update ALL toolbar elements (they're part of the same document in browser mode!)
            document.querySelectorAll('.pywry-toolbar').forEach(function(toolbar) {{
                toolbar.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                toolbar.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Update all wrapper elements
            document.querySelectorAll('[class*="pywry-wrapper"]').forEach(function(wrapper) {{
                wrapper.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                wrapper.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Force browser to recompute styles before reading CSS variable
            void htmlEl.offsetHeight;

            // Read background from CSS variable (now properly set by html.light or html.dark)
            const bgColor = getComputedStyle(htmlEl).getPropertyValue('--pywry-bg-primary').trim();
            if (bgColor) {{
                bodyEl.style.backgroundColor = bgColor;
                if (widgetEl) {{
                    widgetEl.style.backgroundColor = bgColor;
                }}
            }}

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

            console.log('[PyWry Plotly IFrame] Theme updated, isLight:', isLight, 'bgColor:', bgColor);
        }});

        {get_toolbar_script(with_script_tag=False)}
    </script>
</body>
</html>"""


def show_plotly(
    figure: Figure,
    callbacks: dict[str, Callable[..., Any]] | None = None,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: ThemeLiteral | None = None,
    port: int | None = None,
    config: dict[str, Any] | PlotlyConfig | None = None,
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    open_browser: bool = False,
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
    open_browser : bool, optional
        If True, open in system browser instead of displaying IFrame in notebook.
        Used by BROWSER mode. Default: False.

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
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    from .notebook import create_plotly_widget
    from .plotly_config import PlotlyConfig

    widget_id = uuid.uuid4().hex

    # Convert figure to dict and merge config
    fig_dict = json.loads(figure.to_json())

    # Apply default PlotlyConfig if none provided (hides logo, etc.)
    final_config: dict[str, Any] | PlotlyConfig = config if config is not None else PlotlyConfig()

    # Handle PlotlyConfig Pydantic model or dict
    if hasattr(final_config, "model_dump"):
        # Pydantic model - convert to dict with camelCase aliases
        config_dict = final_config.model_dump(by_alias=True, exclude_none=True)
    elif isinstance(final_config, dict):
        config_dict = final_config
    else:
        config_dict = {}
    fig_dict["config"] = config_dict

    fig_json = json.dumps(fig_dict)

    # Create widget using auto-backend selection
    # Force InlineWidget (IFrame) for BROWSER mode since it has open_in_browser()
    widget = create_plotly_widget(
        figure_json=fig_json,
        widget_id=widget_id,
        title=title,
        theme=theme,
        width=width,
        height=height,
        port=port,
        toolbars=toolbars,
        force_iframe=open_browser,
    )

    # Store config and toolbars for updates
    widget._plotly_config = config  # pylint: disable=attribute-defined-outside-init
    widget._toolbars = toolbars  # pylint: disable=attribute-defined-outside-init

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display - either open in browser or show IFrame
    # Skip display entirely in headless mode (PYWRY_HEADLESS=1) for server deployments
    if is_headless():
        pass  # Server mode: widget is registered, no display needed
    elif open_browser:
        widget.open_in_browser()
    else:
        widget.display()  # Jupyter notebook mode: show IFrame
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
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 0;
    padding: 0;
    background-color: var(--pywry-bg-primary);
}
.pywry-content {
    width: 100%;
    height: 100%;
}
.pywry-toolbar {
    border: none;
}
.pywry-grid {
    height: 100%;
    width: 100%;
}
/* Hide AG Grid watermark/license message */
.ag-watermark {
    display: none !important;
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
    toast_css = get_toast_css()

    return {
        "script": (
            f"<script>{aggrid_js}</script>"
            if aggrid_js
            else '<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@35.0.0/dist/ag-grid-community.min.js"></script>'
        ),
        "defaults_script": f"<script>{aggrid_defaults_js}</script>" if aggrid_defaults_js else "",
        "style": f"<style>{aggrid_css}</style>" if aggrid_css else "",
        "pywry_style": f"<style>{pywry_css}</style>" if pywry_css else "",
        "toast_style": f"<style>{toast_css}</style>" if toast_css else "",
    }


def _build_grid_layout(
    theme_class: str,
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    extra_top_html: str = "",
) -> str:
    """Build grid layout with toolbars.

    Parameters
    ----------
    theme_class : str
        AG Grid theme class.
    toolbars : list
        List of toolbar configurations (Toolbar models or dicts).
    extra_top_html : str
        Custom header HTML to prepend to top toolbar area.

    Returns
    -------
    str
        The complete layout HTML.
    """
    grid_div = f"<div id='grid' class='pywry-grid {theme_class}'></div>"
    return wrap_content_with_toolbars(grid_div, toolbars, extra_top_html)


def generate_dataframe_html(
    row_data: list[dict[str, Any]],
    columns: list[str],
    widget_id: str,
    title: str = "PyWry",
    theme: ThemeLiteral | None = None,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    grid_options: dict[str, Any] | None = None,
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    token: str | None = None,
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
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    # For "system" theme, use dark mode CSS assets (JS will switch dynamically)
    theme_mode = ThemeMode.DARK if theme in ("dark", "system") else ThemeMode.LIGHT

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
    # For system theme, default to dark AG Grid theme (JS will switch)
    theme_class = f"ag-theme-{aggrid_theme}{'-dark' if theme in ('dark', 'system') else ''}"
    widget_theme_class = f"pywry-theme-{theme}"
    widget_content = _build_grid_layout(theme_class, toolbars, header_html)

    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {assets["script"]}
    {assets["defaults_script"]}
    {assets["style"]}
    {assets["pywry_style"]}
    {assets["toast_style"]}
    <style>{_AGGRID_IFRAME_CSS}</style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id, token)}
    <script>
        const gridId = '{widget_id}';
        const gridConfig = {json.dumps(grid_config)};
        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId);
        const gridDiv = document.getElementById('grid');
        const gridApi = agGrid.createGrid(gridDiv, gridOptions);

        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
        }}

        // System theme detection - follows browser/OS preference
        (function() {{
            const widgetEl = document.querySelector('.pywry-widget');
            if (widgetEl && widgetEl.classList.contains('pywry-theme-system')) {{
                function applySystemTheme() {{
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                    widgetEl.classList.add(prefersDark ? 'pywry-theme-dark' : 'pywry-theme-light');
                    document.documentElement.classList.remove('dark', 'light');
                    document.documentElement.classList.add(prefersDark ? 'dark' : 'light');

                    // Update AG Grid theme
                    const gridDiv = document.getElementById('grid');
                    if (gridDiv) {{
                        const baseTheme = '{aggrid_theme}';
                        const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                        gridDiv.className = classes.join(' ') + ' ag-theme-' + baseTheme + (prefersDark ? '-dark' : '');
                    }}
                }}
                applySystemTheme();
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applySystemTheme);
            }}
        }})();

        window.pywry.on('pywry:update-theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;
            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            // Update HTML class FIRST (this controls CSS variables)
            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            // Update widget class
            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}

            // Update ALL toolbar elements (they're part of the same document in browser mode!)
            document.querySelectorAll('.pywry-toolbar').forEach(function(toolbar) {{
                toolbar.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                toolbar.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Update all wrapper elements
            document.querySelectorAll('[class*="pywry-wrapper"]').forEach(function(wrapper) {{
                wrapper.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                wrapper.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Force browser to recompute styles
            void htmlEl.offsetHeight;

            const bgColor = getComputedStyle(htmlEl).getPropertyValue('--pywry-bg-primary').trim();
            if (bgColor) {{
                bodyEl.style.backgroundColor = bgColor;
                if (widgetEl) {{
                    widgetEl.style.backgroundColor = bgColor;
                }}
            }}

            if (gridDiv && data.theme && data.theme.startsWith('ag-theme-')) {{
                const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                gridDiv.className = classes.join(' ') + ' ' + data.theme;
            }}
            console.log('[PyWry IFrame] Theme updated to:', data.theme, 'isLight:', isLight, 'bgColor:', bgColor);
        }});

        {get_toolbar_script(with_script_tag=False)}
    </script>
</body>
</html>"""


def generate_dataframe_html_from_config(
    config: GridConfig,
    widget_id: str,
    title: str = "PyWry",
    theme: ThemeLiteral | None = None,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    toolbars: list[dict[str, Any] | Toolbar] | None = None,
    token: str | None = None,
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
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    # For "system" theme, use dark mode CSS assets (JS will switch dynamically)
    theme_mode = ThemeMode.DARK if theme in ("dark", "system") else ThemeMode.LIGHT

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
    widget_content = _build_grid_layout(theme_class, toolbars, header_html)

    return f"""<!DOCTYPE html>
<html class="{theme}">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {assets["script"]}
    {assets["defaults_script"]}
    {assets["style"]}
    {assets["pywry_style"]}
    {assets["toast_style"]}
    <style>{_AGGRID_IFRAME_CSS}</style>
</head>
<body>
    <div class="pywry-widget {widget_theme_class}">
        {widget_content}
    </div>
    {_get_pywry_bridge_js(widget_id, token)}
    <script>
        const gridId = '{widget_id}';
        const gridConfig = {json.dumps(grid_config)};
        const gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId);
        const gridDiv = document.getElementById('grid');
        const gridApi = agGrid.createGrid(gridDiv, gridOptions);

        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
            window.PYWRY_AGGRID_REGISTER_LISTENERS(gridApi, gridDiv, gridId);
        }}

        // System theme detection - follows browser/OS preference
        (function() {{
            const widgetEl = document.querySelector('.pywry-widget');
            if (widgetEl && widgetEl.classList.contains('pywry-theme-system')) {{
                function applySystemTheme() {{
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                    widgetEl.classList.add(prefersDark ? 'pywry-theme-dark' : 'pywry-theme-light');
                    document.documentElement.classList.remove('dark', 'light');
                    document.documentElement.classList.add(prefersDark ? 'dark' : 'light');

                    // Update AG Grid theme
                    const gridDiv = document.getElementById('grid');
                    if (gridDiv) {{
                        const baseTheme = '{aggrid_theme}';
                        const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                        gridDiv.className = classes.join(' ') + ' ag-theme-' + baseTheme + (prefersDark ? '-dark' : '');
                    }}
                }}
                applySystemTheme();
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applySystemTheme);
            }}
        }})();

        window.pywry.on('pywry:update-theme', function(data) {{
            const widgetEl = document.querySelector('.pywry-widget');
            const htmlEl = document.documentElement;
            const bodyEl = document.body;
            const isDark = data.theme && data.theme.includes('dark');
            const isLight = !isDark;

            // Update HTML class FIRST (this controls CSS variables)
            htmlEl.classList.remove('dark', 'light');
            htmlEl.classList.add(isLight ? 'light' : 'dark');

            // Update widget class
            if (widgetEl) {{
                widgetEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                widgetEl.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }}

            // Update ALL toolbar elements (they're part of the same document in browser mode!)
            document.querySelectorAll('.pywry-toolbar').forEach(function(toolbar) {{
                toolbar.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                toolbar.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Update all wrapper elements
            document.querySelectorAll('[class*="pywry-wrapper"]').forEach(function(wrapper) {{
                wrapper.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                wrapper.classList.add(isLight ? 'pywry-theme-light' : 'pywry-theme-dark');
            }});

            // Force browser to recompute styles
            void htmlEl.offsetHeight;

            const bgColor = getComputedStyle(htmlEl).getPropertyValue('--pywry-bg-primary').trim();
            if (bgColor) {{
                bodyEl.style.backgroundColor = bgColor;
                if (widgetEl) {{
                    widgetEl.style.backgroundColor = bgColor;
                }}
            }}

            if (gridDiv && data.theme && data.theme.startsWith('ag-theme-')) {{
                const classes = Array.from(gridDiv.classList).filter(c => !c.startsWith('ag-theme-'));
                gridDiv.className = classes.join(' ') + ' ' + data.theme;
            }}
            console.log('[PyWry IFrame] Theme updated to:', data.theme, 'isLight:', isLight, 'bgColor:', bgColor);
        }});

        {get_toolbar_script(with_script_tag=False)}
    </script>
</body>
</html>"""


def show_dataframe(  # pylint: disable=too-many-arguments
    df: Any,
    callbacks: dict[str, Callable[..., Any]] | None = None,
    title: str = "PyWry",
    width: str = "100%",
    height: int = 500,
    theme: ThemeLiteral | None = None,
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
    header_html: str = "",
    grid_options: dict[str, Any] | None = None,
    toolbars: list[Any] | None = None,
    port: int | None = None,
    widget_id: str | None = None,
    column_defs: list[Any] | None = None,
    row_selection: Any | bool = False,
    enable_cell_span: bool | None = None,
    pagination: bool | None = None,
    pagination_page_size: int = 100,
    open_browser: bool = False,
) -> BaseWidget:
    """Show a DataFrame (or dict/list) inline in a notebook with automatic event handling.

    This function automatically wires up AG Grid events (grid:cell-click, grid:row-selected)
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
    open_browser : bool, optional
        If True, open in system browser instead of displaying IFrame in notebook.
        Used by BROWSER mode. Default: False.

    Returns
    -------
    BaseWidget
        Widget implementing BaseWidget protocol.
    """
    # Default theme based on execution mode
    if theme is None:
        theme = _get_default_theme()

    from .grid import build_grid_config
    from .notebook import create_dataframe_widget

    # Convert "system" to "dark" for grid config (grid doesn't support system theme)
    grid_theme: Literal["dark", "light"] = "dark" if theme in ("dark", "system") else "light"

    # Use unified grid config builder
    config = build_grid_config(
        data=df,
        column_defs=column_defs,
        grid_options=grid_options,
        theme=grid_theme,
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
    # Force InlineWidget (IFrame) for BROWSER mode since it has open_in_browser()
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
        force_iframe=open_browser,
    )

    # Auto-register callbacks
    if callbacks:
        for event_type, callback in callbacks.items():
            widget.on(event_type, callback)

    # Display - either open in browser or show IFrame
    # Skip display entirely in headless mode (PYWRY_HEADLESS=1) for server deployments
    if is_headless():
        pass  # Server mode: widget is registered, no display needed
    elif open_browser:
        widget.open_in_browser()
    else:
        widget.display()  # Jupyter notebook mode: show IFrame
    return widget
