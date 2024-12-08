"""WebSocket Client module for interacting with a provider websocket in a non-blocking pattern."""

# pylint: disable=too-many-statements
# flake8: noqa: PLR0915

import logging
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

if TYPE_CHECKING:
    from openbb_core.provider.abstract.data import Data


class WebSocketClient:
    """Client for interacting with a websocket server in a non-blocking pattern.

    Parameters
    ----------
    name : str
        Name to assign the WebSocket connection. Used to identify and manage multiple instances.
    module : str
        The Python module for the provider websocket_client module. Runs in a separate thread.
        Example: 'openbb_fmp.utils.websocket_client'. Pass additional keyword arguments by including kwargs.
    symbol : Optional[str]
        The symbol(s) requested to subscribe. Enter multiple symbols separated by commas without spaces.
    limit : Optional[int]
        The limit of records to hold in memory. Once the limit is reached, the oldest records are removed.
        Default is 1000. Set to None to keep all records.
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
        The pre-configured logger instance to use for this connection. By default, a new logger is created.
    kwargs : Optional[dict]
        Additional keyword arguments to pass to the target provider module. Keywords and values must not contain spaces.
        To pass items to 'websocket.connect()', include them in the 'kwargs' dictionary as,
        {'connect_kwargs': {'key': 'value'}}.

    Properties
    ----------
    symbol : str
        Symbol(s) requested to subscribe.
    module : str
        Path to the provider connection script.
    is_running : bool
        Check if the provider connection process is running.
    is_broadcasting : bool
        Check if the broadcast server process is running.
    broadcast_address : str
        URI address for the results broadcast server.
    results : list[Data]
        All stored results from the provider's WebSocket stream.
        Results are stored in a SQLite database as a serialized JSON string, this property deserializes the results.
        Clear the results by deleting the property. e.g., del client.results

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
        Stop the broadcast server and disconnect all listening clients.
    send_message
        Send a message to the WebSocket process. Messages can be sent to "provider" or "broadcast" targets.
    """

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        module: str,
        symbol: Optional[str] = None,
        limit: Optional[int] = 1000,
        results_file: Optional[str] = None,
        table_name: Optional[str] = None,
        save_results: bool = False,
        data_model: Optional["Data"] = None,
        auth_token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ) -> None:
        """Initialize the WebSocketClient class."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import atexit
        import os
        import tempfile
        import threading
        from aiosqlite import DatabaseError
        from queue import Queue
        from pathlib import Path
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_websockets.helpers import get_logger

        self.name = name
        self.module = module.replace(".py", "")
        self.results_file = results_file if results_file else None
        self.table_name = table_name if table_name else "records"
        self._limit = limit
        self.data_model = data_model
        self._symbol = symbol
        self._key = os.urandom(32)
        self._iv = os.urandom(16)
        self._auth_token = self._encrypt_value(auth_token) if auth_token else None
        # strings in kwargs are encrypted before storing in the class but unencrypted when passed to the provider module.
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, str):
                    encrypted_value = self._encrypt_value(v)
                    kwargs[k] = encrypted_value
                else:
                    kwargs[k] = v

        self._kwargs = kwargs if kwargs else {}

        self._process: Any = None
        self._psutil_process: Any = None
        self._thread: Any = None
        self._log_thread: Any = None
        self._provider_message_queue: Queue = Queue()
        self._stop_log_thread_event: threading.Event = threading.Event()
        self._stop_broadcasting_event: threading.Event = threading.Event()
        self._broadcast_address: Any = None
        self._broadcast_process: Any = None
        self._psutil_broadcast_process: Any = None
        self._broadcast_thread: Any = None
        self._broadcast_log_thread: Any = None
        self._broadcast_message_queue: Queue = Queue()
        self._exception: Any = None

        if not results_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                pass
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path

        self.results_path = Path(self.results_file).absolute()  # type: ignore
        self.save_results = save_results
        self.logger = logger if logger else get_logger("openbb.websocket.client")

        atexit.register(self._atexit)

        try:
            self._setup_database()
        except DatabaseError as e:
            msg = f"Unexpected error setting up the SQLite database and table -> {e.__class___.__name__}: {e}"
            self.logger.error(msg)
            self._exception = OpenBBError(msg)

    def _encrypt_value(self, value):
        """Encrypt a value before storing."""
        # pylint: disable=import-outside-toplevel
        from openbb_websockets.helpers import encrypt_value

        return encrypt_value(self._key, self._iv, value)

    def _decrypt_value(self, encrypted_value):
        """Decrypt the value for use."""
        # pylint: disable=import-outside-toplevel
        from openbb_websockets.helpers import decrypt_value

        return decrypt_value(self._key, self._iv, encrypted_value)

    def _atexit(self) -> None:
        """Clean up the WebSocket client processes at exit."""
        # pylint: disable=import-outside-toplevel
        import os

        self._exception = None

        if self.is_running:
            self.disconnect()
        if self.is_broadcasting:
            self.stop_broadcasting()
        if self.save_results:
            self.logger.info("Websocket results saved to, %s\n", str(self.results_path))
        if os.path.exists(self.results_file) and not self.save_results:  # type: ignore
            os.remove(self.results_file)  # type: ignore

    def _setup_database(self) -> None:
        """Set up the SQLite database and table."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import threading
        import time
        from openbb_websockets.helpers import setup_database

        def run_in_new_loop():
            """Run setup in new event loop."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    setup_database(self.results_path, self.table_name)
                )
            finally:
                loop.close()

        def run_in_thread():
            """Run setup in separate thread."""
            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            time.sleep(0.01)
            thread.join()

        try:
            loop = asyncio.get_running_loop()  # noqa
            run_in_thread()
        except RuntimeError:
            run_in_new_loop()

    def _log_provider_output(self, output_queue) -> None:
        """Log output from the provider logger, handling exceptions, errors, and messages that are not data."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import queue
        import sys
        from openbb_core.provider.utils.errors import UnauthorizedError
        from openbb_websockets.helpers import clean_message
        from pydantic import ValidationError

        while not self._stop_log_thread_event.is_set():
            try:
                output = output_queue.get(timeout=1)
                if output:
                    # Handle raised exceptions from the provider connection thread, killing the process if required.
                    # UnauthorizedError should be raised by the parent thread, but we kill the process here.
                    if "UnauthorizedError" in output:
                        self._psutil_process.kill()
                        self._process.wait()
                        self._thread.join()
                        err = UnauthorizedError(output)
                        self._exception = err
                        sys.stdout.write(output + "\n")
                        sys.stdout.flush()
                        break
                    # ValidationError may occur after the provider connection is established.
                    # We write to stdout in case the exception can't be raised before the main function returns.
                    # We kill the connection here.
                    if "ValidationError" in output:
                        self._psutil_process.kill()
                        self._process.wait()
                        self._thread.join()
                        title, errors = output.split(" -> ")[-1].split(": ")
                        line_errors = json.loads(errors.strip())
                        err = ValidationError.from_exception_data(
                            title=title.strip(), line_errors=line_errors
                        )
                        self._exception = err
                        msg = (
                            "PROVIDER ERROR:     Disconnecting because a ValidatonError was raised"
                            + " by the provider while processing data."
                            + f"\n\n{str(err)}\n"
                        )
                        sys.stdout.write(msg + "\n")
                        sys.stdout.flush()
                        break
                    # We don't kill the process on SymbolError, but raise the exception in the main thread instead.
                    # This is likely a subscribe event and the connection is already streaming.
                    if "SymbolError" in output:
                        err = ValueError(output)
                        self._exception = err
                        continue
                    # Other errors are logged to stdout and the process is killed.
                    # If the exception is raised by the parent thread, it will be treated as an unexpected error.
                    if (
                        "server rejected" in output.lower()
                        or "PROVIDER ERROR" in output
                        or "unexpected error" in output.lower()
                    ):
                        self._psutil_process.kill()
                        self._process.wait()
                        self._thread.join()
                        err = ChildProcessError(output)
                        self._exception = err
                        output = output + "\n"
                        sys.stdout.write(output)
                        sys.stdout.flush()
                        break

                    output = clean_message(output)

                    if output.startswith("ERROR:"):
                        output = output.replace("ERROR:", "PROVIDER ERROR:")
                    elif output.startswith("INFO:"):
                        output = output.replace("INFO:", "PROVIDER INFO:")

                    self.logger.info(output)
            except queue.Empty:
                continue

    def _log_broadcast_output(self, output_queue) -> None:
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
                    if output.startswith("ERROR:"):
                        output = output.replace("ERROR:", "BROADCAST ERROR:") + "\n"
                    elif output.startswith("INFO:"):
                        output = output.replace("INFO:", "BROADCAST INFO:") + "\n"
                    output = output[0] if isinstance(output, tuple) else output
                    output = clean_message(output)
                    sys.stdout.write(output + "\n")
                    sys.stdout.flush()
            except queue.Empty:
                continue

    def connect(self) -> None:
        """Connect to the provider WebSocket."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import os
        import psutil
        import queue
        import subprocess
        import threading
        import time
        from openbb_core.app.model.abstract.error import OpenBBError

        if self.is_running:
            self.logger.info("Provider connection already running.")
            return

        symbol = self.symbol

        if not symbol:
            self.logger.info("No subscribed symbols.")
            return

        command = self.module
        command.extend([f"symbol={symbol}"])
        command.extend([f"results_file={self.results_file}"])
        command.extend([f"table_name={self.table_name}"]),

        if self.limit:
            command.extend([f"limit={self.limit}"])

        kwargs = self._kwargs.copy()

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, str):
                    unencrypted_value = self._decrypt_value(v)
                    kwargs[k] = unencrypted_value
                else:
                    kwargs[k] = v

            _kwargs = (
                [f"{k}={str(v).strip().replace(' ', '_')}" for k, v in kwargs.items()]
                if kwargs
                else None
            )
            if _kwargs is not None:
                for kwarg in _kwargs:
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

        log_output_queue: queue.Queue = queue.Queue()
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

        # Give it some startup time to allow the connection to be established and for exceptions to populate.
        time.sleep(2)

        if self._exception is not None:
            exc = getattr(self, "_exception", None)
            self._exception = None
            raise OpenBBError(exc)

        if not self.is_running:
            self.logger.error("The provider server failed to start.")

    def send_message(
        self, message, target: Literal["provider", "broadcast"] = "provider"
    ) -> None:
        """Send a message to the WebSocket process."""
        if target == "provider":
            self._provider_message_queue.put(message)
            read_message_queue(self, self._provider_message_queue)
        elif target == "broadcast":
            self._broadcast_message_queue.put(message)
            read_message_queue(self, self._broadcast_message_queue, target="broadcast")

    def disconnect(self) -> None:
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
        if hasattr(self, "_exception") and self._exception:
            raise self._exception
        return

    def subscribe(self, symbol) -> None:
        """Subscribe to a new symbol or list of symbols."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import time
        from openbb_core.app.model.abstract.error import OpenBBError

        if not self.is_running:
            raise OpenBBError("Provider connection is not running.")

        ticker = symbol if isinstance(symbol, list) else symbol.split(",")
        msg = {"event": "subscribe", "symbol": ticker}
        self.send_message(json.dumps(msg))
        time.sleep(0.1)
        if self._exception:
            exc = getattr(self, "_exception", None)
            self._exception = None
            raise OpenBBError(exc)
        old_symbols = self.symbol.split(",")
        new_symbols = list(set(old_symbols + ticker))
        self._symbol = ",".join(new_symbols)

    def unsubscribe(self, symbol) -> None:
        """Unsubscribe from a symbol or list of symbols."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import time
        from openbb_core.app.model.abstract.error import OpenBBError

        if not self.symbol:
            self.logger.info("No subscribed symbols.")
            return

        if not self.is_running:
            raise OpenBBError("Provider connection is not running.")

        ticker = symbol if isinstance(symbol, list) else symbol.split(",")
        msg = {"event": "unsubscribe", "symbol": ticker}
        self.send_message(json.dumps(msg))
        time.sleep(0.1)
        old_symbols = self.symbol.split(",")
        new_symbols = list(set(old_symbols) - set(ticker))
        self._symbol = ",".join(new_symbols)

    @property
    def is_running(self) -> bool:
        """Check if the provider connection is running."""
        if hasattr(self._psutil_process, "is_running"):
            return self._psutil_process.is_running()
        return False

    @property
    def is_broadcasting(self) -> bool:
        """Check if the broadcast server is running."""
        if hasattr(self._psutil_broadcast_process, "is_running"):
            return self._psutil_broadcast_process.is_running()
        return False

    @property
    def results(self) -> Union[list[dict], list["Data"], None]:
        """Retrieve the deserialized results from the results file."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import sqlite3
        from openbb_core.app.model.abstract.error import OpenBBError

        output: list = []
        file_path = self.results_path
        if file_path.exists():
            with sqlite3.connect(file_path) as conn:
                try:
                    cursor = conn.execute(f"SELECT * FROM {self.table_name}")  # noqa
                    for row in cursor:
                        index, message = row
                        if self.data_model:
                            message = json.loads(message)
                            if isinstance(message, (str, bytes)):
                                output.append(
                                    self.data_model.model_validate_json(message)
                                )
                            elif isinstance(message, dict):
                                output.append(self.data_model(**message))
                        else:
                            output.append(json.loads(json.loads(message)))
                except Exception as e:
                    raise OpenBBError(f"Error retrieving results: {e}")
        if output:
            return output

        self.logger.info("No results found in %s", self.results_file)

        return None

    @results.deleter
    def results(self):
        """Clear results stored from the WebSocket stream."""
        # pylint: disable=import-outside-toplevel
        import sqlite3  # noqa

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
    def module(self) -> list:
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
    def symbol(self) -> Union[str, None]:
        """Symbol(s) requested to subscribe."""
        return self._symbol

    @property
    def limit(self) -> Union[int, None]:
        """Get the limit of records to hold in memory."""
        return self._limit

    @limit.setter
    def limit(self, limit):
        """Set the limit of records to hold in memory."""
        self._limit = limit

    @property
    def broadcast_address(self) -> Union[str, None]:
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
    ) -> None:
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
            f"auth_token={self._decrypt_value(self._auth_token) if self._auth_token else None}",
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
        output_queue: queue.Queue = queue.Queue()
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


