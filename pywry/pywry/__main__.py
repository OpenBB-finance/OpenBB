"""PyWry subprocess entry point.

This module runs as a subprocess, handling the pytauri event loop on the main thread
and receiving commands via stdin JSON IPC.
"""

# pylint: disable=C0413,C0415,C0103
# flake8: noqa: N806,E402

import sys


# Set process and thread title for Activity Monitor/Task Manager visibility
try:
    import setproctitle

    setproctitle.setproctitle("PyWry")
    setproctitle.setthreadtitle("PyWry")
except ImportError:
    pass  # setproctitle is optional

# Set macOS process name early (before Tauri starts) so child processes inherit it

from ctypes import c_void_p


if sys.platform == "darwin":
    try:
        from ctypes import Structure, byref, c_uint32, cdll

        class _ProcessSerialNumber(Structure):
            _fields_ = [("highLongOfPSN", c_uint32), ("lowLongOfPSN", c_uint32)]  # noqa

        _Carbon = cdll.LoadLibrary("/System/Library/Frameworks/Carbon.framework/Carbon")
        _psn = _ProcessSerialNumber()
        _Carbon.GetCurrentProcess(byref(_psn))
        _Carbon.CPSSetProcessName(byref(_psn), b"PyWry")
        del _Carbon, _psn, _ProcessSerialNumber
    except (OSError, AttributeError):
        pass

import io
import json
import os
import threading

from contextlib import suppress
from pathlib import Path
from typing import Any


def _set_macos_dock_icon() -> None:
    """Set the macOS dock icon programmatically using Cocoa APIs via ctypes.

    When running as a Python subprocess (not bundled as a .app), macOS uses the
    Python interpreter's icon for the dock. This function sets it to our custom icon.
    """
    if sys.platform != "darwin":
        return

    try:
        from ctypes import cdll  # pylint: disable=redefined-outer-name

        # Load the icon file - prefer .icns
        assets_dir = Path(__file__).parent / "frontend" / "assets"
        icon_path = assets_dir / "icon.icns"
        if not icon_path.exists():
            # Fallback to .png if .icns not available
            icon_path = assets_dir / "icon.png"
            if not icon_path.exists():
                return

        # Load Cocoa frameworks
        objc = cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")
        AppKit = cdll.LoadLibrary("/System/Library/Frameworks/AppKit.framework/AppKit")

        # Set up objc_msgSend - the core Objective-C message sending function
        objc.objc_getClass.restype = c_void_p
        objc.objc_getClass.argtypes = [c_void_p]
        objc.sel_registerName.restype = c_void_p
        objc.sel_registerName.argtypes = [c_void_p]
        objc.objc_msgSend.restype = c_void_p
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p]

        # Get NSApplication.sharedApplication
        NSApplication = objc.objc_getClass(b"NSApplication")
        sel_sharedApplication = objc.sel_registerName(b"sharedApplication")
        app = objc.objc_msgSend(NSApplication, sel_sharedApplication)

        if not app:
            return

        # Create NSString with path
        NSString = objc.objc_getClass(b"NSString")
        sel_stringWithUTF8String = objc.sel_registerName(b"stringWithUTF8String:")
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p, c_void_p]
        path_str = objc.objc_msgSend(
            NSString, sel_stringWithUTF8String, str(icon_path).encode("utf-8")
        )

        if not path_str:
            return

        # Create NSImage from path
        NSImage = objc.objc_getClass(b"NSImage")
        sel_alloc = objc.sel_registerName(b"alloc")
        sel_initWithContentsOfFile = objc.sel_registerName(b"initWithContentsOfFile:")

        objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
        image = objc.objc_msgSend(NSImage, sel_alloc)
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p, c_void_p]
        image = objc.objc_msgSend(image, sel_initWithContentsOfFile, path_str)

        if not image:
            return

        # Set the application icon
        sel_setApplicationIconImage = objc.sel_registerName(b"setApplicationIconImage:")
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p, c_void_p]
        objc.objc_msgSend(app, sel_setApplicationIconImage, image)

        # Keep reference to AppKit to prevent it from being garbage collected
        _ = AppKit

    except Exception:
        # Silently ignore errors - dock icon is non-critical
        pass


