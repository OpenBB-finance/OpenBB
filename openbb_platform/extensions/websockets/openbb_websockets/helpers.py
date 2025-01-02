"""WebSockets helpers."""

import logging
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import UnauthorizedError
from openbb_core.provider.utils.websockets.helpers import AUTH_TOKEN_FILTER

connected_clients: dict = {}


async def get_status(name: Optional[str] = None, client: Optional[Any] = None) -> dict:
    """Get the status of a client."""
    if name and name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    if not name and not client:
        raise OpenBBError("Either name or client must be provided.")
    client = client if client else connected_clients[name]
    provider_pid = (
        client._psutil_process.pid  # pylint: disable=protected-access
        if client.is_running
        else None
    )
    broadcast_pid = (
        client._psutil_broadcast_process.pid  # pylint: disable=protected-access
        if client.is_broadcasting
        else None
    )
    status = {
        "name": client.name,
        "auth_required": client._auth_token  # pylint: disable=protected-access
        is not None,
        "subscribed_symbols": client.symbol,
        "is_running": client.is_running,
        "provider_pid": provider_pid,
        "is_broadcasting": client.is_broadcasting,
        "broadcast_address": client.broadcast_address,
        "broadcast_pid": broadcast_pid,
        "results_file": client.results_file,
        "table_name": client.table_name,
        "save_database": client.save_database,
    }
    return status


async def check_auth(name: str, auth_token: Optional[str] = None) -> bool:
    """Check the auth token."""
    if name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    client = connected_clients[name]
    if client._auth_token is None:  # pylint: disable=protected-access
        return True
    if auth_token is None:
        raise UnauthorizedError(f"Client authorization token is required for {name}.")
    if auth_token != client._decrypt_value(  # pylint: disable=protected-access
        client._auth_token  # pylint: disable=protected-access
    ):
        raise UnauthorizedError(f"Invalid client authorization token for {name}.")
    return True


class StdOutSink:
    """Filter stdout for PII."""

    def write(self, message):
        """Write to stdout."""
        # pylint: disable=import-outside-toplevel
        import os
        import sys

        os.set_blocking(sys.__stdout__.fileno(), False)  # type: ignore
        cleaned_message = AUTH_TOKEN_FILTER.sub(r"\1********", message)
        if cleaned_message != message:
            cleaned_message = f"{cleaned_message}\n"
        sys.__stdout__.write(cleaned_message)  # type: ignore

    def flush(self):
        """Flush stdout."""
        # pylint: disable=import-outside-toplevel
        import sys

        sys.__stdout__.flush()  # type: ignore


class AuthTokenFilter(logging.Formatter):
    """Custom logging formatter to filter auth tokens."""

    def format(self, record):
        """Format the log record."""
        original_message = super().format(record)
        cleaned_message = AUTH_TOKEN_FILTER.sub(r"\1********", original_message)
        return cleaned_message
