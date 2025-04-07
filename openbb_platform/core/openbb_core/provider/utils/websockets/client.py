"""Module for running OpenBB Provider websocket connection scripts."""

# pylint: disable=too-many-statements,protected-access
# flake8: noqa: PLR0915

from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError

if TYPE_CHECKING:
    import logging

    from pydantic import BaseModel


class WebSocketClient:  # pylint: disable=too-many-instance-attributes
    """
    Client for interacting with a websocket server in a non-blocking pattern, and handling the subprocesses.

    Parameters
    ----------
    name : str
        Name to assign the WebSocket connection. Used to identify and manage multiple instances from the API.
    module : str
        The Python module for the provider websocket_client module.
        Runs in a separate thread, and is an equivalent to 'python -m module'.
        Example: 'openbb_fmp.utils.websocket_client'.
        Pass additional keyword arguments to the script by including **kwargs.
    symbol : Optional[str]
        The symbol(s) requested to subscribe on start. Enter multiple symbols separated by commas, without spaces.
        Where supported by the provider, * represents all symbols within the feed.
    limit : Optional[int]
        The limit of records to store. Once the limit is reached, a one-in-one-out policy is used.
        A limit of None is the most efficient setting, but requires adequate disk storage to handle high volume.
        Default is 5000. Set to None to keep all records.
    results_file : Optional[str]
        Absolute path to the file for continuous writing. By default, a temporary file is created.
        File is discarded when the Python session ends unless 'save_database' is set to True.
        The connection can be re-established with the same results file to continue writing.
        EACH NEW CONNECTION SHOULD HAVE A UNIQUE RESULTS FILE.
        If the intention is to permanently store the results for historical records,
        save the current session to a new file and copy new records at periodic intervals into the master.
    table_name : Optional[str]
        SQL table name to store serialized data messages. By default, 'records'.
    save_database : bool
        Whether to persist the results after exiting. Default is False.
    data_model : Optional[BaseModel]
        Pydantic data model to validate the results before storing them in the database.
    auth_token : Optional[str]
        Used to limit access to the broadcast stream. When provided, listeners should supply as a URL parameter.
        Example: 'ws://127.0.0.1:6666/?auth_token=SOME_TOKEN'.
        When provided, the auth_token is required to interact with the instance of this class
        from the REST API and Python application endpoints.
    logger : Optional[logging.Logger]
        A pre-configured logger to use for this instance. By default, a new logger is created.
    kwargs : Optional[dict]
        Additional keyword arguments to pass to the target provider module. Keywords and values must not contain spaces.
        To pass items to 'websocket.connect()', include them in the 'kwargs' dictionary as a nested dictionary,
        with key, 'connect_kwargs'.
            {'api_key': 'MY_API_KEY', 'connect_kwargs': {'key': 'value'}}.

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
    is_exporting : bool
        Check if the export thread is running.
    broadcast_address : str
        URI address for connecting to the broadcast stream.
    num_results : int
        Number of results stored in the database.
    results : list[Data]
        All stored results from the provider connection.
        Clear the results by deleting the property. e.g., del client.results

    Methods
    -------
    connect
        Connect to the provider WebSocket stream.
    disconnect
        Disconnect from the provider WebSocket.
    subscribe
        Send a subscribe message to the provider connection.
    unsubscribe
        Send an unsubscribe message to the provider connection.
    start_broadcasting
        Start the broadcast server to stream results over a network.
    stop_broadcasting
        Stop the broadcast server and disconnect all listening clients.
    send_message
        Send a message to the WebSocket process. Messages can be sent to "provider" or "broadcast" targets.
    get_latest_results
        Get the latest results from the database, optionally filter by symbol.
    query_database
        Run a SELECT query to the database. Returns a list of deserialized results.
    """

    def __init__(  # noqa: PLR0913  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        name: str,
        module: str,
        symbol: Optional[str] = None,
        limit: Optional[int] = 5000,
        results_file: Optional[str] = None,
        table_name: Optional[str] = None,
        batch_size: int = 5000,
        save_database: bool = False,
        data_model: Optional["BaseModel"] = None,
        prune_interval: Optional[int] = None,
        export_directory: Optional[str] = None,
        export_interval: Optional[int] = None,
        compress_export: bool = False,
        verbose: bool = True,
        auth_token: Optional[str] = None,
        logger: Optional["logging.Logger"] = None,
        **kwargs,
    ) -> None:
        """Initialize the WebSocketClient class."""
        # pylint: disable=import-outside-toplevel
        import atexit  # noqa
        import os
        import tempfile
        import threading
        from queue import Queue
        from pathlib import Path
        from openbb_core.provider.utils.websockets.database import Database
        from openbb_core.provider.utils.websockets.helpers import (
            encrypt_value,
            get_logger,
        )

        self.name = name
        self.module = module.replace(".py", "")  # type: ignore
        self.results_file = results_file if results_file else None
        self.table_name = table_name if table_name else "records"
        self._limit = limit
        self.data_model = data_model
        self._symbol = symbol
        self._key = os.urandom(32)
        self._iv = os.urandom(16)
        self._auth_token = (
            encrypt_value(self._key, self._iv, auth_token) if auth_token else None
        )
        # strings in kwargs are encrypted before storing in the class but unencrypted when passed to the provider module.
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, str):
                    kwargs[k] = encrypt_value(self._key, self._iv, v)
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
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path

        self.results_path = Path(self.results_file).absolute()  # type: ignore
        self.save_database = save_database
        self.logger = logger if logger else get_logger("openbb.websocket.client")

        atexit.register(self._atexit)

        try:
            self.database = Database(
                results_file=self.results_file,
                table_name=self.table_name,
                limit=self._limit,
                logger=self.logger,
                data_model=self.data_model,
            )
            self.database.writer = self.database.create_writer(
                queue=None,
                prune_interval=prune_interval,
                batch_size=batch_size,
                export_directory=export_directory,
                export_interval=export_interval,
                compress_export=compress_export,
                verbose=verbose,
            )

        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error setting up the SQLite database and table ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            self._exception = OpenBBError(msg)
            self._atexit()
            raise OpenBBError(msg) from e

    def _atexit(self) -> None:
        """Clean up the running processes at exit."""
        # pylint: disable=import-outside-toplevel
        import os

        self._exception = None

        if self.is_exporting:
            self.database.writer.stop_export_task()
        if self.is_pruning:
            self.database.writer.stop_prune_task()

        if self.is_running:
            self.disconnect()
        if self.is_broadcasting:
            self.stop_broadcasting()
        if self.save_database:
            self.logger.info("Websocket results saved to, %s\n", str(self.results_path))
        if os.path.exists(self.results_file) and not self.save_database:  # type: ignore
            os.remove(self.results_file)  # type: ignore
            if os.path.exists(self.results_file + "-journal"):  # type: ignore
                os.remove(self.results_file + "-journal")  # type: ignore
            if os.path.exists(self.results_file + "-shm"):  # type: ignore
                os.remove(self.results_file + "-shm")  # type: ignore
            if os.path.exists(self.results_file + "-wal"):  # type: ignore
                os.remove(self.results_file + "-wal")  # type: ignore

    def _log_provider_output(self, output_queue) -> None:
        """Log output from the provider logger, handling exceptions, errors, and messages that are not data."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import queue
        import sys
        from openbb_core.provider.utils.errors import UnauthorizedError
        from openbb_core.provider.utils.websockets.helpers import clean_message
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
                        self._thread.join(timeout=1)
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
                        self._thread.join(timeout=1)
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
                        sys.stdout.write(output + "\n")
                        sys.stdout.flush()
                        continue
                    # Other errors are logged to stdout and the process is killed.
                    # If the exception is raised by the parent thread, it will be treated as an unexpected error.
                    if (
                        "server rejected" in output.lower()
                        or "PROVIDER ERROR" in output
                        or "unexpected error" in output.lower()
                        or "Error:" in output
                    ):
                        self._psutil_process.kill()
                        self._process.wait()
                        self._thread.join(timeout=1)
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

                    sys.stdout.write(output + "\n")
                    sys.stdout.flush()
            except queue.Empty:
                continue

    def _log_broadcast_output(self, output_queue) -> None:
        """Log output from the broadcast server queue."""
        # pylint: disable=import-outside-toplevel
        import queue  # noqa
        import sys
        from openbb_core.provider.utils.websockets.helpers import clean_message

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

                if output and "Waiting for application startup." in output:
                    output = None

                if output and "Application startup complete." in output:
                    output = None

                if output:
                    if output.startswith("ERROR:"):
                        output = output.replace("ERROR:", "BROADCAST ERROR:")
                    elif output.startswith("INFO:"):
                        output = output.replace("INFO:", "BROADCAST INFO:")
                    output = output[0] if isinstance(output, tuple) else output
                    output = clean_message(output)
                    # if (
                    #    output.startswith("BROADCAST ERROR:")
                    #    or "unexpected error" in output.lower()
                    # ):
                    #    self._psutil_broadcast_process.kill()
                    #    self._broadcast_process.wait()
                    #    self._broadcast_thread.join()
                    #    sys.stdout.write(output + "\n")
                    #    sys.stdout.flush()
                    #    continue
                    sys.stdout.write(output + "\n")
                    sys.stdout.flush()
            except queue.Empty:
                continue

    def connect(self) -> None:  # pylint: disable=too-many-locals
        """Connect to the provider client connection."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        import psutil
        import queue
        import subprocess
        import threading
        from openbb_core.provider.utils.websockets.helpers import decrypt_value

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
        command.extend([f"table_name={self.table_name}"])

        if self.limit:
            command.extend([f"limit={self.limit}"])

        try:
            kwargs = self._kwargs.copy()

            if kwargs:
                for k, v in kwargs.items():
                    if isinstance(v, str):
                        unencrypted_value = decrypt_value(
                            self._key, self._iv, v  # pylint: disable=protected-access
                        )
                        kwargs[k] = unencrypted_value
                    else:
                        kwargs[k] = v

                _kwargs = (
                    [
                        f"{k}={str(v).strip().replace(' ', '_')}"
                        for k, v in kwargs.items()
                    ]
                    if kwargs
                    else None
                )
                if _kwargs is not None:
                    for kwarg in _kwargs:
                        if kwarg not in command:
                            command.extend([kwarg])

                self._process = (
                    subprocess.Popen(  # noqa  # pylint: disable=consider-using-with
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        env=os.environ,
                        text=True,
                        bufsize=1,
                    )
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
                self._thread.name = f"Provider-Connection-{self.name}"
                self._thread.daemon = True
                self._thread.start()

                self._log_thread = threading.Thread(
                    target=self._log_provider_output,
                    args=(log_output_queue,),
                )
                self._log_thread.name = f"Provider-Log-{self.name}"
                self._log_thread.daemon = True
                self._log_thread.start()

        except Exception as e:  # pylint: disable=broad-except
            msg = f"Unexpected error -> {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            self.logger.error(msg)
            self._atexit()
            raise OpenBBError(msg) from e

        if self._exception is not None:
            exc = getattr(self, "_exception", None)
            self._exception = None
            raise OpenBBError(exc)

        if not self.is_running:
            self.logger.error(
                "Unexpected error -> Provider connection process failed to start."
            )

        if self.database.writer.export_interval:
            self.database.writer.start_export_task()

        if self.database.writer.prune_interval:
            self.database.writer.start_prune_task()

    def send_message(
        self, message, target: Literal["provider", "broadcast"] = "provider"
    ) -> None:
        """Write to the provider, or broadcast, process stdin."""
        if target == "provider":
            self._provider_message_queue.put(message)
            read_message_queue(self, self._provider_message_queue)
        elif target == "broadcast":
            self._broadcast_message_queue.put(message)
            read_message_queue(self, self._broadcast_message_queue, target="broadcast")

    def disconnect(self) -> None:
        """Disconnect from the provider connection."""
        self._stop_log_thread_event.set()
        if self._process is None or self.is_running is False:
            self.logger.info("Provider client connection is not running.")
            return

        if (
            self._psutil_process is not None
            and hasattr(self._psutil_process, "is_running")
            and self._psutil_process.is_running()
        ):
            self._psutil_process.kill()
        self._process.wait()
        self._thread.join(timeout=1)
        self._log_thread.join(timeout=1)
        self._stop_log_thread_event.clear()
        self.logger.info("Disconnected from the provider server.")
        if hasattr(self, "_exception") and self._exception:
            raise self._exception
        return

    def subscribe(self, symbol) -> None:
        """
        Send a subscribe message to the active provider connection.

        Messages are sent as JSON strings formatted as:
            {"event": "subscribe", "symbol": "AAPL,MSFT"}
        """
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import time

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
        old_symbols = self.symbol.split(",") if self.symbol is not None else []
        new_symbols = list(set(old_symbols + ticker))
        self._symbol = ",".join(new_symbols)

    def unsubscribe(self, symbol) -> None:
        """
        Unsubscribe from a symbol or list of symbols.

        Messages are sent as JSON strings formatted as:
            {"event": "unsubscribe", "symbol": "AAPL,MSFT"}
        """
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import time

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
    def is_exporting(self) -> bool:
        """Check if the database is exporting records."""
        if (
            hasattr(self.database, "writer")
            and hasattr(self.database.writer, "export_thread")
            and hasattr(self.database.writer.export_thread, "is_alive")
        ):
            return self.database.writer.export_thread.is_alive()
        return False

    @property
    def is_pruning(self) -> bool:
        """Check if the pruning event is running."""
        if (
            hasattr(self.database, "writer")
            and hasattr(self.database.writer, "prune_thread")
            and hasattr(self.database.writer.prune_thread, "is_alive")
        ):
            return self.database.writer.prune_thread.is_alive()
        return False

    @property
    def num_results(self) -> int:
        """Get the number of results stored in the database."""
        return self.query_database(f"SELECT COUNT(*) FROM {self.table_name};")[  # noqa
            0
        ]

    @property
    def results(self) -> list:
        """
        Retrieve the deserialized results from the active Database.

        Clear the results by deleting the property. e.g., del client.results
        """
        try:
            return self.database.fetch_all()
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Error retrieving results:"
                f" {e.__class__.__name__ if hasattr(e,'__class__') else e} -> {e.args}"
            )
            raise OpenBBError(msg) from e

    @results.deleter
    def results(self):
        """Clear results stored by the active WebSocket stream."""
        try:
            self.database.clear_results()
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Error clearing results:"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)

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

    def get_latest_results(
        self, symbol: Optional[str] = None, limit: Optional[int] = 100
    ) -> list:
        """Get the latest results from the database, optionally filter by symbol."""
        return self.database.get_latest_results(symbol=symbol, limit=limit)

    def query_database(
        self,
        sql: Optional[str] = None,
        limit: Optional[int] = 100,
    ) -> list:
        """
        Make a SELECT query to the database for results.

        The database always contains two columns:
            "id" - an auto-incrementing ID
            "message" - a JSON serialized row of data

        Parameters
        ----------
        sql : Optional[str]
            SQL query to execute. Default is None.
        limit : Optional[int]
            Limit the number of records returned, by most recent. Default is 25, set to None to return all records.

        Returns
        -------
        list
            A list of deserialized results from the database.
            If a 'data_model' was supplied at initialization, it will be a list of validated models.
        """
        if not sql:
            query = f"SELECT message FROM {self.table_name} ORDER BY id DESC"  # noqa
            if limit is not None:
                query += f" LIMIT {limit};"
        else:
            query = (
                sql.replace(";", "") + f" LIMIT {limit}"
                if limit is not None and "LIMIT" not in sql.upper()
                else sql
            )

        return self.database.query(query)

    def start_broadcasting(  # pylint: disable=too-many-locals
        self,
        host: str = "127.0.0.1",
        port: int = 6666,
        **kwargs,
    ) -> None:
        """
        Broadcast results over a network connection.

        Parameters
        ----------
        host : str
            The host address to broadcast results to. Default is 127.0.0.1
        port : int
            The port to broadcast results to. Default is 6666
            If the port is already in use, the next available port is used.
        **kwargs: dict
            Additional keyword arguments to pass to the `uvicorn.run`.
        """
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        import subprocess
        import sys
        import threading
        import psutil
        import queue
        from openbb_platform_api.utils.api import check_port
        from openbb_core.provider.utils.websockets.helpers import decrypt_value

        if (
            self._broadcast_process is not None
            and self._broadcast_process.poll() is None
        ):
            msg = f"WebSocket broadcast already running on: {self._broadcast_address}"
            self.logger.info(msg)
            return

        open_port = check_port(host, port)

        if open_port != port:
            msg = f"Port {port} is already in use. Using {open_port} instead."
            self.logger.warning(msg)

        command = [
            sys.executable,
            "-m",
            "openbb_core.provider.utils.websockets.broadcast",
            f"host={host}",
            f"port={open_port}",
            f"results_file={self.results_file}",
            f"table_name={self.table_name}",
            f"auth_token={decrypt_value(self._key, self._iv, self._auth_token) if self._auth_token else None}",
        ]
        if kwargs:
            for k, v in kwargs.items():
                command.extend([f"{k}={v}"])

        self._broadcast_process = (
            subprocess.Popen(  # noqa  # pylint: disable=consider-using-with
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                env=os.environ,
                text=True,
                bufsize=1,
            )
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
        self._broadcast_thread.name = f"Broadcast-Connection-{self.name}"
        self._broadcast_thread.daemon = True
        self._broadcast_thread.start()

        self._broadcast_log_thread = threading.Thread(
            target=self._log_broadcast_output,
            args=(output_queue,),
        )
        self._broadcast_log_thread.name = f"Broadcast-Log-{self.name}"
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
        self._broadcast_thread.join(timeout=1)
        self._broadcast_log_thread.join(timeout=1)
        self._broadcast_process = None
        self._psutil_broadcast_process = None
        self._broadcast_address = None
        self._stop_broadcasting_event.clear()
        return

    def __repr__(self):
        """Return the WebSocketClient representation."""
        return (
            f"WebSocketClient(module={[d for d in self.module if 'api_key' not in d]}, symbol={self.symbol}, "
            f"is_running={self.is_running}, provider_pid: "
            f"{self._psutil_process.pid if self._psutil_process else ''}, is_broadcasting={self.is_broadcasting}, "
            f"broadcast_address={self.broadcast_address}, "
            f"broadcast_pid: {self._psutil_broadcast_process.pid if self._psutil_broadcast_process else ''}, "
            f"results_file={self.results_file}, table_name={self.table_name}, "
            f"save_database={self.save_database})"
        )


def non_blocking_websocket(client, output_queue, provider_message_queue) -> None:
    """Communicate with the threaded process."""
    try:
        while not client._stop_log_thread_event.is_set():

            if (
                client.database.writer.prune_interval
                and client.database.writer.prune_thread is not None
                and not client.database.writer.prune_thread.is_alive()
            ):
                client.database.writer.start_prune_task()

            if (
                client.database.writer.export_interval is not None
                and client.database.writer.export_thread is not None
                and not client.database.writer.export_thread.is_alive()
            ):
                client.database.writer.start_export_task()

            while not provider_message_queue.empty():
                read_message_queue(client, provider_message_queue)
            output = client._process.stdout.readline()

            if output == "" and client._process.poll() is not None:
                break

            if output:
                output_queue.put(output.strip())

    except Exception as e:  # pylint: disable=broad-except
        msg = (
            "Unexpected error in non_blocking_websocket:"
            f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
        )
        client.logger.error(msg)
        raise e from e
    finally:
        client._process.stdout.close()
        client._process.wait()
        if client.is_exporting:
            client.database.writer.stop_export_task()
        if client.is_pruning:
            client.database.writer.stop_prune_task()


def send_message(
    client, message, target: Literal["provider", "broadcast"] = "provider"
) -> None:
    """Send a message to the WebSocketConnection process."""
    # pylint: disable=import-outside-toplevel
    import json

    if not isinstance(message, str):
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
    except Exception as e:  # pylint: disable=broad-except
        msg = (
            f"Error sending message to the {target} process:"
            f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
        )
        client.logger.error(msg)


def read_message_queue(
    client, message_queue, target: Literal["provider", "broadcast"] = "provider"
):
    """Read messages from the queue and send them to the WebSocketConnection process."""
    while not message_queue.empty():
        message = message_queue.get(timeout=1)
        if message:
            try:
                if target == "provider" and not client._stop_log_thread_event.is_set():
                    send_message(client, message, target="provider")
                elif (
                    target == "broadcast"
                    and not client._stop_broadcasting_event.is_set()
                ):
                    send_message(client, message, target="broadcast")
            except Exception as e:  # pylint: disable=broad-except
                err = (
                    "Error while attempting to transmit from the outgoing message queue:"
                    f"{e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args} -> {message}"
                )
                client.logger.error(err)


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
    except Exception as e:  # pylint: disable=broad-except
        err = (
            f"Unexpected error in non_blocking_broadcast:"
            f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
        )
        client.logger.error(err)
    finally:
        client._broadcast_process.stdout.close()
        client._broadcast_process.wait()
