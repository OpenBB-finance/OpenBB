"""Broadcast server for streaming results to connected clients via WebSocket."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openbb_core.provider.utils.websockets.database import Database
from openbb_core.provider.utils.websockets.helpers import get_logger, parse_kwargs
from starlette.websockets import WebSocketState

connected_clients: set = set()

kwargs = parse_kwargs()

HOST = kwargs.pop("host", None) or "localhost"
PORT = kwargs.pop("port", None) or 6666
PORT = int(PORT)

RESULTS_FILE = kwargs.pop("results_file", None)
TABLE_NAME = kwargs.pop("table_name", None) or "records"
SLEEP_TIME = kwargs.pop("sleep_time", None) or 0.25
AUTH_TOKEN = kwargs.pop("auth_token", None)

DATABASE = Database(results_file=RESULTS_FILE, table_name=TABLE_NAME)

app = FastAPI()


async def read_stdin(broadcast_server):
    """Read from stdin."""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        sys.stdin.flush()

        if not line:
            break

        try:
            command = (
                json.loads(line.strip())
                if line.strip().startswith("{") or line.strip().startswith("[")
                else line.strip()
            )
            await broadcast_server.broadcast(json.dumps(command))
        except json.JSONDecodeError:
            broadcast_server.logger.error("Invalid JSON received from stdin")


@app.websocket("/")
async def websocket_endpoint(  # noqa: PLR0915
    websocket: WebSocket, auth_token: Optional[str] = None
):
    """Connect to the broadcast server."""

    broadcast_server = BroadcastServer(
        RESULTS_FILE,
        TABLE_NAME,
        SLEEP_TIME,
        str(AUTH_TOKEN),
    )
    auth_token = str(auth_token)

    if (
        broadcast_server.auth_token is not None
        and auth_token
        != broadcast_server._decrypt_value(  # pylint: disable=protected-access
            broadcast_server.auth_token
        )
    ):
        await websocket.accept()
        await websocket.send_text(
            "ERROR:    Invalid authentication token. Could not connect to the broadcast."
        )
        broadcast_server.logger.error(
            "ERROR:    Invalid authentication token passed by a client connecting."
        )
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    await websocket.accept()

    if RESULTS_FILE is None:
        raise ValueError("Results file path is required for WebSocket server.")

    broadcast_server.websocket = websocket
    connected_clients.add(broadcast_server)

    stream_task = asyncio.create_task(broadcast_server.stream_results())
    stdin_task = asyncio.create_task(read_stdin(broadcast_server))
    try:
        await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    except Exception as e:  # pylint: disable=broad-except
        msg = f"Unexpected error: {e.__class__.__name__} -> {e}"
        broadcast_server.logger.error(msg)
    finally:
        if broadcast_server in connected_clients:
            connected_clients.remove(broadcast_server)
        stream_task.cancel()
        stdin_task.cancel()
        try:
            await stream_task
            await stdin_task
        except asyncio.CancelledError:
            broadcast_server.logger.info("INFO:     A listener task was cancelled.")
        except Exception as e:  # pylint: disable=broad-except
            msg = f"Unexpected error while cancelling stream task: {e.__class__.__name__} -> {e}"
            broadcast_server.logger.error(msg)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except RuntimeError as e:
                msg = f"Unexpected error while closing websocket: {e.__class__.__name__} -> {e}"
                broadcast_server.logger.error(msg)


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
    ):
        """Initialize the BroadcastServer instance."""
        # pylint: disable=import-outside-toplevel
        import os

        self.results_file = results_file
        self.table_name = table_name
        self.logger = get_logger("openbb.websocket.broadcast_server")
        self.sleep_time = sleep_time
        self._app = app
        self._key = os.urandom(32)
        self._iv = os.urandom(16)
        self.auth_token = self._encrypt_value(auth_token) if auth_token else None
        self.websocket = None
        self.kwargs = kwargs

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
    ):
        """Continuously read the database and send new messages as JSON via WebSocket."""
        # pylint: disable=import-outside-toplevel
        import sqlite3  # noqa
        from openbb_core.app.model.abstract.error import OpenBBError

        file_path = Path(self.results_file).absolute()
        last_id = 0

        if not file_path.exists():
            self.logger.error("Results file not found: %s", str(file_path))
            return
        conn = sqlite3.connect(self.results_file)
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX(id) FROM {self.table_name}")  # noqa:S608
        last_id = cursor.fetchone()[0] or 0
        conn.close()

        try:  # pylint: disable=too-many-nested-blocks
            while True:
                try:
                    if file_path.exists():
                        conn = sqlite3.connect(self.results_file)
                        cursor = conn.cursor()
                        cursor.execute(
                            f"SELECT * FROM {self.table_name} WHERE id > ?",  # noqa:S608
                            (last_id,),
                        )
                        rows = cursor.fetchall()
                        conn.close()

                        if rows:
                            for row in rows:
                                _, message = row
                                await self.broadcast(json.dumps(json.loads(message)))
                            last_id = max(row[0] for row in rows)
                    else:
                        self.logger.error("Results file not found: %s", str(file_path))
                        break

                    await asyncio.sleep(self.sleep_time)
                except KeyboardInterrupt:
                    self.logger.info("\nResults stream cancelled.")
                    break
                except sqlite3.OperationalError as e:
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
            msg = f"Unexpected error: {e.__class__.__name__} -> {e}"
            self.logger.error(msg)
        return

    async def broadcast(self, message: str):
        """Broadcast a message to all connected connected clients."""
        disconnected_clients = set()
        for client in connected_clients.copy():
            try:
                await client.websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected_clients.add(client)
            except Exception as e:  # pylint: disable=broad-except
                msg = f"Unexpected error: {e.__class__.__name__} -> {e}"
                self.logger.error(msg)
                disconnected_clients.add(client)
        # Remove disconnected connected clients
        for client in disconnected_clients:
            connected_clients.remove(client)

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
):
    """Create a new BroadcastServer instance."""
    return BroadcastServer(results_file, table_name, sleep_time, auth_token)


def main():
    """Run the main function."""
    broadcast_server = create_broadcast_server(
        RESULTS_FILE,
        TABLE_NAME,
        SLEEP_TIME,
        str(AUTH_TOKEN),
    )

    try:
        broadcast_server.start_app(
            host=HOST,
            port=PORT,
            **kwargs,
        )
    except TypeError as e:
        msg = (
            f"ERROR:     Invalid keyword argument passed to unvicorn. -> {e.args[0]}\n"
        )
        broadcast_server.logger.error(msg)
    except KeyboardInterrupt:
        broadcast_server.logger.info("INFO:      Broadcast server terminated.")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    if not RESULTS_FILE:
        raise ValueError("Results file path is required for Broadcast server.")

    if not Path(RESULTS_FILE).absolute().exists():
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async

        run_async(DATABASE._setup_database)
    main()
