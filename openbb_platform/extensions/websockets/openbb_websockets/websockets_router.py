"""Websockets Router."""

# pylint: disable=unused-argument,protected-access,unused-import

import asyncio
import sys
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import ValidationError

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
    examples=[
        APIEx(
            parameters={
                "name": "client1",
                "provider": "fmp",
                "asset_type": "crypto",
                "symbol": "btcusd,ethusd,solusd",
                "start_broadcast": True,
            }
        ),
        APIEx(
            parameters={
                "name": "client2",
                "provider": "polygon",
                "asset_type": "stock_delayed",
                "feed": "aggs_sec",
                "symbol": "*",
                "limit": "None",
                "results_file": "/path/to/results.db",
                "save_results": "True",
                "auth_token": "someAuthToken123$",
            }
        ),
    ],
)
async def create_connection(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
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

    if not client.is_running or client._exception is not None:
        exc = getattr(client, "_exception", None)
        if exc:
            client._atexit()
            if isinstance(exc, UnauthorizedError):
                raise exc
            raise OpenBBError(exc)
        raise OpenBBError("Client failed to connect.")

    if hasattr(extra_params, "start_broadcast") and extra_params.start_broadcast:
        try:
            client.start_broadcasting()
            await asyncio.sleep(1)
            if client._exception is not None:
                exc = getattr(client, "_exception", None)
                client._exception = None
                raise OpenBBError(exc)
        except Exception as e:  # pylint: disable=broad-except
            client._atexit()
            raise e from e

    client_name = client.name
    connected_clients[client_name] = client
    status = await get_status(client_name)
    obbject.results.status = WebSocketConnectionStatus(**status)
    return obbject


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Get all written results from a client connection.",
            code=["res = obb.websockets.get_results(name='client1')", "res.to_df()"],
        )
    ],
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
        return OBBject(results=client.results)
    except ValidationError as e:
        raise OpenBBError(e) from e


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Clear all results from a client connection database.",
            code=["obb.websockets.clear_results(name='client1')"],
        )
    ],
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
    examples=[
        PythonEx(
            description="Subscribe to a new symbol in an active client connection.",
            code=["obb.websockets.subscribe(name='client1', subscribe='ethusd')"],
        )
    ],
)
async def subscribe(
    name: str, symbol: str, auth_token: Optional[str] = None
) -> OBBject[WebSocketConnectionStatus]:
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
    WebSocketConnectionStatus
        The status of the client connection.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")

    client = connected_clients[name]
    symbols = client.symbol.split(",")

    if symbols and symbol in symbols:
        raise OpenBBError(f"Client {name} already subscribed to {symbol}.")

    try:
        client.subscribe(symbol)
    except OpenBBError as e:
        raise e from e

    status = await get_status(name)

    if client.is_running:
        return OBBject(results=WebSocketConnectionStatus(**status))

    client.logger.error(
        f"Client {name} failed to subscribe to {symbol} and is not running."
    )


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Unsubscribe from a symbol in an active client connection.",
            code=["obb.websockets.unsubscribe(name='client1', symbol='btcusd')"],
        )
    ],
)
async def unsubscribe(
    name: str, symbol: str, auth_token: Optional[str] = None
) -> OBBject[WebSocketConnectionStatus]:
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
    WebSocketConnectionStatus
        The status of the client connection.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")

    client = connected_clients[name]
    symbols = client.symbol.split(",")

    if symbol not in symbols:
        raise OpenBBError(f"Client {name} not subscribed to {symbol}.")

    client.unsubscribe(symbol)

    status = await get_status(name)

    return OBBject(results=WebSocketConnectionStatus(**status))


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Get the status of all created clients which have not been killed.",
            code=["obb.websockets.get_client_status()"],
        ),
        PythonEx(
            description="Get the status of a specific client.",
            code=["obb.websockets.get_client_status(name='client1')"],
        ),
    ],
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
    list[WebSocketConnectionStatus]
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
    examples=[
        PythonEx(
            description="Get the Python client object by 'name'."
            + " Useful if the local was collected by the Garbage Collector.",
            code=["obb.websockets.get_client(name='client1')"],
        ),
    ],
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
    examples=[
        PythonEx(
            description="Stop the connection to a provider websocket.",
            code=["obb.websockets.stop_connection(name='client2')"],
        ),
    ],
)
async def stop_connection(
    name: str, auth_token: Optional[str] = None
) -> OBBject[WebSocketConnectionStatus]:
    """Stop a the connection to the provider's websocket. Does not stop the broadcast server.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    WebSocketConnectionStatus
        The status of the client connection.
    """
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]
    client.disconnect()
    status = await get_status(name)

    return OBBject(results=WebSocketConnectionStatus(**status))


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Restart a stopped connection to a provider websocket.",
            code=["obb.websockets.restart_connection(name='client2')"],
        ),
    ],
)
async def restart_connection(
    name: str, auth_token: Optional[str] = None
) -> OBBject[WebSocketConnectionStatus]:
    """Restart a websocket connection.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    WebSocketConnectionStatus
        The status of the client connection.
    """
    if name not in connected_clients:
        raise OpenBBError(f"No active client named, {name}. Use create_connection.")
    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")
    client = connected_clients[name]

    try:
        client.connect()
    except OpenBBError as e:
        raise e from e

    status = await get_status(name)

    return OBBject(results=WebSocketConnectionStatus(**status))


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Stop broadcasting the results file.",
            code=["obb.websockets.stop_broadcasting(name='client1')"],
        ),
    ],
)
async def stop_broadcasting(
    name: str, auth_token: Optional[str] = None
) -> OBBject[WebSocketConnectionStatus]:
    """Stop the broadcast server.

    Parameters
    ----------
    name : str
        The name of the client.
    auth_token : Optional[str]
        The client's authorization token.

    Returns
    -------
    WebSocketConnectionStatus
        The status of the client connection.
    """
    if name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")

    if not await check_auth(name, auth_token):
        raise OpenBBError("Error finding client.")

    client = connected_clients[name]

    if not client.is_broadcasting:
        raise OpenBBError(f"Client {name} not broadcasting.")

    client.stop_broadcasting()

    if not client.is_running:
        client._atexit()
        del connected_clients[name]
        return OBBject(
            results=f"Client {name} stopped broadcasting and was not running, client removed."
        )

    status = await get_status(name)

    return OBBject(results=WebSocketConnectionStatus(**status))


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Start broadcasting the results file.",
            code=[
                "obb.websockets.start_broadcasting(name='client1', host='0.0.0.0', port=6942)"
            ],
        ),
    ],
)
async def start_broadcasting(
    name: str,
    auth_token: Optional[str] = None,
    host: str = "127.0.0.1",
    port: int = 6666,
    uvicorn_kwargs: Optional[dict[str, Any]] = None,
) -> OBBject[WebSocketConnectionStatus]:
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
        Additional keyword arguments to pass directly to `uvicorn.run()`.

    Returns
    -------
    WebSocketConnectionStatus
        The status of the client connection.
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

    status = await get_status(name)

    return OBBject(results=WebSocketConnectionStatus(**status))


@router.command(
    methods=["GET"],
    examples=[
        PythonEx(
            description="Kill all associated processes with a websocket connection.",
            code=["obb.websockets.kill(name='client2')"],
        ),
    ],
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

    if name and name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")

    client = connected_clients[name]
    client._atexit()
    del connected_clients[name]

    return OBBject(results=f"Clients {name} killed.")