# Reconfigure stdin/stdout to UTF-8 on Windows
# This is needed because Windows may default to the locale encoding (cp1252)
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from anyio import create_task_group
from anyio.from_thread import start_blocking_portal
from pytauri import Commands, Manager, RunEvent, WebviewUrl, WindowEvent
from pytauri.webview import WebviewWindowBuilder
from pytauri_plugins import dialog as dialog_plugin, fs as fs_plugin
from pytauri_wheel.lib import builder_factory, context_factory


# Debug mode controlled by environment variable
DEBUG = os.environ.get("PYWRY_DEBUG", "").lower() in ("1", "true", "yes", "on")

# Headless mode for CI testing - windows are created but not shown
HEADLESS = os.environ.get("PYWRY_HEADLESS", "").lower() in ("1", "true", "yes", "on")

# Window mode: "single", "multi", or "new"
WINDOW_MODE = os.environ.get("PYWRY_WINDOW_MODE", "new").lower()

# What happens when user clicks X in MULTI_WINDOW mode: "hide" or "close"
ON_WINDOW_CLOSE = os.environ.get("PYWRY_ON_WINDOW_CLOSE", "hide").lower()

# Lock for thread-safe stdout writes
_stdout_lock = threading.Lock()


def log(msg: str) -> None:
    """Log to stderr for debugging (only when DEBUG is enabled)."""
    if DEBUG:
        sys.stderr.write(f"[pywry] {msg}\n")
        sys.stderr.flush()


def log_error(msg: str) -> None:
    """Log error to stderr (always, regardless of DEBUG)."""
    sys.stderr.write(f"[pywry] ERROR: {msg}\n")
    sys.stderr.flush()


