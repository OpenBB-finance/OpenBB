"""WebSocket Client module for interacting with a provider websocket in a non-blocking pattern."""

# pylint: disable=too-many-statements
# flake8: noqa: PLR0915
import logging
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from openbb_core.provider.abstract.data import Data


class WebSocketClient:
    """Client for interacting with a websocket server in a non-blocking pattern.

    Parameters
    ----------
    name : str
        Name to assign the WebSocket connection. Used to identify and manage multiple instances.
    module : str
        The Python module for the provider server connection. Runs in a separate thread.
        Example: 'openbb_fmp.websockets.server'. Pass additional keyword arguments by including kwargs.
    symbol : Optional[str]
        The symbol(s) requested to subscribe. Enter multiple symbols separated by commas without spaces.
    limit : Optional[int]
        The limit of records to hold in memory. Once the limit is reached, the oldest records are removed.
        Default is None.
    results_file : Optional[str]
        Absolute path to the file for continuous writing. By default, a temporary file is created.
    table_name : Optional[str]
        SQL table name to store serialized data messages. By default, 'records'.
    save_results : bool
        Whether to persist the results after the main Python session ends. Default is False.
    data_model : Optional[Data]
        Pydantic data model to validate the results before storing them in the database.
        Also used to deserialize the results from the database.
    auth_token : Optional[str]
        The authentication token to use for the WebSocket connection. Default is None.
        Only used for API and Python application endpoints.
    logger : Optional[logging.Logger]
        The logger instance to use this connection. By default, a new logger is created.
    kwargs : dict
        Additional keyword arguments to pass to the target module.

    Properties
    ----------
    symbol : str
        Symbol(s) requested to subscribe.
    module : str
        Path to the provider connection script.
    is_running : bool
        Check if the provider connection is running.
    is_broadcasting : bool
        Check if the broadcast server is running.
    broadcast_address : str
        URI address for the results broadcast server.
    results : list
        All stored results from the provider's WebSocket stream. The results are stored in a SQLite database.
        Set the 'limit' property to cap the number of stored records.
        Clear the results by deleting the property. e.g., del client.results
    transformed_results : list
        Deserialize the records from the results file using the provided data model, if available.

    Methods
    -------
    connect
        Connect to the provider WebSocket stream.
    disconnect
        Disconnect from the provider WebSocket.
    subscribe
        Subscribe to a new symbol or list of symbols.
    unsubscribe
        Unsubscribe from a symbol or list of symbols.
    start_broadcasting
        Start the broadcast server to stream results over a network connection.
    stop_broadcasting
        Stop the broadcast server and disconnect all reading clients.
    send_message
        Send a message to the WebSocket process.
    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        module: str,
        symbol: Optional[str] = None,
        limit: Optional[int] = None,
        results_file: Optional[str] = None,
        table_name: Optional[str] = None,
        save_results: bool = False,
        data_model: Optional["Data"] = None,
        auth_token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ):
        """Initialize the WebSocketClient class."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import atexit
        import tempfile
        import threading
        from aiosqlite import DatabaseError
        from queue import Queue
        from pathlib import Path
        from openbb_websockets.helpers import get_logger

        self.name = name
        self.module = module.replace(".py", "")
        self.results_file = results_file if results_file else None
        self.table_name = table_name if table_name else "records"
        self._limit = limit
        self.data_model = data_model
        self._auth_token = auth_token
        self._symbol = symbol
        self._kwargs = (
            [f"{k}={str(v).strip().replace(" ", "_")}" for k, v in kwargs.items()]
            if kwargs
            else None
        )

        self._process = None
        self._psutil_process = None
        self._thread = None
        self._log_thread = None
        self._provider_message_queue = Queue()
        self._stop_log_thread_event = threading.Event()
        self._stop_broadcasting_event = threading.Event()
        self._broadcast_address = None
        self._broadcast_process = None
        self._psutil_broadcast_process = None
        self._broadcast_thread = None
        self._broadcast_log_thread = None
        self._broadcast_message_queue = Queue()

        if not results_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                pass
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path

        self.results_path = Path(self.results_file).absolute()
        self.save_results = save_results
        self.logger = logger if logger else get_logger("openbb.websocket.client")

        atexit.register(self._atexit)

        try:
            self._setup_database()
        except DatabaseError as e:
            self.logger.error("Error setting up the SQLite database and table: %s", e)

    def _atexit(self):
        """Clean up the WebSocket client processes at exit."""
        # pylint: disable=import-outside-toplevel
        import os

        if self.is_running:
            self.disconnect()
        if self.is_broadcasting:
            self.stop_broadcasting()
        if self.save_results:
            self.logger.info("Websocket results saved to, %s\n", self.results_file)
        if os.path.exists(self.results_file):
            os.remove(self.results_file)

    def _setup_database(self):
        """Set up the SQLite database and table."""
        # pylint: disable=import-outside-toplevel
        from openbb_websockets.helpers import setup_database

        return setup_database(self.results_path, self.table_name)

    def _log_provider_output(self, output_queue):
        """Log output from the provider server queue."""
        # pylint: disable=import-outside-toplevel
        import queue  # noqa
        import sys
        from openbb_websockets.helpers import clean_message

        while not self._stop_log_thread_event.is_set():
            try:
                output = output_queue.get(timeout=1)
                if output:
                    output = clean_message(output)
                    output = output + "\n"
                    sys.stdout.write(output + "\n")
                    sys.stdout.flush()
            except queue.Empty:
                continue

    def _log_broadcast_output(self, output_queue):
        """Log output from the broadcast server queue."""
        # pylint: disable=import-outside-toplevel
        import queue  # noqa
        import sys
        from openbb_websockets.helpers import clean_message

        while not self._stop_broadcasting_event.is_set():
            try:
                output = output_queue.get(timeout=1)

                if output and "Uvicorn running" in output:
                    address = (
                        output.split("Uvicorn running on ")[-1]
                        .strip()
                        .replace(" (Press CTRL+C to quit)", "")
                        .replace("http", "ws")
                    )
                    output = "INFO:     " + f"Stream results from {address}"
                    self._broadcast_address = address

                if output and "Started server process" in output:
                    output = None

                if output and "Waiting for application startup." in output:
                    output = None

                if output and "Application startup complete." in output:
                    output = None

                if output:
                    if "ERROR:" in output:
                        output = output.replace("ERROR:", "BROADCAST ERROR:") + "\n"
                    if "INFO:" in output:
                        output = output.replace("INFO:", "BROADCAST INFO:") + "\n"
                    output = output[0] if isinstance(output, tuple) else output
                    output = clean_message(output)
                    sys.stdout.write(output + "\n")
                    sys.stdout.flush()
            except queue.Empty:
                continue

    def connect(self):
        """Connect to the provider WebSocket."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import os
        import queue
        import subprocess
        import threading
        import psutil

        if self.is_running:
            self.logger.info("Provider connection already running.")
            return

        symbol = self.symbol

        if not symbol:
            self.logger.info("No subscribed symbols.")
            return

        command = self.module.copy()
        command.extend([f"symbol={symbol}"])
        command.extend([f"results_file={self.results_file}"])
        command.extend([f"table_name={self.table_name}"]),

        if self.limit:
            command.extend([f"limit={self.limit}"])

        if self._kwargs:
            for kwarg in self._kwargs:
                if kwarg not in command:
                    command.extend([kwarg])

        self._process = subprocess.Popen(  # noqa
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            env=os.environ,
            text=True,
            bufsize=1,
        )
        self._psutil_process = psutil.Process(self._process.pid)

        log_output_queue = queue.Queue()
        self._thread = threading.Thread(
            target=non_blocking_websocket,
            args=(
                self,
                log_output_queue,
                self._provider_message_queue,
            ),
        )
        self._thread.daemon = True
        self._thread.start()

        self._log_thread = threading.Thread(
            target=self._log_provider_output,
            args=(log_output_queue,),
        )
        self._log_thread.daemon = True
        self._log_thread.start()

        if not self.is_running:
            self.logger.error("The provider server failed to start.")

    def send_message(
        self, message, target: Literal["provider", "broadcast"] = "provider"
    ):
        """Send a message to the WebSocket process."""
        if target == "provider":
            self._provider_message_queue.put(message)
            read_message_queue(self, self._provider_message_queue)
        elif target == "broadcast":
            self._broadcast_message_queue.put(message)
            read_message_queue(self, self._broadcast_message_queue, target="broadcast")

    def disconnect(self):
        """Disconnect from the provider WebSocket."""
        self._stop_log_thread_event.set()
        if self._process is None or self.is_running is False:
            self.logger.info("Not connected to the provider WebSocket.")
            return
        if (
            self._psutil_process is not None
            and hasattr(self._psutil_process, "is_running")
            and self._psutil_process.is_running()
        ):
            self._psutil_process.kill()
        self._process.wait()
        self._thread.join()
        self._log_thread.join()
        self._stop_log_thread_event.clear()
        self.logger.info("Disconnected from the provider WebSocket.")
        return

    def subscribe(self, symbol):
        """Subscribe to a new symbol or list of symbols."""
        # pylint: disable=import-outside-toplevel
        import json

        ticker = symbol if isinstance(symbol, list) else symbol.split(",")
        msg = {"event": "subscribe", "symbol": ticker}
        self.send_message(json.dumps(msg))
        old_symbols = self.symbol.split(",")
        new_symbols = list(set(old_symbols + ticker))
        self._symbol = ",".join(new_symbols)

    def unsubscribe(self, symbol):
        """Unsubscribe from a symbol or list of symbols."""
        # pylint: disable=import-outside-toplevel
        import json

        if not self.symbol:
            self.logger.info("No subscribed symbols.")
            return

        ticker = symbol if isinstance(symbol, list) else symbol.split(",")
        msg = {"event": "unsubscribe", "symbol": ticker}
        self.send_message(json.dumps(msg))
        old_symbols = self.symbol.split(",")
        new_symbols = list(set(old_symbols) - set(ticker))
        self._symbol = ",".join(new_symbols)

    @property
    def is_running(self):
        """Check if the provider connection is running."""
        if hasattr(self._psutil_process, "is_running"):
            return self._psutil_process.is_running()
        return False

    @property
    def is_broadcasting(self):
        """Check if the broadcast server is running."""
        if hasattr(self._psutil_broadcast_process, "is_running"):
            return self._psutil_broadcast_process.is_running()
        return False

    @property
    def results(self):
        """Retrieve the raw results dumped by the WebSocket stream."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import sqlite3

        output: list = []
        file_path = self.results_path
        if file_path.exists():
            with sqlite3.connect(file_path) as conn:
                cursor = conn.execute(f"SELECT * FROM {self.table_name}")  # noqa
                for row in cursor:
                    index, message = row
                    output.append(json.loads(message))

            return output

        self.logger.info("No results found in %s", self.results_file)

        return []

    @results.deleter
    def results(self):
        """Clear results stored from the WebSocket stream."""
        # pylint: disable=import-outside-toplevel
        import sqlite3

        try:
            with sqlite3.connect(self.results_path) as conn:
                conn.execute(f"DELETE FROM {self.table_name}")  # noqa
                conn.commit()
            self._setup_database()
            self.logger.info(
                "Results cleared from table %s in %s",
                self.table_name,
                self.results_file,
            )
        except Exception as e:
            self.logger.error("Error clearing results: %s", e)

    @property
    def module(self):
        """Path to the provider connection script."""
        return self._module

    @module.setter
    def module(self, module):
        """Set the path to the provider connection script."""
        # pylint: disable=import-outside-toplevel
        import sys

        self._module = [
            sys.executable,
            "-m",
            module,
        ]

    @property
    def symbol(self):
        """Symbol(s) requested to subscribe."""
        return self._symbol

    @property
    def limit(self):
        """Get the limit of records to hold in memory."""
        return self._limit

    @limit.setter
    def limit(self, limit):
        """Set the limit of records to hold in memory."""
        self._limit = limit

    @property
    def broadcast_address(self):
        """Get the WebSocket broadcast address."""
        return (
            self._broadcast_address
            if self._broadcast_address and self.is_broadcasting
            else None
        )

    def start_broadcasting(
        self,
        host: str = "127.0.0.1",
        port: int = 6666,
        **kwargs,
    ):
        """Broadcast results over a network connection."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        import subprocess
        import sys
        import threading
        import psutil
        import queue
        from openbb_platform_api.utils.api import check_port

        if (
            self._broadcast_process is not None
            and self._broadcast_process.poll() is None
        ):
            self.logger.info(
                f"WebSocket broadcast already running on: {self._broadcast_address}"
            )
            return

        open_port = check_port(host, port)

        if open_port != port:
            msg = f"Port {port} is already in use. Using {open_port} instead."
            self.logger.warning(msg)

        command = [
            sys.executable,
            "-m",
            "openbb_websockets.broadcast",
            f"host={host}",
            f"port={open_port}",
            f"results_file={self.results_file}",
            f"table_name={self.table_name}",
            f"auth_token={self._auth_token}",
        ]
        if kwargs:
            for kwarg in kwargs:
                command.extend([f"{kwarg}={kwargs[kwarg]}"])

        self._broadcast_process = subprocess.Popen(  # noqa
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            env=os.environ,
            text=True,
            bufsize=1,
        )
        self._psutil_broadcast_process = psutil.Process(self._broadcast_process.pid)
        output_queue = queue.Queue()
        self._broadcast_thread = threading.Thread(
            target=non_blocking_broadcast,
            args=(
                self,
                output_queue,
                self._broadcast_message_queue,
            ),
        )
        self._broadcast_thread.daemon = True
        self._broadcast_thread.start()

        self._broadcast_log_thread = threading.Thread(
            target=self._log_broadcast_output,
            args=(output_queue,),
        )
        self._broadcast_log_thread.daemon = True
        self._broadcast_log_thread.start()

        if not self.is_broadcasting:
            self.logger.error(
                "The broadcast server failed to start on: %s",
                self._broadcast_address,
            )

    def stop_broadcasting(self):
        """Stop the broadcast server."""
        broadcast_address = self._broadcast_address
        self._stop_broadcasting_event.set()
        if self._broadcast_process is None or self.is_broadcasting is False:
            self.logger.info("Not currently broadcasting.")
            return
        if (
            self._psutil_broadcast_process is not None
            and hasattr(self._psutil_broadcast_process, "is_running")
            and self._psutil_broadcast_process.is_running()
        ):
            self._psutil_broadcast_process.kill()
            if broadcast_address:
                self.logger.info("Stopped broadcasting to: %s", broadcast_address)

        self._broadcast_process.wait()
        self._broadcast_thread.join()
        self._broadcast_log_thread.join()
        self._broadcast_process = None
        self._psutil_broadcast_process = None
        self._broadcast_address = None
        self._stop_broadcasting_event.clear()
        return

    @property
    def transformed_results(self):
        """Deserialize the records from the results file."""
        # pylint: disable=import-outside-toplevel
        import json

        if not self.data_model:
            raise NotImplementedError("No model provided to transform the results.")

        return [self.data_model.model_validate(json.loads(d)) for d in self.results]

    def __repr__(self):
        """Return the WebSocketClient representation."""
        return (
            f"WebSocketClient(module={self.module}, symbol={self.symbol}, "
            f"is_running={self.is_running}, provider_pid: "
            f"{self._psutil_process.pid if self._psutil_process else ''}, is_broadcasting={self.is_broadcasting}, "
            f"broadcast_address={self.broadcast_address}, "
            f"broadcast_pid: {self._psutil_broadcast_process.pid if self._psutil_broadcast_process else ''}, "
            f"results_file={self.results_file}, table_name={self.table_name}, "
            f"save_results={self.save_results})"
        )


def non_blocking_websocket(client, output_queue, provider_message_queue):
    """Communicate with the threaded process."""
    try:
        while not client._stop_log_thread_event.is_set():
            while not provider_message_queue.empty():
                read_message_queue(client, provider_message_queue)
            output = client._process.stdout.readline()
            if output == "" and client._process.poll() is not None:
                break
            if output:
                output_queue.put(output.strip())

    except Exception as e:
        raise e from e
        client.logger.error(f"Error in non_blocking_websocket: {e}")
    finally:
        client._process.stdout.close()
        client._process.wait()


def send_message(
    client, message, target: Literal["provider", "broadcast"] = "provider"
):
    """Send a message to the WebSocket process."""
    try:
        if target == "provider":
            if client._process and client._process.stdin:
                client._process.stdin.write(message + "\n")
                client._process.stdin.flush()
            else:
                client.logger.error("Provider process is not running.")
        elif target == "broadcast":
            if client._broadcast_process and client._broadcast_process.stdin:
                client._broadcast_process.stdin.write(message + "\n")
                client._broadcast_process.stdin.flush()
            else:
                client.logger.error("Broadcast process is not running.")
    except Exception as e:
        client.logger.error(f"Error sending message to WebSocket process: {e}")


def read_message_queue(
    client, message_queue, target: Literal["provider", "broadcast"] = "provider"
):
    """Read messages from the queue and send them to the WebSocket process."""
    while not message_queue.empty():
        try:
            if target == "provider":
                while not client._stop_log_thread_event.is_set():
                    message = message_queue.get(timeout=1)
                    if message:
                        send_message(client, message, target="provider")
            elif target == "broadcast":
                while not client._stop_broadcasting_event.is_set():
                    message = message_queue.get(timeout=1)
                    if message:
                        send_message(client, message, target="broadcast")
        except Exception as e:
            err = f"Error reading message queue: {e.args[0]} -> {message}"
            client.logger.error(err)
        finally:
            break


def non_blocking_broadcast(client, output_queue, broadcast_message_queue):
    """Continuously read the output from the broadcast process and log it to the main thread."""
    try:
        while not client._stop_broadcasting_event.is_set():
            while not broadcast_message_queue.empty():
                read_message_queue(client, broadcast_message_queue, target="broadcast")

            output = client._broadcast_process.stdout.readline()
            if output == "" and client._broadcast_process.poll() is not None:
                break
            if output:
                output_queue.put(output.strip())
    except Exception as e:
        client.logger.error(f"Error in non_blocking_broadcast: {e}")
    finally:
        client._broadcast_process.stdout.close()
        client._broadcast_process.wait()
