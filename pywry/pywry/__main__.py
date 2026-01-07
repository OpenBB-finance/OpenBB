"""PyWry subprocess entry point.

This module runs as a subprocess, handling the pytauri event loop on the main thread
and receiving commands via stdin JSON IPC.
"""

import json
import os
import sys
import threading

from pathlib import Path
from typing import Any

from anyio import create_task_group
from anyio.from_thread import start_blocking_portal
from pytauri import Commands, Manager, RunEvent, WebviewUrl
from pytauri.webview import WebviewWindowBuilder
from pytauri_wheel.lib import builder_factory, context_factory


# Debug mode controlled by environment variable
DEBUG = os.environ.get("PYWRY_DEBUG", "").lower() in ("1", "true", "yes", "on")

# Headless mode for CI testing - windows are created but not shown
HEADLESS = os.environ.get("PYWRY_HEADLESS", "").lower() in ("1", "true", "yes", "on")


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
        elif action == "close":
            self.close_window(cmd)
        elif action == "emit":
            self.emit_event(cmd)
        elif action == "eval":
            self.eval_js(cmd)
        elif action == "quit":
            self.quit()
        else:
            self.send_error(f"Unknown action: {action}")

    def quit(self) -> None:
        """Quit the application."""
        log("Quit command received, exiting...")
        self.running = False
        # Close all windows to trigger app exit
        if self.app_handle:
            for label in list(self.windows.keys()):
                try:
                    window = self.windows.get(label)
                    if window:
                        window.close()
                except Exception:
                    pass
            # Also close the main window if it exists
            try:
                main_window = Manager.get_webview_window(self.app_handle, "main")
                if main_window:
                    main_window.close()
            except Exception:
                pass

    def create_window(self, cmd: dict[str, Any]) -> None:
        """Create a new window."""
        label = cmd.get("label", "main")
        title = cmd.get("title", "PyWry")
        width = cmd.get("width", 800)
        height = cmd.get("height", 600)

        if self.app_handle is None:
            self.send_error("App not ready")
            return

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
                window.show()
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

            escaped = json.dumps(html)
            escaped_theme = json.dumps(theme)

            # Inject content into #app div and execute scripts
            # Order: Theme class -> CSS -> Scripts -> Body -> Body scripts
            script = f"""
            (function() {{
                var html = {escaped};
                var theme = {escaped_theme};
                
                // Set theme class on <html> element
                var htmlEl = document.documentElement;
                htmlEl.classList.remove('dark', 'light');
                htmlEl.classList.add(theme);
                
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
        payload_json = json.dumps(payload)
        script = f"""
        (function() {{
            if (window.pywry && window.pywry.dispatch) {{
                window.pywry.dispatch({json.dumps(event)}, {payload_json});
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

    def close_window(self, cmd: dict[str, Any]) -> None:
        """Close a window."""
        label = cmd.get("label", "main")
        window = self.windows.pop(label, None)

        if window is None and self.app_handle:
            window = Manager.get_webview_window(self.app_handle, label)

        if window:
            try:
                window.close()
                log(f"Closed window '{label}'")
                self.send_result(label, True)
            except Exception as e:
                self.send_error(f"Failed to close window: {e}")
        else:
            self.send_error(f"Window not found: {label}")


def stdin_reader(ipc: JsonIPC) -> None:
    """Read commands from stdin in a separate thread."""
    log("stdin_reader started")
    try:
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue
            log(f"Received line: {line[:100]}...")
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


def main() -> int:
    """Run the PyWry subprocess."""
    from .commands import register_commands

    log(f"Starting subprocess... (headless={HEADLESS})")
    src_dir = Path(__file__).parent.absolute()
    ipc = JsonIPC()
    # Start stdin reader thread
    reader_thread = threading.Thread(target=stdin_reader, args=(ipc,), daemon=True)
    reader_thread.start()

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
        )

        def on_run(app_handle: Any, run_event: Any) -> None:
            if isinstance(run_event, RunEvent.Ready):
                log("App ready!")
                ipc.app_handle = app_handle
                # Get pre-configured main window
                main_window = Manager.get_webview_window(app_handle, "main")
                if main_window:
                    ipc.windows["main"] = main_window
                    log("Registered 'main' window")
                else:
                    log("WARNING: 'main' window not found!")
                ipc.send_ready()

        log("Starting app.run()...")
        app.run(on_run)

    log("Subprocess exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