class JsonIPC:
    """Handle JSON IPC communication via stdin/stdout."""

    def __init__(self) -> None:
        """Initialize the IPC handler."""
        self.windows: dict[str, Any] = {}
        self.app_handle: Any = None
        self.running = True

    def send(self, msg: dict[str, Any]) -> None:
        """Send a JSON message to stdout."""
        try:
            line = json.dumps(msg)
            with _stdout_lock:
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
        except Exception as e:
            log(f"IPC send error: {e}")

    def send_ready(self) -> None:
        """Signal that the app is ready."""
        self.send({"type": "ready"})

    def send_error(self, error: str) -> None:
        """Send an error message."""
        log_error(error)
        self.send({"type": "error", "error": error})

    def send_result(self, label: str, success: bool) -> None:
        """Send a command result."""
        self.send({"type": "result", "label": label, "success": success})

    def handle_command(self, cmd: dict[str, Any]) -> None:
        """Handle an incoming command."""
        action = cmd.get("action")
        log(f"Received command: {action}")

        if action == "create":
            self.create_window(cmd)
        elif action == "set_content":
            self.set_content(cmd)
        elif action == "show":
            self.show_window(cmd)
        elif action == "hide":
            self.hide_window(cmd)
        elif action == "close":
            self.close_window(cmd)
        elif action == "emit":
            self.emit_event(cmd)
        elif action == "eval":
            self.eval_js(cmd)
        elif action == "check_open":
            self.check_window_open(cmd)
        elif action == "window_get":
            self.window_get_property(cmd)
        elif action == "window_call":
            self.window_call_method(cmd)
        elif action == "quit":
            self.quit()
        else:
            self.send_error(f"Unknown action: {action}")

    def quit(self) -> None:
        """Quit the application."""
        log("Quit command received, exiting...")
        self.running = False
        # Destroy all windows (bypasses CloseRequested handler)
        if self.app_handle:
            for label in list(self.windows.keys()):
                try:
                    window = self.windows.get(label)
                    if window:
                        window.destroy()
                except Exception:
                    pass
            # Also destroy the main window if it exists
            try:
                main_window = Manager.get_webview_window(self.app_handle, "main")
                if main_window:
                    main_window.destroy()
            except Exception:
                pass
        # Force exit the process since prevent_exit() may have been called
        log("Forcing process exit...")
        import os  # pylint: disable=redefined-outer-name,reimported

        os._exit(0)

    def create_window(self, cmd: dict[str, Any]) -> None:
        """Create a new window, or reuse existing one."""
        label = cmd.get("label", "main")
        title = cmd.get("title", "PyWry")
        width = cmd.get("width", 800)
        height = cmd.get("height", 600)

        if self.app_handle is None:
            self.send_error("App not ready")
            return

        # Check if window already exists - if so, just show it
        try:
            existing = Manager.get_webview_window(self.app_handle, label)
            if existing:
                log(f"Window '{label}' already exists, reusing it")
                self.windows[label] = existing
                if not HEADLESS:
                    existing.show()
                    existing.set_focus()
                self.send_result(label, True)
                return
        except Exception as e:
            log(f"Warning: Failed to check existing window: {e}")

        try:
            url = WebviewUrl.App(f"index.html?label={label}")
            window = WebviewWindowBuilder.build(
                self.app_handle,
                label,
                url,
                title=title,
                inner_size=(float(width), float(height)),
                visible=not HEADLESS,  # Hidden in headless mode for CI
            )
            if not HEADLESS:
                window.center()
                window.show()
                window.set_focus()
            self.windows[label] = window
            log(f"Created window '{label}' (headless={HEADLESS})")
            self.send_result(label, True)
        except Exception as e:
            self.send_error(f"Failed to create window: {e}")

    def set_content(self, cmd: dict[str, Any]) -> None:
        """Set content for a window."""
        import time

        label = cmd.get("label", "main")
        html = cmd.get("html", "")
        theme = cmd.get("theme", "dark")
        log(f"set_content for '{label}', html length: {len(html)}, theme: {theme}")

        window = self.windows.get(label)
        if window is None and self.app_handle:
            log(f"Window '{label}' not in cache, trying Manager...")
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window
                log(f"Found window '{label}' via Manager")

        if window is None:
            self.send_error(f"Window not found: {label}")
            return

        try:
            # Wait for page to load
            time.sleep(0.5)

            # Use ensure_ascii=False to preserve emoji and unicode characters
            escaped = json.dumps(html, ensure_ascii=False)
            escaped_theme = json.dumps(theme, ensure_ascii=False)

            # Inject content into #app div and execute scripts
            # Order: Theme class -> CSS -> Scripts -> Body -> Body scripts
            script = f"""
            (function() {{
                var html = {escaped};
                var theme = {escaped_theme};
                var themeClass = 'pywry-theme-' + theme;

                // Set theme class on <html> element
                var htmlEl = document.documentElement;
                htmlEl.classList.remove('pywry-theme-dark', 'pywry-theme-light');
                htmlEl.classList.add('pywry-native', themeClass);

                var app = document.getElementById('app');
                if (!app) return;

                // Extract head content
                var headMatch = html.match(/<head[^>]*>([\\s\\S]*?)<\\/head>/i);
                if (!headMatch) return;

                var headContent = headMatch[1];

                // Inject CSS
                var styleRegex = /<style[^>]*>([\\s\\S]*?)<\\/style>/gi;
                var styleMatch;
                while ((styleMatch = styleRegex.exec(headContent)) !== null) {{
                    var styleEl = document.createElement('style');
                    styleEl.textContent = styleMatch[1];
                    document.head.appendChild(styleEl);
                }}

                // Extract head scripts
                var scriptMatches = headContent.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/gi) || [];
                var headScripts = [];
                scriptMatches.forEach(function(scriptHtml) {{
                    var contentMatch = scriptHtml.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/i);
                    if (contentMatch && contentMatch[1].trim()) headScripts.push(contentMatch[1]);
                }});

                // Wait for CSS parse, then execute scripts and set content
                setTimeout(function() {{
                    headScripts.forEach(function(scriptContent) {{
                        try {{
                            var scriptEl = document.createElement('script');
                            scriptEl.textContent = scriptContent;
                            document.head.appendChild(scriptEl);
                        }} catch (e) {{ console.error('[PyWry]', e); }}
                    }});

                    // Set body content
                    var bodyMatch = html.match(/<body[^>]*>([\\s\\S]*?)<\\/body>/i);
                    app.innerHTML = bodyMatch ? bodyMatch[1] : html;

                    // Execute body scripts
                    setTimeout(function() {{
                        var scripts = app.querySelectorAll('script');
                        for (var i = 0; i < scripts.length; i++) {{
                            var oldScript = scripts[i];
                            var newScript = document.createElement('script');
                            if (oldScript.src) newScript.src = oldScript.src;
                            else newScript.textContent = oldScript.textContent;
                            oldScript.parentNode.replaceChild(newScript, oldScript);
                        }}

                        // Re-initialize toolbar handlers now that content is in DOM
                        if (typeof initToolbarHandlers === 'function' && window.pywry) {{
                            console.log('[PyWry] Re-initializing toolbar handlers after content injection');
                            initToolbarHandlers(document, window.pywry);
                        }}

                        // Notify Python that content is ready
                        if (window.pywry && window.pywry.sendEvent) {{
                            window.pywry.sendEvent('content:ready', {{ timestamp: Date.now() }});
                        }}
                    }}, 50);
                }}, 100);
            }})();
            """
            log("Calling eval with script")
            window.eval(script)
            log(f"Content set for '{label}'")
            self.send_result(label, True)
        except Exception as e:
            self.send_error(f"Failed to set content: {e}")

    def show_window(self, cmd: dict[str, Any]) -> None:
        """Show a hidden window."""
        label = cmd.get("label", "main")
        window = self.windows.get(label)

        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window

        if window:
            try:
                if not HEADLESS:
                    window.show()
                log(f"Showed window '{label}' (headless={HEADLESS})")
                self.send_result(label, True)
            except Exception as e:
                self.send_error(f"Failed to show window: {e}")
        else:
            self.send_error(f"Window not found: {label}")

    def hide_window(self, cmd: dict[str, Any]) -> None:
        """Hide a window (keeps it alive, just not visible)."""
        label = cmd.get("label", "main")
        window = self.windows.get(label)

        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window

        if window:
            try:
                if not HEADLESS:
                    window.hide()
                log(f"Hid window '{label}' (headless={HEADLESS})")
                # Notify Python side that window is hidden
                self.send(
                    {
                        "type": "event",
                        "event_type": "window:hidden",
                        "label": label,
                        "data": {},
                    }
                )
                self.send_result(label, True)
            except Exception as e:
                self.send_error(f"Failed to hide window: {e}")
        else:
            self.send_error(f"Window not found: {label}")

    def emit_event(self, cmd: dict[str, Any]) -> None:
        """Emit an event to a window.

        Uses Tauri's event system to send the event to the webview,
        which dispatches it to JavaScript handlers.
        """
        label = cmd.get("label", "main")
        event = cmd.get("event", "")
        payload = cmd.get("payload", {})

        if not event:
            self.send_error("emit: missing 'event' field")
            return

        # Handle wildcard - emit to all windows
        if label == "*":
            for window_label, window in self.windows.items():
                try:
                    self._emit_to_window(window, event, payload)
                    log(f"Emitted '{event}' to window '{window_label}'")
                except Exception as e:
                    log(f"Failed to emit to '{window_label}': {e}")
            self.send_result("*", True)
            return

        # Get specific window
        window = self.windows.get(label)
        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window

        if window is None:
            self.send_error(f"emit: Window not found: {label}")
            return

        try:
            self._emit_to_window(window, event, payload)
            log(f"Emitted '{event}' to window '{label}'")
            self.send_result(label, True)
        except Exception as e:
            self.send_error(f"emit: Failed to emit event: {e}")

    def _emit_to_window(self, window: Any, event: str, payload: dict[str, Any]) -> None:
        """Emit event to a window using JavaScript eval."""
        # Build JavaScript to dispatch the event
        # Use ensure_ascii=False to preserve emoji and unicode characters
        payload_json = json.dumps(payload, ensure_ascii=False)
        script = f"""
        (function() {{
            if (window.pywry && window.pywry.dispatch) {{
                window.pywry.dispatch({json.dumps(event, ensure_ascii=False)}, {payload_json});
            }}
        }})();
        """
        window.eval(script)

    def eval_js(self, cmd: dict[str, Any]) -> None:
        """Evaluate arbitrary JavaScript in a window without replacing content."""
        label = cmd.get("label", "main")
        script = cmd.get("script", "")

        if not script:
            self.send_error("eval: missing 'script' field")
            return

        window = self.windows.get(label)
        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window

        if window is None:
            self.send_error(f"eval: Window not found: {label}")
            return

        try:
            window.eval(script)
            log(f"Evaluated JS in window '{label}'")
            self.send_result(label, True)
        except Exception as e:
            self.send_error(f"eval: Failed to evaluate JS: {e}")

    def check_window_open(self, cmd: dict[str, Any]) -> None:
        """Check if a window is open."""
        label = cmd.get("label", "main")

        # Check cache
        window = self.windows.get(label)

        # Check manager if not in cache
        if window is None and self.app_handle:
            with suppress(Exception):
                window = Manager.get_webview_window(self.app_handle, label)

        is_open = window is not None
        log(f"check_open for '{label}': {is_open}")
        self.send({"type": "result", "label": label, "is_open": is_open})

    def close_window(self, cmd: dict[str, Any]) -> None:
        """Force-close a window (bypasses CloseRequested handler)."""
        label = cmd.get("label", "main")
        window = self.windows.pop(label, None)

        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)

        if window:
            try:
                # Use destroy() to bypass CloseRequested handler
                window.destroy()
                log(f"Destroyed window '{label}'")
                self.send_result(label, True)
            except Exception as e:
                self.send_error(f"Failed to close window: {e}")
        else:
            self.send_error(f"Window not found: {label}")

    def _get_window(self, label: str) -> Any | None:
        """Get a window by label, checking cache first then manager."""
        window = self.windows.get(label)
        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)
            if window:
                self.windows[label] = window
        return window

    def window_get_property(self, cmd: dict[str, Any]) -> None:
        """Get a window property - blocking call with response.

        Expected cmd format:
        {
            "action": "window_get",
            "label": "main",
            "property": "title",
            "request_id": "uuid-xxx"
        }

        Response format:
        {
            "type": "response",
            "request_id": "uuid-xxx",
            "success": true,
            "value": "Window Title"
        }
        or on error:
        {
            "type": "response",
            "request_id": "uuid-xxx",
            "success": false,
            "error": "error message"
        }
        """
        label = cmd.get("label", "main")
        prop = cmd.get("property", "")
        request_id = cmd.get("request_id", "")

        if not prop:
            self.send(
                {
                    "type": "response",
                    "request_id": request_id,
                    "success": False,
                    "error": "window_get: missing 'property' field",
                }
            )
            return

        window = self._get_window(label)
        if window is None:
            self.send(
                {
                    "type": "response",
                    "request_id": request_id,
                    "success": False,
                    "error": f"Window not found: {label}",
                }
            )
            return

        try:
            from .window_dispatch import get_window_property

            value = get_window_property(window, prop)
            log(f"window_get '{label}'.{prop} = {value!r}")
            self.send(
                {
                    "type": "response",
                    "request_id": request_id,
                    "success": True,
                    "value": value,
                }
            )
        except Exception as e:
            self.send(
                {
                    "type": "response",
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                }
            )

    def window_call_method(self, cmd: dict[str, Any]) -> None:
        """Call a window method - fire-and-forget or blocking.

        Expected cmd format:
        {
            "action": "window_call",
            "label": "main",
            "method": "set_title",
            "args": ["New Title"],
            "request_id": "uuid-xxx"  # Optional for fire-and-forget
        }
        """
        label = cmd.get("label", "main")
        method = cmd.get("method", "")
        args = cmd.get("args", [])
        request_id = cmd.get("request_id", "")

        if not method:
            if request_id:
                self.send(
                    {
                        "type": "response",
                        "request_id": request_id,
                        "success": False,
                        "error": "window_call: missing 'method' field",
                    }
                )
            else:
                log_error("window_call: missing 'method' field")
            return

        window = self._get_window(label)
        if window is None:
            if request_id:
                self.send(
                    {
                        "type": "response",
                        "request_id": request_id,
                        "success": False,
                        "error": f"Window not found: {label}",
                    }
                )
            else:
                log_error(f"window_call: Window not found: {label}")
            return

        try:
            from .window_dispatch import call_window_method

            result = call_window_method(window, method, args)
            log(f"window_call '{label}'.{method}({args}) = {result!r}")
            if request_id:
                self.send(
                    {
                        "type": "response",
                        "request_id": request_id,
                        "success": True,
                        "value": result,
                    }
                )
        except Exception as e:
            log_error(f"window_call '{label}'.{method} failed: {e}")
            if request_id:
                self.send(
                    {
                        "type": "response",
                        "request_id": request_id,
                        "success": False,
                        "error": str(e),
                    }
                )


