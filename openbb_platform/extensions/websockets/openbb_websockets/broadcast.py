import asyncio
import json
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from openbb_websockets.helpers import get_logger, parse_kwargs

connected_clients = set()

kwargs = parse_kwargs()

HOST = kwargs.pop("host", None) or "localhost"
PORT = kwargs.pop("port", None) or 6666
PORT = int(PORT)

RESULTS_FILE = kwargs.pop("results_file", None)
TABLE_NAME = kwargs.pop("table_name", None) or "records"
SLEEP_TIME = kwargs.pop("sleep_time", None) or 0.25
AUTH_TOKEN = kwargs.pop("auth_token", None)

app = FastAPI()


@app.websocket("/")
async def websocket_endpoint(  # noqa: PLR0915
    websocket: WebSocket, auth_token: Optional[str] = None
):

    broadcast_server = BroadcastServer(
        RESULTS_FILE,
        TABLE_NAME,
        SLEEP_TIME,
        str(AUTH_TOKEN),
    )
    auth_token = str(auth_token)

    if (
        broadcast_server.auth_token is not None
        and auth_token != broadcast_server.auth_token
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
    try:
        await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        broadcast_server.logger.error(f"Unexpected error: {e}")
        pass
    finally:
        if broadcast_server in connected_clients:
            connected_clients.remove(broadcast_server)
        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            broadcast_server.logger.info("Stream task cancelled")
        except Exception as e:
            broadcast_server.logger.error(f"Error while cancelling stream task: {e}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except RuntimeError as e:
                broadcast_server.logger.error(f"Error while closing websocket: {e}")


class BroadcastServer:
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

        self.results_file = results_file
        self.table_name = table_name
        self.logger = get_logger("openbb.websocket.broadcast_server")
        self.sleep_time = sleep_time
        self.auth_token = auth_token
        self._app = app
        self.websocket = None

    async def stream_results(self):  # noqa: PLR0915
        """Continuously read the database and send new messages as JSON via WebSocket."""
        import sqlite3  # noqa
        from pathlib import Path
        from openbb_core.app.model.abstract.error import OpenBBError

        file_path = Path(self.results_file).absolute()
        last_id = 0

        if not file_path.exists():
            self.logger.error(f"Results file not found: {file_path}")
            return
        else:
            conn = sqlite3.connect(self.results_file)
            cursor = conn.cursor()
            cursor.execute(f"SELECT MAX(id) FROM {self.table_name}")  # noqa:S608
            last_id = cursor.fetchone()[0] or 0
            conn.close()

        try:
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
                                index, message = row
                                await self.broadcast(json.dumps(json.loads(message)))
                            last_id = max(row[0] for row in rows)
                    else:
                        self.logger.error(f"Results file not found: {file_path}")
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
                    else:
                        raise OpenBBError(e) from e
                except asyncio.CancelledError:
                    break
        except WebSocketDisconnect:
            pass
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            return

    async def broadcast(self, message: str):
        """Broadcast a message to all connected connected clients."""
        disconnected_clients = set()
        for client in connected_clients.copy():
            try:
                await client.websocket.send_text(message)
            except WebSocketDisconnect:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                disconnected_clients.add(client)
        # Remove disconnected connected clients
        for client in disconnected_clients:
            connected_clients.remove(client)

    def start_app(self, host: str = "127.0.0.1", port: int = 6666, **kwargs):
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
    **kwargs,
):
    return BroadcastServer(results_file, table_name, sleep_time, auth_token)


def main():
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
        broadcast_server.logger.error(
            f"Invalid keyword argument passed to unvicorn. -> {e.args[0]}\n"
        )
    except KeyboardInterrupt:
        broadcast_server.logger.info("Broadcast server terminated.")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
