"""PyTauri subprocess runtime management.

Spawns pytauri as a subprocess and communicates via JSON IPC over stdin/stdout.
"""

from __future__ import annotations

import atexit
import contextlib
import json
import os
import subprocess
import sys
import threading

from pathlib import Path
from queue import Empty, Queue
from typing import Any

from .callbacks import get_registry


def is_headless() -> bool:
    """Check if headless mode is enabled.

    Headless mode creates windows that are fully functional but not visible,
    allowing full E2E testing in CI environments without a display.

    Returns
    -------
    bool
        True if PYWRY_HEADLESS environment variable is set.
    """
    return os.environ.get("PYWRY_HEADLESS", "").lower() in ("1", "true", "yes", "on")


# Module state
_process: subprocess.Popen[str] | None = None
_reader_thread: threading.Thread | None = None
_writer_thread: threading.Thread | None = None
_ready_event = threading.Event()
_outgoing: Queue[dict[str, Any]] = Queue()
_responses: Queue[dict[str, Any]] = Queue()
_running = False  # pylint: disable=invalid-name
_registry = None  # pylint: disable=invalid-name


def _get_registry() -> Any:
    """Get the registry, caching the reference."""
    global _registry
    if _registry is None:
        _registry = get_registry()
    return _registry


def get_pywry_dir() -> Path:
    """Get the pywry directory containing the subprocess entry point."""
    return Path(__file__).parent.absolute()


def is_running() -> bool:
    """Check if the subprocess is running."""
    return _process is not None and _process.poll() is None


def wait_ready(timeout: float = 10.0) -> bool:
    """Wait for the subprocess to be ready."""
    return _ready_event.wait(timeout)


def _stdout_reader() -> None:
    """Read responses from subprocess stdout."""
    global _running
    try:
        while _running and _process and _process.stdout:
            line = _process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                if msg.get("type") == "ready":
                    _ready_event.set()
                elif msg.get("type") == "event":
                    _dispatch_event(msg)
                else:
                    _responses.put(msg)
            except json.JSONDecodeError:
                pass
    except Exception:
        pass


def _dispatch_event(msg: dict[str, Any]) -> None:
    """Dispatch an event from the subprocess to Python callbacks."""
    label = msg.get("label", "main")
    event_type = msg.get("event_type", "")
    data = msg.get("data", {})

    registry = _get_registry()

    # Map content:ready -> pywry:ready for consistent public API
    # content:ready is sent AFTER content is actually set in the DOM
    # (window:ready fires too early - before set_content completes)
    if event_type == "content:ready":
        event_type = "pywry:ready"

    registry.dispatch(label, event_type, data)


def _stdin_writer() -> None:
    """Write commands to subprocess stdin."""
    global _running
    try:
        while _running and _process and _process.stdin and not _process.stdin.closed:
            try:
                cmd = _outgoing.get(timeout=0.1)
                if not _running or not _process or not _process.stdin or _process.stdin.closed:
                    break
                line = json.dumps(cmd) + "\n"
                _process.stdin.write(line)
                _process.stdin.flush()
            except Empty:
                continue
            except (OSError, BrokenPipeError):
                # Pipe closed during shutdown - expected
                break
            except Exception as e:
                sys.stderr.write(f"[pywry] Write error: {e}\n")
                break
    except Exception as e:
        sys.stderr.write(f"[pywry] Writer error: {e}\n")


def send_command(cmd: dict[str, Any]) -> None:
    """Send a command to the subprocess."""
    _outgoing.put(cmd)


def get_response(timeout: float = 5.0) -> dict[str, Any] | None:
    """Get a response from the subprocess."""
    try:
        return _responses.get(timeout=timeout)
    except Empty:
        return None


def create_window(
    label: str,
    title: str = "PyWry",
    width: int = 800,
    height: int = 600,
) -> bool:
    """Create a window via IPC. Waits for window to be created."""
    send_command(
        {
            "action": "create",
            "label": label,
            "title": title,
            "width": width,
            "height": height,
        }
    )
    # Wait for the window to be created
    response = get_response(timeout=5.0)
    return response is not None and response.get("success", False)


def set_content(label: str, html: str, theme: str = "dark") -> bool:
    """Set window content via IPC. Waits for content to be set.

    Parameters
    ----------
    label : str
        Window label.
    html : str
        HTML content.
    theme : str
        Theme mode ('dark' or 'light') - MUST match window background.
    """
    send_command(
        {
            "action": "set_content",
            "label": label,
            "html": html,
            "theme": theme,
        }
    )
    response = get_response(timeout=5.0)
    return response is not None and response.get("success", False)


def close_window(label: str) -> bool:
    """Close a window via IPC."""
    send_command(
        {
            "action": "close",
            "label": label,
        }
    )
    return True


def show_window(label: str) -> bool:
    """Show a hidden window via IPC."""
    send_command(
        {
            "action": "show",
            "label": label,
        }
    )
    return True