def non_blocking_websocket(client, output_queue, provider_message_queue) -> None:
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
        client.logger.error(
            f"Unexpected error in non_blocking_websocket: {e.__class__.__name__} -> {e}"
        )
        raise e from e
    finally:
        client._process.stdout.close()
        client._process.wait()


def send_message(
    client, message, target: Literal["provider", "broadcast"] = "provider"
) -> None:
    """Send a message to the WebSocketConnection process."""
    # pylint: disable=import-outside-toplevel
    import json

    if isinstance(message, (dict, list)):
        message = json.dumps(message)
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
        msg = f"Error sending message to the {target} process: {e.__class__.__name__} -> {e}"
        client.logger.error(msg)


def read_message_queue(
    client, message_queue, target: Literal["provider", "broadcast"] = "provider"
):
    """Read messages from the queue and send them to the WebSocketConnection process."""
    while not message_queue.empty():
        try:
            message = message_queue.get(timeout=1)
            if message:
                try:
                    if (
                        target == "provider"
                        and not client._stop_log_thread_event.is_set()
                    ):
                        send_message(client, message, target="provider")
                    elif (
                        target == "broadcast"
                        and not client._stop_broadcasting_event.is_set()
                    ):
                        send_message(client, message, target="broadcast")
                except Exception as e:
                    err = (
                        f"Error while attempting to transmit from the outgoing message queue: {e.__class__.__name__} "
                        f"-> {e} -> {message}"
                    )
                    client.logger.error(err)
        finally:
            break


def non_blocking_broadcast(client, output_queue, broadcast_message_queue) -> None:
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
        client.logger.error(
            f"Unexpected error in non_blocking_broadcast: {e.__class__.__name__} -> {e}"
        )
    finally:
        client._broadcast_process.stdout.close()
        client._broadcast_process.wait()
