"""WebSockets models."""

from datetime import datetime
from typing import Any, Optional

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

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
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
        default=True,
        description="Whether to start the broadcast server."
        + " Set to False if system or network conditions do not allow it."
        + " Can be started manually with the 'start_broadcasting' method.",
    )


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
