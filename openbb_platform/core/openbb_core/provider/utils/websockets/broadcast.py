"""Broadcast server for streaming results to connected clients via WebSocket."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openbb_core.provider.utils.websockets.database import (
    CHECK_FOR,
    Database,
)
from openbb_core.provider.utils.websockets.helpers import (
    get_logger,
    parse_kwargs,
)
from starlette.websockets import WebSocketState

kwargs = parse_kwargs()

HOST = kwargs.pop("host", None) or "localhost"
PORT = kwargs.pop("port", None) or 6666
PORT = int(PORT)

RESULTS_FILE = kwargs.pop("results_file", None)
TABLE_NAME = kwargs.pop("table_name", None) or "records"
SLEEP_TIME = kwargs.pop("sleep_time", None) or 0.25
AUTH_TOKEN = kwargs.pop("auth_token", None)

SQL = kwargs.pop("sql", None)
SQL_CONNECT_KWARGS = kwargs.pop("sql_connect_kwargs", None) or {}

app = FastAPI()

CONNECTED_CLIENTS: set = set()
MAIN_CLIENT = None
STDIN_TASK = None
LOGGER = get_logger("broadcast-server")


async def read_stdin():
    """Read from stdin."""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        sys.stdin.flush()
        sys.stdout.flush()

        if not line:
            continue

        if line.strip() == "numclients":
            MAIN_CLIENT.logger.info(  # type: ignore
                "Number of connected clients: %i", len(CONNECTED_CLIENTS)
            )
            continue
        if len(CONNECTED_CLIENTS) > 0:
            try:
                command = (
                    json.loads(line.strip())
                    if line.strip().startswith("{") or line.strip().startswith("[")
                    else line.strip()
                )
            except json.JSONDecodeError:
                err_msg = f"Invalid JSON received from stdin -> {line}"
                for client in CONNECTED_CLIENTS:
                    client.logger.error(err_msg)

            for client in CONNECTED_CLIENTS:
                if client.websocket.client_state != WebSocketState.DISCONNECTED:
                    await client.websocket.send_json(command)
                else:
                    CONNECTED_CLIENTS.remove(client)


@app.websocket("/")
async def websocket_endpoint(  # noqa: PLR0915
    websocket: WebSocket,
    auth_token: Optional[str] = None,
    replay: bool = False,
):
    """Connect to the broadcast server."""
    headers = dict(websocket.headers)
    sql = None

    if headers.get("sql"):
        sql = headers.pop("sql", None)

    broadcast_server = BroadcastServer(
        RESULTS_FILE,
        TABLE_NAME,
        SLEEP_TIME,
        str(AUTH_TOKEN),
        sql=sql,
    )
    broadcast_server.replay = replay  # type: ignore
    auth_token = str(auth_token)

    if sql and (
        any(x in sql for x in CHECK_FOR)
        or (broadcast_server.table_name not in sql and "message" not in sql)
    ):
        await websocket.accept()
        await websocket.send_text("Connection refused because of invalid SQL.")
        broadcast_server.logger.info("Invalid SQL query passed. -> %s", sql)
        await websocket.close(code=1008, reason="Invalid parameter values.")
        return

    if (
        broadcast_server.auth_token is not None
        and auth_token
        != broadcast_server._decrypt_value(  # pylint: disable=protected-access
            broadcast_server.auth_token
        )
    ):
        await websocket.accept()
        await websocket.send_text(
            "UnauthorizedError:    Invalid authentication token. Could not connect to the broadcast."
        )
        broadcast_server.logger.error(
            "Invalid authentication token passed by a client connecting."
        )
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    await websocket.accept()

    if RESULTS_FILE is None:
        raise ValueError("Results file path is required for WebSocket server.")

    broadcast_server.websocket = websocket
    CONNECTED_CLIENTS.add(broadcast_server)
    try:
        stream_task = asyncio.create_task(broadcast_server.stream_results())
        stdin_task = asyncio.create_task(read_stdin())
        await asyncio.gather(*[stdin_task, stream_task], return_exceptions=True)

    except (asyncio.CancelledError, RuntimeError):
        broadcast_server.logger.info("A listener task was cancelled.")

    except WebSocketDisconnect:
        broadcast_server.logger.info("A listener connection was disconnected.")

    except Exception as e:  # pylint: disable=broad-except
        msg = f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
        broadcast_server.logger.error(msg)

    finally:
        CONNECTED_CLIENTS.remove(broadcast_server)
        stream_task.cancel()
        await stream_task
        stdin_task.cancel()
        try:
            await stdin_task
        except asyncio.CancelledError:
            broadcast_server.logger.info("A listener task was cancelled.")


class BroadcastServer:  # pylint: disable=too-many-instance-attributes
    """Stream new results from a continuously written SQLite database.

    Not intended to be used directly, it is initialized by the server app when it accepts a new connection.
    It is responsible for reading the results database and sending new messages to the connected client(s).
    """

    def __init__(
        self,
        results_file,
        table_name,
        sleep_time: float = 0.25,
        auth_token: Optional[str] = None,
        sql_connect_kwargs: Optional[dict] = None,
        sql: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ):
        """Initialize the BroadcastServer instance."""
        self.results_file = results_file
        self.table_name = table_name
        self.logger = logger if logger else logging.getLogger("uvicorn.error")
        self.sleep_time = sleep_time
        self._app = app
        self._key = os.urandom(32)
        self._iv = os.urandom(16)
        self.auth_token = self._encrypt_value(auth_token) if auth_token else None
        self.websocket = None
        self.kwargs = kwargs
        self.sql_connect_kwargs = (
            sql_connect_kwargs if sql_connect_kwargs is not None else {}
        )
        self.database = Database(
            results_file=results_file,
            table_name=table_name,
            logger=self.logger,
            **sql_connect_kwargs or {},
        )
        self.sql = sql

    def _encrypt_value(self, value: str) -> str:
        """Encrypt the value for storage."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.websockets.helpers import encrypt_value

        return encrypt_value(self._key, self._iv, value)

    def _decrypt_value(self, value: str) -> str:
        """Decrypt the value for use."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.websockets.helpers import decrypt_value

        return decrypt_value(self._key, self._iv, value)

    async def stream_results(  # noqa: PLR0915  # pylint: disable=too-many-branches
        self,
        sql: Optional[str] = None,
        replay: bool = False,
    ):
        """Continuously read the database and send new messages as JSON via WebSocket."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite
        from openbb_core.app.model.abstract.error import OpenBBError

        file_path = Path(self.results_file).absolute()
        last_id = 0

        if not file_path.exists():
            self.logger.error("Results file not found: %s", str(file_path))
            return

        query = f"SELECT MAX(id) FROM {self.table_name}"  # noqa:S608

        async with self.database.get_connection("read") as conn:
            cursor = await conn.execute(query)
            last_id = (await cursor.fetchone())[0]
            await cursor.close()

        last_id = (
            0
            if hasattr(self, "replay") and self.replay is True or replay is True  # type: ignore
            else last_id
        )

        if sql and self.sql is None:
            self.sql = sql
        elif self.sql is not None and sql is None:
            sql = self.sql

        if sql and sql.lower().startswith("json_extract"):
            sql = f"SELECT * FROM {self.table_name} WHERE {sql}"  # noqa:S608

        if sql and (
            any(x.lower() in sql.lower() for x in CHECK_FOR)
            or (self.table_name not in sql and "message" not in sql)
        ):
            await self.websocket.accept()  # type: ignore
            await self.websocket.send_text("Invalid SQL query passed.")  # type: ignore
            await self.websocket.close(code=1008, reason="Invalid query")  # type: ignore
            self.logger.error(  # type: ignore
                "Invalid query passed to the stream_results method: %s", sql
            )
            return

        try:  # pylint: disable=too-many-nested-blocks
            while True:
                try:
                    async with self.database.get_connection("read") as conn:
                        query = (
                            sql.replace(";", "")
                            + f" {'AND' if 'WHERE' in sql else 'WHERE'} id > ?"
                            if sql is not None
                            else f"SELECT * FROM {self.table_name} WHERE id > ?"  # noqa:S608
                            + " ORDER BY json_extract (message, '$.date') ASC"
                        )
                        params = (last_id,)
                        cursor = await conn.execute(query, params)
                        rows = await cursor.fetchall()
                        if not rows:
                            await cursor.close()
                            await asyncio.sleep(1)
                            continue
                        for row in rows:
                            last_id = row[0] if row[0] > last_id else last_id
                            await self.websocket.send_json(  # type: ignore
                                json.dumps(json.loads(row[1]))
                            )
                            if self.replay is True:  # type: ignore
                                await asyncio.sleep(self.sleep_time / 10)
                        await cursor.close()

                    await asyncio.sleep(self.sleep_time)
                except KeyboardInterrupt:
                    self.logger.info("\nResults stream cancelled.")
                    break
                except aiosqlite.OperationalError as e:
                    if "no such table" in str(e):
                        self.logger.error(
                            "Results file was removed by the parent process."
                        )
                        break
                    raise OpenBBError(e) from e
                except asyncio.CancelledError:
                    break
        except WebSocketDisconnect:
            pass
        except Exception as e:  # pylint: disable=broad-except
            msg = f"{e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e}"
            self.logger.error(msg)
        finally:
            CONNECTED_CLIENTS.remove(self)
            self.logger.info("Listener connection was disconnected.")

    def start_app(self, host: str = "127.0.0.1", port: int = 6666):
        """Start the FastAPI app with Uvicorn."""
        uvicorn.run(
            self._app,
            host=host,
            port=port,
            **kwargs,
        )