def stdin_reader(ipc: JsonIPC) -> None:
    """Read commands from stdin in a separate thread."""
    log("stdin_reader started")
    try:
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue
            try:
                cmd = json.loads(line)
                ipc.handle_command(cmd)
            except json.JSONDecodeError as e:
                ipc.send_error(f"Invalid JSON: {e}")
            except Exception as e:
                ipc.send_error(f"Command error: {e}")

            if not ipc.running:
                break
    except Exception as e:
        log_error(f"stdin reader error: {e}")
    log("stdin_reader exiting")


def _handle_ready_event(ipc: JsonIPC, app_handle: Any) -> None:
    """Handle app ready event."""
    log("App ready!")

    # Set the macOS dock icon (no-op on other platforms)
    _set_macos_dock_icon()

    ipc.app_handle = app_handle
    # Get pre-configured main window
    main_window = Manager.get_webview_window(app_handle, "main")
    if main_window:
        ipc.windows["main"] = main_window
        log("Registered 'main' window")
    else:
        log("WARNING: 'main' window not found!")
    ipc.send_ready()


def _handle_close_requested(ipc: JsonIPC, app_handle: Any, label: str, window_event: Any) -> None:
    """Handle window close requested event."""
    # User clicked X - behavior depends on window mode:
    # - SINGLE_WINDOW: Always hide (reuse the window)
    # - NEW_WINDOW: Always destroy (each window is independent)
    # - MULTI_WINDOW: Use ON_WINDOW_CLOSE setting
    window_event.api.prevent_close()

    window = ipc.windows.get(label)
    if window is None:
        window = Manager.get_webview_window(app_handle, label)

    # Determine whether to destroy based on window mode
    if WINDOW_MODE == "single":
        should_destroy = False  # SINGLE_WINDOW: Always hide
    elif WINDOW_MODE == "new":
        should_destroy = True  # NEW_WINDOW: Always destroy
    else:
        should_destroy = ON_WINDOW_CLOSE == "close"  # MULTI_WINDOW: Use setting

    if should_destroy:
        log(f"CloseRequested for '{label}' - destroying")
        if window:
            window.destroy()
        if label in ipc.windows:
            del ipc.windows[label]
        ipc.send({"type": "event", "event_type": "window:closed", "label": label, "data": {}})
    else:
        log(f"CloseRequested for '{label}' - hiding")
        if window:
            window.hide()
        ipc.send({"type": "event", "event_type": "window:hidden", "label": label, "data": {}})


