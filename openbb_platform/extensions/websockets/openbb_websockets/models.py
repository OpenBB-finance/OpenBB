"""WebSockets models."""

from datetime import datetime
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import ConfigDict, Field, field_validator

from openbb_websockets.client import WebSocketClient


class WebSocketQueryParams(QueryParams):
    """Query parameters for WebSocket connection creation."""

    name: str = Field(
        description="Name to assign the client connection.",
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Authentication token for API access control of the client, not related to the provider credentials.",
    )
    results_file: Optional[str] = Field(
        default=None,
        description="Absolute path to the file for continuous writing. By default, a temporary file is created.",
    )
    save_results: bool = Field(
        default=False,
        description="Whether to save the results after the session ends.",
    )
    table_name: str = Field(
        default="records",
        description="Name of the SQL table to write the results to.",
    )
    limit: Optional[int] = Field(
        default=1000,
        description="Maximum number of newest records to keep in the database."
        + " If None, all records are kept, which can be memory-intensive.",
    )
    sleep_time: float = Field(
        default=0.25,
        description="Time to sleep between checking for new records in the database from the broadcast server."
        + " The default is 0.25 seconds.",
    )
    broadcast_host: str = Field(
        default="127.0.0.1",
        description="IP address to bind the broadcast server to.",
    )
    broadcast_port: int = Field(
        default=6666,
        description="Port to bind the broadcast server to.",
    )
    start_broadcast: bool = Field(
        default=False,
        description="Whether to start the broadcast server."
        + " Set to False if system or network conditions do not allow it."
        + " Can be started manually with the 'start_broadcasting' method.",
    )
    connect_kwargs: Optional[Any] = Field(
        default=None,
        description="A formatted dictionary, or serialized JSON string, of keyword arguments to pass"
        + " directly to websockets.connect().",
    )

    @field_validator("connect_kwargs", mode="before", check_fields=False)
    @classmethod
    def _validate_connect_kwargs(cls, v):
        """Validate the connect_kwargs format."""
        # pylint: disable=import-outside-toplevel
        import json

        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError as e:
                raise OpenBBError(
                    f"Invalid JSON format for 'connect_kwargs': {e}"
                ) from e
        if v is not None and not isinstance(v, dict):
            raise OpenBBError(
                "Invalid 'connect_kwargs' format. Must be a dictionary or serialized JSON string."
            )

        return json.dumps(v, separators=(",", ":"))


class WebSocketData(Data):
    """WebSocket data model."""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )


class WebSocketConnection(Data):
    """Data model for returning WebSocketClient from the Provider Interface."""

    __model_config__ = ConfigDict(
        extra="forbid",
    )

    client: Any = Field(
        description="Instance of WebSocketClient class initialized by a provider Fetcher."
        + " The client is used to communicate with the provider's data stream."
        + " It is not returned to the user, but is handled by the router for API access.",
        exclude=True,
    )

    @field_validator("client", mode="before", check_fields=False)
    def _validate_client(cls, v):
        """Validate the client."""
        if not isinstance(v, WebSocketClient):
            raise ValueError("Client must be an instance of WebSocketClient.")
        return v


class WebSocketConnectionStatus(Data):
    """Data model for WebSocketConnection status information."""

    name: str = Field(
        description="Name assigned to the client connection.",
    )
    auth_required: bool = Field(
        description="True when 'auth_token' is supplied at initialization."
        " When True, interactions with the client from the Python or API"
        + " endpoints requires it to be supplied as a query parameter.",
    )
    subscribed_symbols: str = Field(
        description="Symbols subscribed to by the client connection.",
    )
    is_running: bool = Field(
        description="Whether the client connection is running.",
    )
    provider_pid: Optional[int] = Field(
        default=None,
        description="Process ID of the provider connection.",
    )
    is_broadcasting: bool = Field(
        description="Whether the client connection is broadcasting.",
    )
    broadcast_address: Optional[str] = Field(
        default=None,
        description="URI to the broadcast server.",
    )
    broadcast_pid: Optional[int] = Field(
        default=None,
        description="Process ID of the broadcast server.",
    )
    results_file: Optional[str] = Field(
        description="Absolute path to the file for continuous writing.",
    )
    table_name: Optional[str] = Field(
        default=None,
        description="Name of the SQL table to write the results to.",
    )
    save_results: bool = Field(
        description="Whether to save the results after the session ends.",
    )
