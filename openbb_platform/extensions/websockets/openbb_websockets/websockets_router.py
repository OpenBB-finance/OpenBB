"""Websockets Router."""

# pylint: disable=unused-argument

import asyncio
import sys
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError

from openbb_websockets.helpers import (
    StdOutSink,
    check_auth,
    connected_clients,
    get_status,
)
from openbb_websockets.models import WebSocketConnectionStatus

router = Router("", description="WebSockets Router")
sys.stdout = StdOutSink()


@router.command(
    model="WebSocketConnection",
)
async def create_connection(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[WebSocketConnectionStatus]:
    """Create a new provider websocket connection."""
    name = extra_params.name
    if name in connected_clients:
        broadcast_address = connected_clients[name].broadcast_address
        is_running = connected_clients[name].is_running
        if broadcast_address or is_running:
            raise OpenBBError(
                f"Client {name} already connected! Broadcasting to: {broadcast_address}"
            )
        raise OpenBBError(f"Client {name} already connected but not running.")
    del name

    obbject = await OBBject.from_query(Query(**locals()))
    client = obbject.results.client

    await asyncio.sleep(1)

    if not client.is_running or client._exception:
        exc = getattr(client, "_exception", None)
        if exc:
            client._atexit()
            if isinstance(exc, UnauthorizedError):
                raise exc
            raise OpenBBError(exc)
        raise OpenBBError("Client failed to connect.")

    if hasattr(extra_params, "start_broadcast") and extra_params.start_broadcast:
        client.start_broadcasting()

    client_name = client.name
    connected_clients[client_name] = client
    results = await get_status(client_name)

    obbject.results = WebSocketConnectionStatus(**results)

    return obbject


@router.command(
    methods=["GET"],
)
async def get_results(name: str, auth_token: Optional[str] = None) -> OBBject:
    """Get all recorded results from a client connection.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    list[Data]
        The recorded results from the client.
    """

    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    if not client.results:
        raise EmptyDataError(f"No results recorded for client {name}.")
    try:
        return OBBject(results=client.transformed_results)
    except NotImplementedError:
        return OBBject(results=client.results)


@router.command(
    methods=["GET"],
)
async def clear_results(name: str, auth_token: Optional[str] = None) -> OBBject[str]:
    """Clear all stored results from a client connection. Does not stop the client or broadcast.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The number of results cleared from the client.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    n_before = len(client.results)
    del client.results
    return OBBject(results=f"{n_before} results cleared from {name}.")


@router.command(
    methods=["GET"],
)
async def subscribe(
    name: str, symbol: str, auth_token: Optional[str] = None
) -> OBBject[str]:
    """Subscribe to a new symbol.

    Parameters
    ----------
    name : str
        The name of the client.
    symbol : str
        The symbol to subscribe to.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the client subscribed to the symbol.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")

    client = connected_clients[name]
    symbols = client.symbol.split(",")

    if symbols and symbol in symbols:
        raise OpenBBError(f"Client {name} already subscribed to {symbol}.")

    client.subscribe(symbol)
    await asyncio.sleep(1)

    if client.is_running:
        return OBBject(results=f"Added {symbol} to client {name} connection.")

    client.logger.error(
        f"Client {name} failed to subscribe to {symbol} and is not running."
    )


@router.command(
    methods=["GET"],
)
async def unsubscribe(
    name: str, symbol: str, auth_token: Optional[str] = None
) -> OBBject[str]:
    """Unsubscribe to a symbol.

    Parameters
    ----------
    name : str
        The name of the client.
    symbol : str
        The symbol to unsubscribe from.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the client unsubscribed from the symbol.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    symbols = client.symbol.split(",")
    if symbol not in symbols:
        raise OpenBBError(f"Client {name} not subscribed to {symbol}.")
    client.unsubscribe(symbol)
    # await asyncio.sleep(2)
    if client.is_running:
        return OBBject(results=f"Client {name} unsubscribed to {symbol}.")
    client.logger.error(
        f"Client {name} failed to unsubscribe to {symbol} and is not running."
    )


@router.command(
    methods=["GET"],
)
async def get_client_status(
    name: str = "all",
) -> OBBject[list[WebSocketConnectionStatus]]:
    """Get the status of a client, or all client connections.

    Parameters
    ----------
    name : str
        The name of the client. Default is "all".

    Returns
    -------
    list[dict]
        The status of the client(s).
    """
    if not connected_clients:
        raise OpenBBError("No active connections.")
    if name == "all":
        connections = [
            await get_status(client.name) for client in connected_clients.values()
        ]
    else:
        connections = [await get_status(name)]
    return OBBject(results=[WebSocketConnectionStatus(**d) for d in connections])


@router.command(
    methods=["GET"],
    include_in_schema=False,
)
async def get_client(name: str, auth_token: Optional[str] = None) -> OBBject:
    """Get an open client connection object. This endpoint is only available from the Python interface.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    WebSocketClient
        The provider client connection object.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    return OBBject(results=client)


@router.command(
    methods=["GET"],
)
async def stop_connection(name: str, auth_token: Optional[str] = None) -> OBBject[str]:
    """Stop a the connection to the provider's websocket. Does not stop the broadcast server.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the provider connection was stopped.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    client.disconnect()
    return OBBject(
        results=f"Client {name} connection to the provider's websocket was stopped."
    )


@router.command(
    methods=["GET"],
)
async def restart_connection(
    name: str, auth_token: Optional[str] = None
) -> OBBject[str]:
    """Restart a websocket connection.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the client connection was restarted.
    """
    if name not in connected_clients:
        raise OpenBBError(f"No active client named, {name}. Use create_connection.")
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    client.connect()
    return OBBject(results=f"Client {name} connection was restarted.")


@router.command(
    methods=["GET"],
)
async def stop_broadcasting(
    name: str, auth_token: Optional[str] = None
) -> OBBject[str]:
    """Stop the broadcast server.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the client stopped broadcasting to the address.
    """
    if name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")

    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")

    client = connected_clients[name]

    if not client.is_broadcasting:
        raise OpenBBError(f"Client {name} not broadcasting.")

    old_address = client.broadcast_address
    client.stop_broadcasting()

    if not client.is_running:
        client._atexit()
        del connected_clients[name]
        return OBBject(
            results=f"Client {name} stopped broadcasting and was not running, client removed."
        )

    return OBBject(results=f"Client {name} stopped broadcasting to: {old_address}")


@router.command(
    methods=["GET"],
)
async def start_broadcasting(
    name: str,
    auth_token: Optional[str] = None,
    host: str = "127.0.0.1",
    port: int = 6666,
    uvicorn_kwargs: Optional[dict[str, Any]] = None,
) -> OBBject[str]:
    """Start broadcasting from a websocket.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.
    host : str
        The host address to broadcast to. Default is 127.0.0.1"
    port : int
        The port to broadcast to. Default is 6666.
    uvicorn_kwargs : Optional[dict[str, Any]]
        Additional keyword arguments for passing directly to the uvicorn server.

    Returns
    -------
    str
        The message that the client started broadcasting.
    """
    if name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    kwargs = uvicorn_kwargs if uvicorn_kwargs else {}
    client.start_broadcasting(host=host, port=port, **kwargs)

    await asyncio.sleep(2)
    if not client.is_broadcasting:
        raise OpenBBError(f"Client {name} failed to broadcast.")
    return OBBject(
        results=f"Client {name} started broadcasting to {client.broadcast_address}."
    )


@router.command(
    methods=["GET"],
)
async def kill(name: str, auth_token: Optional[str] = None) -> OBBject[str]:
    """Kills a client.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    str
        The message that the client was killed.
    """
    if not connected_clients:
        raise OpenBBError("No connections to kill.")
    elif name and name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    client = connected_clients[name]
    client._atexit()
    del connected_clients[name]
    return OBBject(results=f"Clients {name} killed.")