def inject_css(label: str, css: str, asset_id: str) -> bool:
    """Inject or update CSS in a window without page reload.

    Parameters
    ----------
    label : str
        Window label to inject into.
    css : str
        CSS content to inject.
    asset_id : str
        ID for the style element (for updates).

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "emit",
            "label": label,
            "event": "pywry:inject-css",
            "payload": {
                "css": css,
                "id": asset_id,
            },
        }
    )
    return True


def remove_css(label: str, asset_id: str) -> bool:
    """Remove a CSS style element from a window.

    Parameters
    ----------
    label : str
        Window label.
    asset_id : str
        ID of the style element to remove.

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "emit",
            "label": label,
            "event": "pywry:remove-css",
            "payload": {
                "id": asset_id,
            },
        }
    )
    return True


def refresh_window(label: str) -> bool:
    """Trigger a full page refresh for a window.

    Preserves scroll position using sessionStorage.

    Parameters
    ----------
    label : str
        Window label to refresh.

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "emit",
            "label": label,
            "event": "pywry:refresh",
            "payload": {},
        }
    )
    return True


def refresh_all_windows() -> bool:
    """Trigger a full page refresh for all windows.

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "emit",
            "label": "*",
            "event": "pywry:refresh",
            "payload": {},
        }
    )
    return True


def emit_event(label: str, event: str, payload: dict[str, Any] | None = None) -> bool:
    """Emit a custom event to a window.

    Parameters
    ----------
    label : str
        Window label (or "*" for all windows).
    event : str
        Event name.
    payload : dict[str, Any] or None, optional
        Event payload data.

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "emit",
            "label": label,
            "event": event,
            "payload": payload or {},
        }
    )
    return True


def eval_js(label: str, script: str) -> bool:
    """Evaluate arbitrary JavaScript in a window.

    This runs JavaScript without replacing window content,
    useful for DOM queries and dynamic updates.

    Parameters
    ----------
    label : str
        Window label.
    script : str
        JavaScript code to execute.

    Returns
    -------
    bool
        True if command was sent.
    """
    send_command(
        {
            "action": "eval",
            "label": label,
            "script": script,
        }
    )
    return True


def start() -> bool:
    """Start the pytauri subprocess.

    Returns
    -------
    bool
        True if started successfully.
    """
    global _process, _reader_thread, _writer_thread, _running

    if is_running():
        return True

    _ready_event.clear()
    _running = True
    pywry_dir = get_pywry_dir()
    python_exe = sys.executable
    cmd = [python_exe, "-u", "-m", "pywry"]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        _process = subprocess.Popen(  # pylint: disable=R1732
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=pywry_dir.parent,
            text=True,
            bufsize=1,
            env=env,
        )
    except Exception as e:
        sys.stderr.write(f"[pywry] Failed to start subprocess: {e}\n")
        _running = False
        return False

    # Start reader thread
    _reader_thread = threading.Thread(target=_stdout_reader, daemon=True)
    _reader_thread.start()

    # Start writer thread
    _writer_thread = threading.Thread(target=_stdin_writer, daemon=True)
    _writer_thread.start()

    # Start stderr reader for debugging
    def stderr_reader() -> None:
        try:
            while _running and _process and _process.stderr:
                line = _process.stderr.readline()
                if not line:
                    break
                sys.stderr.write(f"[pywry-subprocess] {line}")
        except Exception:
            pass

    stderr_thread = threading.Thread(target=stderr_reader, daemon=True)
    stderr_thread.start()

    # Wait for ready signal
    if not wait_ready(timeout=10.0):
        sys.stderr.write("[pywry] Subprocess did not become ready\n")
        stop()
        return False

    # Register cleanup on exit
    atexit.register(stop)

    return True


def stop() -> None:
    """Stop the pytauri subprocess."""
    global _process, _running  # pylint: disable=W0603

    _running = False
    _ready_event.clear()

    # Clear queues to prevent stale data on restart
    while not _outgoing.empty():
        try:
            _outgoing.get_nowait()
        except Empty:
            break
    while not _responses.empty():
        try:
            _responses.get_nowait()
        except Empty:
            break

    if _process:
        # Send quit command
        try:
            if _process.stdin and not _process.stdin.closed:
                _process.stdin.write('{"action": "quit"}\n')
                _process.stdin.flush()
        except (OSError, BrokenPipeError, ValueError):
            pass

        # Close all pipes to prevent flush errors on GC
        for pipe in (_process.stdin, _process.stdout, _process.stderr):
            if pipe:
                with contextlib.suppress(OSError, BrokenPipeError, ValueError):
                    pipe.close()

        # Wait for process to exit
        try:
            _process.wait(timeout=2.0)
        except Exception:
            try:
                _process.terminate()
                _process.wait(timeout=1.0)
            except Exception:
                with contextlib.suppress(Exception):
                    _process.kill()

        _process = None
