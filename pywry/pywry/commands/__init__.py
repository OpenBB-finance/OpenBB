"""PyTauri commands for PyWry IPC communication."""

from __future__ import annotations

import json
import subprocess
import sys
import threading

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ..callbacks import get_registry
from ..log import debug, exception, redact_sensitive_data, warn
from ..models import GenericEvent


# Lock for thread-safe stdout writes
_stdout_lock = threading.Lock()


if TYPE_CHECKING:
    from pytauri import Commands

__all__ = [
    "COMMAND_HANDLERS",
    "GenericEvent",
    "dispatch_command",
    "handle_aggrid_event",
    "handle_open_file",
    "handle_open_url",
    "handle_plotly_event",
    "handle_pywry_event",
    "handle_pywry_result",
    "handle_window_close",
    "register_commands",
    "serialize_response",
]


class EventPayload(BaseModel):
    """Payload for event commands."""

    label: str
    event_type: str
    data: dict[str, Any]


class ResultPayload(BaseModel):
    """Payload for result commands."""

    data: Any
    window_label: str


class OpenPayload(BaseModel):
    """Payload for open commands."""

    target: str


def register_commands(commands: Commands) -> None:
    """Register IPC commands with pytauri.

    Parameters
    ----------
    commands : Commands
        pytauri Commands instance.
    """

    @commands.command()
    async def pywry_event(body: EventPayload) -> dict[str, Any]:
        """Handle event from JavaScript."""
        try:
            debug(
                f"[IPC] pywry_event: label={body.label}, type={body.event_type}, data={body.data}"
            )
            result = handle_pywry_event(body.label, {"type": body.event_type, "data": body.data})
            debug(f"[IPC] pywry_event returning: {result}")
            return result
        except Exception as e:
            exception(f"pywry_event failed: {e}")
            raise

    @commands.command()
    async def pywry_result(body: ResultPayload) -> dict[str, Any]:
        """Handle result from JavaScript."""
        # Redact sensitive values in debug output
        debug(
            f"[IPC] pywry_result: label={body.window_label}, data={redact_sensitive_data(body.data)}"
        )
        result = handle_pywry_result(body.window_label, body.data)
        debug(f"[IPC] pywry_result returning: {result}")
        return result

    @commands.command()
    async def pywry_open_file(body: OpenPayload) -> dict[str, Any]:
        """Open a file in the default application."""
        return handle_open_file(body.target)

    @commands.command()
    async def pywry_open_url(body: OpenPayload) -> dict[str, Any]:
        """Open a URL in the default browser."""
        return handle_open_url(body.target)

    debug("Registered pytauri commands")


def send_event_to_parent(label: str, event_type: str, data: dict[str, Any]) -> None:
    """Send an event to the parent process via stdout.

    Parameters
    ----------
    label : str
        The window label.
    event_type : str
        The event type.
    data : dict of str to Any
        The event data.
    """
    msg = {
        "type": "event",
        "label": label,
        "event_type": event_type,
        "data": data,
    }
    # Redact sensitive values (e.g., SecretInput values) in debug output
    debug(f"[IPC] send_event_to_parent: {redact_sensitive_data(msg)}")
    try:
        with _stdout_lock:
            sys.stdout.write(json.dumps(msg) + "\n")
            sys.stdout.flush()
        debug("[IPC] Event sent to stdout")
    except Exception as e:
        # Log error but don't crash - stdout might be closed during shutdown
        exception(f"send_event_to_parent failed: {e}")