def create_broadcast_server(
    results_file: str,
    table_name: str,
    sleep_time: float = 0.25,
    auth_token: Optional[str] = None,
    sql_connect_kwargs: Optional[dict] = None,
    sql: Optional[str] = None,
    **kwargs,
):
    """Create a new BroadcastServer instance."""
    return BroadcastServer(
        results_file,
        table_name,
        sleep_time,
        auth_token,
        sql_connect_kwargs,
        sql,
        **kwargs,
    )


def run_broadcast_server(broadcast_server, host, port, **kwargs):
    """Run the broadcast server."""
    broadcast_server.start_app(host=host, port=port, **kwargs)


async def main():
    """Run the main function."""
    import threading

    loop = asyncio.get_running_loop()

    STDIN_TASK = loop.create_task(read_stdin())

    broadcast_server = create_broadcast_server(
        RESULTS_FILE,
        TABLE_NAME,
        SLEEP_TIME,
        str(AUTH_TOKEN),
        SQL_CONNECT_KWARGS,
        SQL,
    )
    global MAIN_CLIENT  # noqa: PLW0603
    MAIN_CLIENT = broadcast_server
    try:
        broadcast_thread = threading.Thread(
            target=run_broadcast_server,
            args=(broadcast_server, HOST, PORT),
            kwargs=kwargs,
            daemon=True,
        )
        broadcast_thread.start()
        await asyncio.sleep(0.1)

        await asyncio.gather(STDIN_TASK, return_exceptions=True)

    except TypeError as e:
        msg = f"Invalid keyword argument passed to unvicorn. -> {e.args[0]}"
        broadcast_server.logger.error(msg)
    except KeyboardInterrupt:
        broadcast_server.logger.info("Broadcast server terminated.")
    finally:
        if STDIN_TASK:
            STDIN_TASK.cancel()
        broadcast_thread.join()

        loop.stop()
        loop.close()
        sys.exit(0)


if __name__ == "__main__":
    if not RESULTS_FILE:
        raise ValueError("Results file path is required for Broadcast server.")

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        sys.exit(0)