def main() -> int:  # pylint: disable=too-many-statements
    """Run the PyWry subprocess."""
    from .commands import register_commands

    log(f"Starting subprocess... (headless={HEADLESS})")
    src_dir = Path(__file__).parent.absolute()
    ipc = JsonIPC()
    # Start stdin reader thread
    reader_thread = threading.Thread(target=stdin_reader, args=(ipc,), daemon=True)
    reader_thread.start()

    try:
        with (
            start_blocking_portal("asyncio") as portal,
            portal.wrap_async_context_manager(portal.call(create_task_group)) as _,
        ):
            context = context_factory(src_dir)
            commands = Commands()
            register_commands(commands)

            app = builder_factory().build(
                context=context,
                invoke_handler=commands.generate_handler(portal),
                plugins=[dialog_plugin.init(), fs_plugin.init()],
            )

            def on_run(app_handle: Any, run_event: Any) -> None:
                if isinstance(run_event, RunEvent.Ready):
                    _handle_ready_event(ipc, app_handle)
                elif isinstance(run_event, RunEvent.ExitRequested):
                    # Prevent app exit when all windows are closed
                    # This keeps the subprocess alive so windows can be recreated
                    if ipc.running:
                        log("ExitRequested - preventing exit to keep subprocess alive")
                        run_event.api.prevent_exit()
                elif isinstance(run_event, RunEvent.WindowEvent):
                    window_event = run_event.event
                    label = run_event.label
                    if isinstance(window_event, WindowEvent.CloseRequested):
                        _handle_close_requested(ipc, app_handle, label, window_event)
                    elif isinstance(window_event, WindowEvent.Destroyed) and label in ipc.windows:
                        del ipc.windows[label]
                        log(f"Window '{label}' destroyed, removed from cache")

            log("Starting app.run()...")
            app.run(on_run)
    except Exception as e:
        sys.stderr.write(f"[pywry] FATAL: {e}\n")
        sys.stderr.flush()
        import traceback

        traceback.print_exc()
        return 1

    log("Subprocess exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