def handle_pywry_result(label: str, data: dict[str, Any]) -> dict[str, Any]:
    """Handle result from JavaScript execution.

    Parameters
    ----------
    label : str
        The window label.
    data : dict of str to Any
        The result data.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    # Redact sensitive values in debug output
    debug(f"Received result from window '{label}': {redact_sensitive_data(data)}")

    # Send to parent process
    send_event_to_parent(label, "pywry:result", data)

    return {"success": True}


def handle_pywry_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle generic events from JavaScript.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The event data including type and payload.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    # Parse the event
    event_type = event_data.get("type", "")
    data = event_data.get("data", {})

    debug(f"Received event '{event_type}' from window '{label}'")

    # Dispatch to registered callbacks
    dispatched = get_registry().dispatch(label, event_type, data)
    debug(f"Event '{event_type}' dispatched={dispatched}")

    # Also send to parent process via stdout (for external consumers)
    send_event_to_parent(label, event_type, data)

    return {"success": True, "dispatched": dispatched}


def handle_plotly_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle Plotly-specific events.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The event data with plotly_event and data fields.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    event_name = event_data.get("plotly_event", "click")
    data = event_data.get("data", {})

    # Map to namespace:event format
    event_type = f"plotly:{event_name}"

    debug(f"Received Plotly event '{event_type}' from window '{label}'")

    dispatched = get_registry().dispatch(label, event_type, data)
    return {"success": True, "dispatched": dispatched}


def handle_aggrid_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle AG Grid-specific events.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The event data with grid_event and data fields.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    event_name = event_data.get("grid_event", "selection")
    data = event_data.get("data", {})

    # Map to namespace:event format
    event_type = f"aggrid:{event_name}"

    debug(f"Received AG Grid event '{event_type}' from window '{label}'")

    dispatched = get_registry().dispatch(label, event_type, data)
    return {"success": True, "dispatched": dispatched}


def handle_window_close(label: str) -> dict[str, Any]:
    """Handle window close event - aggressive cleanup.

    Parameters
    ----------
    label : str
        The window label.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    debug(f"Window '{label}' closing - destroying resources")

    # Dispatch close event first (in case handlers want to save state)
    get_registry().dispatch(label, "pywry:close", {"label": label})

    # Destroy all callbacks for this window (burn everything)
    get_registry().destroy(label)

    return {"success": True}


def handle_open_file(path: str) -> dict[str, Any]:
    """Open a file with the system's default application.

    Parameters
    ----------
    path : str
        The file path to open.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    debug(f"Opening file: {path}")

    file_path = Path(path)
    if not file_path.exists():
        warn(f"File not found: {path}")
        return {"success": False, "error": "File not found"}

    try:
        if sys.platform == "win32":
            import os

            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=True)  # noqa: S603, S607
        else:
            # Linux and other Unix-like systems
            subprocess.run(["xdg-open", path], check=True)  # noqa: S603, S607
        return {"success": True}
    except (OSError, subprocess.SubprocessError) as e:
        warn(f"Failed to open file: {e}")
        return {"success": False, "error": str(e)}


def handle_open_url(url: str) -> dict[str, Any]:
    """Open a URL in the system's default browser.

    Parameters
    ----------
    url : str
        The URL to open.

    Returns
    -------
    dict of str to Any
        Response dict indicating success/failure.
    """
    import webbrowser

    debug(f"Opening URL: {url}")

    try:
        webbrowser.open(url)
        return {"success": True}
    except (OSError, webbrowser.Error) as e:
        warn(f"Failed to open URL: {e}")
        return {"success": False, "error": str(e)}


# Command dispatcher - maps command names to handlers
COMMAND_HANDLERS: dict[str, Any] = {
    "pywry_result": handle_pywry_result,
    "pywry_event": handle_pywry_event,
    "plotly_event": handle_plotly_event,
    "aggrid_event": handle_aggrid_event,
    "window_close": handle_window_close,
    "open_file": handle_open_file,
    "open_url": handle_open_url,
}


def dispatch_command(command: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a command to its handler.

    Parameters
    ----------
    command : str
        The command name.
    payload : dict of str to Any
        The command payload.

    Returns
    -------
    dict of str to Any
        Response dict from the handler.
    """
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        warn(f"Unknown command: {command}")
        return {"success": False, "error": f"Unknown command: {command}"}

    try:
        # Extract label and data based on command type
        result: dict[str, Any]
        if command in ("open_file",):
            result = handler(payload.get("path", ""))
        elif command in ("open_url",):
            result = handler(payload.get("url", ""))
        elif command in ("window_ready", "window_close"):
            result = handler(payload.get("label", ""))
        else:
            label = payload.get("label", "")
            data = payload.get("data", payload)
            result = handler(label, data)
        return result
    except (RuntimeError, TypeError, ValueError, KeyError) as e:
        warn(f"Error in command handler '{command}': {e}")
        return {"success": False, "error": str(e)}


def serialize_response(response: dict[str, Any]) -> str:
    """Serialize a response to JSON string.

    Parameters
    ----------
    response : dict of str to Any
        The response dict.

    Returns
    -------
    str
        JSON string.
    """
    return json.dumps(response)
