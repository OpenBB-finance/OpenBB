"""Database module for serialized websockets results."""

# pylint: disable=too-many-lines,too-many-arguments,too-many-locals,too-many-branches,too-many-statements,protected-access

import asyncio
import threading
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Iterable, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import run_async
from openbb_core.provider.utils.websockets.helpers import kill_thread

if TYPE_CHECKING:
    import logging
    from pathlib import Path

    from openbb_core.provider.utils.websockets.helpers.message_queue import (
        MessageQueue,
    )
    from pydantic import BaseModel

CHECK_FOR = (
    "DATABASE",
    "TABLE",
    "BACKUP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "CREATE",
    "MODIFY",
    "PRAGMA",
    "ALTER",
    "DROP",
    "RENAME",
    "REPLACE",
    "TRUNCATE",
    "VACUUM",
    "ATTACH",
    "DETACH",
    "REINDEX",
    "MOVE",
    "1=1",
    "=''",
    '=""',
    '"=""',
    "= ''",
    '= ""',
    "or ''",
    'or ""',
    "OR ''",
    'OR ""',
    "AND ''",
    'AND ""',
    "and ''",
    'and ""',
    "('')",
    '("")',
    "('',)",
    '("",)',
    " ''",
    ' ""',
    "' '",
    '" "',
)


class Database:
    """
    Class to read from, and write to, the SQL file using aiosqlite.

    Each write or delete operation uses a new connection context in WAL mode.

    The table always contains only two columns:
        "id" - an auto-incrementing ID & primary key
        "message" - a JSON serialized row of data (dictionary)

    If a path is not specified, a temporary file will be created and used.

    The limit parameter can be used to set a maximum number of records to keep in the database.

    If the number of records exceeds the limit, the oldest records will be deleted.

    The "id" column will not be reset, i.e., the numbering will continue despite deletions.

    Parameters
    ----------
    results_file : Optional[str]
        The full path to the SQLite database file. If not specified, a temporary file will be created.
        Each websocket client should have its own database file.
    table_name : Optional[str]
        The name of the table to write to. Default is "records".
    data_model : Optional[BaseModel]
        A Pydantic model to validate the JSON data. Default is None.
    limit: Optional[int]
        The maximum number of records to keep in the database. Default is None.
    logger : Optional[logging.Logger]
        A custom logger to use. If not provided, a new logger will be created.
    loop: Optional[asyncio.AbstractEventLoop]
        An asyncio event loop.
    **kwargs
        Additional keyword arguments to pass to the SQLite connection at creation.

    Methods
    -------
    get_connection(name: str = "read") -> aiosqlite.Connection
        Get a connection to the SQLite database. Use "read" for read-only connections, and "write" for write connections.
        Yielded as an async context manager.
    write_to_db(message) -> None
        Write the WebSocket message to the SQLite database.
        Synchronous wrapper for _write_to_db.
    fetch_all(limit: Optional[int] = None) -> list
        Read the WebSocket message from the SQLite database.
        Synchronous wrapper for _fetch_all.
    get_latest_results(symbol: Optional[str] = None, limit: Optional[int] = None) -> list
        Get the latest records from the database. Optionally filter by symbol.
        Synchronous wrapper for _get_latest_results.
    query(sql: str, parameters: Optional[Iterable[Any]]) -> list
        Run a SELECT query to the database. Table name cannot be anything other than the originally assigned name.
        For convenience, the query can start after WHERE, or provide a full query string to extract a specific array.
        There are only two columns in the table: "id" - auto-increment index - and "message" - serialized JSON data row.
        Synchronous wrapper for _query_db.
    clear_results() -> None
        Clear all results from the SQLite database.

    Raises
    ------
    OpenBBError
        All exceptions are raised as OpenBBError.
    """

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        results_file: Optional[str] = None,
        table_name: Optional[str] = None,
        data_model: Optional["BaseModel"] = None,
        limit: Optional[int] = None,
        logger: Optional["logging.Logger"] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        **kwargs,
    ):
        """Initialize the ResultsDB class."""
        # pylint: disable=import-outside-toplevel
        import tempfile  # noqa
        from pathlib import Path
        from aiosqlite import ProgrammingError
        from openbb_core.provider.utils.websockets.helpers import get_logger

        self.results_file = None
        self.table_exists = False
        self.logger = (
            logger if logger is not None else get_logger("openbb.websocket.database")
        )

        if not results_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path
        else:
            if ":" in results_file:
                self.results_file = results_file
                self.results_path = results_file  # type: ignore
                kwargs["uri"] = True
            self.results_path = Path(results_file).absolute()
            self.results_file = results_file

        if (
            " " in table_name
            or table_name.isupper()
            or any(x.lower() in table_name.lower() for x in CHECK_FOR)
        ):
            raise OpenBBError(ProgrammingError(f"Invalid table name, {table_name}."))

        self.table_name = table_name if table_name else "records"
        self.limit = limit
        self.loop = loop
        self.kwargs = kwargs if kwargs else {}
        self._connections = {}
        run_async(self._setup_database)
        self.data_model = data_model

    async def _setup_database(self):
        """Create the SQLite database, if required."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        from aiosqlite import DatabaseError

        try:
            if self.results_file is not None and os.path.exists(self.results_file):  # type: ignore
                async with self.get_connection("write") as conn:
                    try:
                        cursor = await conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table';"
                        )
                        await cursor.close()
                    except DatabaseError as e:
                        msg = (
                            "Unexpected error caused by an invalid SQLite database file."
                            "Please check the path, and inspect the file if it exists."
                            + f" -> {e}"
                        )
                        self.logger.error(msg)
                        raise OpenBBError(msg) from e

            async with self.get_connection("write") as conn:
                cursor = await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL
                    );
                """
                )
                pragmas = [
                    "PRAGMA journal_mode=WAL",
                    "PRAGMA synchronous=off",
                    "PRAGMA temp_store=memory",
                ]

                for pragma in pragmas:
                    await conn.execute(pragma)

                await conn.commit()
                await cursor.close()
                self.table_exists = True

        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error while creating SQLite database ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(msg) from e

    @asynccontextmanager
    async def get_connection(self, name: str = "read"):
        """Get a connection to the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite

        conn_kwargs = self.kwargs.copy()

        if name == "read":
            if ":" not in self.results_file:
                results_file = (
                    "file:"
                    + (
                        self.results_file
                        if self.results_file.startswith("/")
                        else "/" + self.results_file
                    )
                    + "?mode=ro"
                )
            else:
                results_file = (
                    self.results_file
                    + f"{'&mode=ro' if '?' in self.results_file else '?mode=ro'}"
                )
            conn_kwargs["uri"] = True
        elif name == "write":
            results_file = self.results_file

        conn_kwargs["check_same_thread"] = False

        if name not in self._connections:
            conn = await aiosqlite.connect(results_file, **conn_kwargs)
            pragmas = [
                "PRAGMA journal_mode=WAL",
                "PRAGMA synchronous=off",
                "PRAGMA temp_store=memory",
            ]
            for pragma in pragmas:
                await conn.execute(pragma)

            await conn.commit()
            self._connections[name] = conn

        yield self._connections[name]

    async def _write_to_db(self, message) -> None:
        """Write the WebSocket message to the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import json

        try:
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            if not isinstance(message, str):
                message = json.dumps(message)

            async with self.get_connection("write") as conn:
                cursor = await conn.execute(
                    f"""
                    INSERT INTO {self.table_name} (message)
                    VALUES (?)
                """,  # noqa
                    (message,),
                )
                self._at_limit = False

                if self.limit is not None and not self._at_limit:
                    limit = max(0, int(self.limit))

                    if limit > 0:
                        count_cursor = await conn.execute(
                            f"SELECT COUNT(*) FROM {self.table_name}"  # noqa
                        )
                        count = await count_cursor.fetchone()

                        if count[0] > limit:
                            self._at_limit = True

                        await count_cursor.close()

                if self._at_limit:
                    await conn.execute(
                        f"""
                        DELETE FROM {self.table_name}
                        WHERE id = (
                            SELECT id FROM {self.table_name}
                            ORDER BY id ASC
                            LIMIT 1
                        )
                        """,  # noqa
                    )

                await cursor.close()
                await conn.commit()

        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    def write_to_db(self, message) -> None:
        """Write a message to the SQLite database."""
        try:
            run_async(self._write_to_db, message)
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error while writing to SQLite database ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(msg) from e

    async def _fetch_all(self, limit: Optional[int] = None) -> list:
        """Read the WebSocket message from the SQLite database."""
        try:
            rows: list = []
            async with self.get_connection("read") as conn:
                query = (
                    f"SELECT message FROM {self.table_name} ORDER BY id DESC"  # noqa
                )
                if limit is not None:
                    query += " LIMIT ?"
                    params = (limit,)
                else:
                    params = ()
                async with conn.execute(query, params) as cursor:
                    async for row in cursor:
                        rows.append(await self._deserialize_row(row, cursor))

            return rows

        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    async def _deserialize_row(self, row, cursor) -> dict:
        """Deserialize a row from the SQLite database.
        Handles both single message column and multiple extracted fields."""
        # pylint: disable=import-outside-toplevel
        import json

        try:
            if len(row) == 1:
                # Single column case (full message)
                return (
                    json.loads(row[0])
                    if (
                        isinstance(row[0], str)
                        and (row[0].startswith("{") or row[0].startswith("["))
                    )
                    or isinstance(row[0], bytes)
                    else row[0]
                )
            else:
                # Multiple column case (extracted fields)
                return {cursor.description[i][0]: row[i] for i in range(len(row))}

        except (json.JSONDecodeError, AttributeError) as e:
            self.logger.error(f"Failed to deserialize row: {e}")
            return row[0] if len(row) == 1 else dict(enumerate(row))

        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error while deserializing row -> "
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(e) from e

    def fetch_all(self, limit: Optional[int] = None) -> list:
        """Fetch all the results from the SQLite database."""
        try:
            return run_async(self._fetch_all, limit)
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error while reading from SQLite database ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(e) from e

    async def _get_latest_results(
        self, symbol: Optional[str] = None, limit: Optional[int] = None
    ) -> list:
        """Get the latest records from the database. Optionally filter by symbol."""
        if symbol:
            symbols = symbol.split(",")
            sym_str = "("
            for sym in symbols:
                sym_str += f"'{sym.upper()}'" + ("," if sym != symbols[-1] else "")
            sym_str += ")"
            query = f"json_extract (message, '$.symbol') IN {sym_str}"
        else:
            query = f"SELECT message FROM {self.table_name}"  # noqa

        query += " ORDER BY json_extract (message, '$.date') DESC"

        if limit is not None:
            query += f" LIMIT {limit};"

        return await self._query_db(query)

    def get_latest_results(
        self, symbol: Optional[str] = None, limit: Optional[int] = None
    ) -> list:
        """Get the latest records from the database. Optionally filter by symbol."""
        try:
            return run_async(self._get_latest_results, symbol, limit)
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Unexpected error while getting latest records ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)

    async def _query_db(self, sql, parameters: Optional[Iterable[Any]] = None) -> list:
        """Query the SQLite database."""

        if not sql or sql in ("", "''"):
            raise OpenBBError("Empty query not allowed.")
        query = (
            sql
            if sql.strip().startswith("SELECT")
            else f"SELECT message FROM {self.table_name} WHERE {sql}"  # noqa
        )
        if not query.endswith(";"):
            query += ";"

        if (
            not query.startswith("SELECT")
            or any(x.lower() in query.lower() for x in CHECK_FOR)
            or (self.table_name not in query and "message" not in query)
        ):
            raise OpenBBError(f"Invalid operation: {sql}.")

        rows: list = []
        try:
            async with self.get_connection("read") as conn, conn.execute(
                query, parameters
            ) as cursor:
                async for row in cursor:
                    rows.append(await self._deserialize_row(row, cursor))
            return rows
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    def query(self, sql: str, parameters: Optional[Iterable[Any]] = None) -> list:
        """
        Run a SELECT query to the database.

        Begin after WHERE, using the built-in JSON functions, or provide a full query string.

        Parameters
        ----------
        sql : str
            The SQL query string to run.

        Examples
        --------
        # Start the query string after WHERE.
        >>> database.query("json_extract (message, '$.price') > 100")
        # Or provide a full query string by starting with SELECT.
        >>> query = (
                "SELECT json_extract (message, '$.symbol')"
                "FROM records WHERE json_extract (message, '$.type') = 'trade';"
            )
        >>> database.query(query)
        >>>
        """
        try:
            return run_async(self._query_db, sql, parameters)
        except Exception as e:  # pylint: disable=broad-except
            msg = f"{e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
            self.logger.error(msg)

    async def _clear_results(self):
        """Clear the results from the SQLite database."""
        try:
            async with self.get_connection("write") as conn:
                cursor = await conn.execute(f"DELETE FROM {self.table_name}")  # noqa
                await cursor.close()
                cursor = await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL
                    )
                """
                )  # noqa
                await conn.commit()
                await cursor.close()

            self.logger.info(
                "Results cleared from table, '%s', in %s",
                self.table_name,
                self.results_file,
            )
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    def clear_results(self) -> None:
        """Clear all results from the SQLite database."""
        try:
            run_async(self._clear_results)
        except Exception as e:  # pylint: disable=broad-except
            msg = (
                "Error clearing results: "
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(msg) from e

    def create_writer(
        self,
        queue: Optional["MessageQueue"] = None,
        batch_size: int = 200,
        prune_interval: Optional[int] = None,
        export_directory: Optional[Union[str, "Path"]] = None,
        export_interval: Optional[int] = None,
        compress_export: bool = False,
        verbose: bool = True,
    ):
        """
        Create a new DatabaseWriter instance from the initialized Database.

        Returns
        -------
        DatabaseWriter
            A new DatabaseWriter instance. Use
        """

        return DatabaseWriter(
            self,
            queue,
            batch_size,
            prune_interval,
            export_directory,
            export_interval,
            compress_export,
            verbose,
        )


class DatabaseWriter:
    """
    Class responsible for continuously writing messages to the SQLite database,
    exporting the database at set intervals,
    and pruning the database of older records at a different interval.

    Setting the 'export_interval' will create a new CSV file for each interval,
    while leaving as None disables the export feature.
    The task is started by the WebsocketClient class when a connection is created from the FastAPI and Python endpoints,
    but can be manually started by calling the `start_batch_writer` async method.

    Parameters
    ----------
    database : Database
        The Database instance to write to.
    queue : Optional[MessageQueue]
        The MessageQueue instance to use. Default is None, which creates a new instance.
    batch_size : int
        The target batch size for writing to the database. Default is 25000.
    prune_interval : Optional[int]
        The interval in minutes to prune the database of older records. Default is None.
    export_directory : Optional[Union[str, Path]]
        The directory to export the database to, if an interval is set. Default is 'OpenBBUserData/exports/websockets'.
    export_interval : Optional[int]
        The interval in minutes to export the database to a CSV file. Default is None.
    num_workers : int
        The number of parallel writers to use. Default is 120.
    """

    def __init__(
        self,
        database: Database,
        queue: Optional["MessageQueue"] = None,
        batch_size: int = 200,
        prune_interval: Optional[int] = None,
        export_directory: Optional[Union[str, "Path"]] = None,
        export_interval: Optional[int] = None,
        compress_export: bool = False,
        verbose: bool = True,
    ):
        """Initialize the DatabaseWriter class."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        import time

        from openbb_core.provider.utils.websockets.message_queue import (
            MessageQueue,
        )
        from openbb_core.app.service.user_service import UserService

        user_settings = UserService().read_from_file()
        obb_export_directory = user_settings.preferences.export_directory

        if not hasattr(database, "loop"):
            try:
                database.loop = asyncio.new_event_loop()
            except (RuntimeError, RuntimeWarning):
                database.loop = asyncio.get_event_loop()

        self.database = database
        self.batch_size = batch_size
        self.queue = queue if queue else MessageQueue(max_size=100000)
        export_directory = (
            export_directory
            if export_directory
            else obb_export_directory + "/websockets"
        )
        os.makedirs(export_directory, exist_ok=True)
        self.export_directory = export_directory
        self.export_interval = export_interval
        self.prune_interval = prune_interval
        self.compress_export = compress_export
        self.verbose = verbose
        self.export_thread = None
        self.prune_thread = None
        self.last_flush = time.time()
        self.writer_running = False
        self._first_timestamp = None
        self._last_processed_timestamp = None
        self._conn = None
        self.num_workers = 60
        self.write_tasks = []
        self._export_running = False
        self._prune_running = False
        self.batch_processor = BatchProcessor(self)
        self._shutdown = False

    async def _create_connection(self):
        """Create a new connection to the SQLite database."""
        async with self.database.get_connection("write") as conn:
            self.writer_running = True
            self._conn = conn

    async def start_writer(self):
        """Start writing tasks."""
        if not self.writer_running:
            if not self.batch_processor.is_alive():
                self.batch_processor.start()
            await self._create_connection()
        for _ in range(self.num_workers):
            task = asyncio.create_task(self._process_queue())
            self.write_tasks.append(task)

    async def stop_writer(self):
        """Stop all queue processors."""
        await self._flush_queue()
        self.writer_running = False
        await asyncio.gather(*self.write_tasks, return_exceptions=True)
        if self._conn:
            await self._conn.close()
        self.batch_processor.stop()
        kill_thread(self.batch_processor)

    async def _process_queue(self):
        """Process queue with parallel writers."""
        batch = []

        while self.writer_running:
            try:
                while len(batch) < self.batch_size:
                    try:
                        message = await asyncio.wait_for(
                            self.queue.dequeue(), timeout=0.1
                        )
                        batch.append(message)
                    except asyncio.TimeoutError:
                        break
                if batch:
                    await self._write_batch(batch)
                    batch = []
                else:
                    await asyncio.sleep(0.001)

            except Exception as e:  # pylint: disable=broad-except
                msg = f"\nQueue processing error: {e}"
                self.database.logger.error(msg, exc_info=True)
                await asyncio.sleep(0.1)

    async def _flush_queue(self):
        """Flush the queue of messages to the database."""
        batch: list = []
        while not self.queue.queue.empty() and len(batch) < self.batch_size:
            batch.append(await self.queue.dequeue())

        await self._write_batch(batch)

    async def _write_batch(self, batch):
        """Write the batch of messages to the database."""
        if not batch:
            return
        self.batch_processor.write_queue.put_nowait(batch)

    async def _export_database(self):
        """Export the database to a CSV file at a set interval."""
        # pylint: disable=import-outside-toplevel
        import csv  # noqa
        import gzip
        import json
        import sys
        from anyio import open_file
        from collections import OrderedDict
        from io import StringIO
        from pandas import to_datetime

        chunk_size = 20000
        minutes = self.export_interval or 5
        latest_date = None
        earliest_date = None
        if not self._export_running or not self.export_thread:
            return
        try:

            latest_query = f"""
                SELECT json_extract(message, '$.date')
                FROM {self.database.table_name}
                ORDER BY json_extract(message, '$.date') DESC LIMIT 1
            """  # noqa

            earliest_query = f"""
                SELECT json_extract(message, '$.date')
                FROM {self.database.table_name}
                ORDER BY json_extract(message, '$.date') ASC LIMIT 1
            """  # noqa

            async with self.database.get_connection("read") as conn:
                try:
                    async with conn.execute(latest_query) as cursor:
                        latest_date = await cursor.fetchone()
                        if not latest_date:
                            return

                    async with conn.execute(earliest_query) as cursor:
                        earliest_date = await cursor.fetchone()
                        if not latest_date:
                            return

                except asyncio.InvalidStateError as e:
                    self.database.logger.error(f"Database connection state error: {e}")
                    self._export_running = False
                    return

            latest_timestamp = to_datetime(latest_date[0])
            earliest_timestamp = to_datetime(earliest_date[0])
            # Round down to nearest interval
            cutoff_time = latest_timestamp - timedelta(
                minutes=latest_timestamp.minute % minutes,
                seconds=latest_timestamp.second,
                microseconds=latest_timestamp.microsecond,
            )
            earliest_time = earliest_timestamp - timedelta(
                minutes=latest_timestamp.minute % minutes,
                seconds=latest_timestamp.second,
                microseconds=latest_timestamp.microsecond,
            )

            # If we have processed data before, use that as reference
            if self._last_processed_timestamp:
                start_time = self._last_processed_timestamp
            else:
                start_time = cutoff_time - timedelta(minutes=minutes)

            if start_time < earliest_timestamp:
                start_time = earliest_time

            # Set end_time to be one interval after start_time
            end_time = start_time + timedelta(minutes=minutes)

            results_file = (
                self.export_directory
                + "/"
                + self.database.results_file.split("/")[-1].split(".")[0]
            )
            path = f"{results_file}_{start_time.strftime('%Y%m%dT%H%M')}.csv"
            query = f"""
                SELECT message
                FROM {self.database.table_name}
                WHERE json_extract(message, '$.date') >= ?
                AND json_extract(message, '$.date') < ?
                ORDER BY json_extract(message, '$.date') ASC
            """  # noqa

            async with self.database.get_connection(
                "read"
            ) as conn, conn.cursor() as cursor:
                await cursor.execute(
                    query, (start_time.isoformat(), end_time.isoformat())
                )

                headers = OrderedDict()
                first_rows = await cursor.fetchmany(chunk_size)
                if not first_rows:
                    return

                for row in first_rows:
                    for key in json.loads(row[0]):
                        headers[key] = None

                if self.compress_export:
                    with gzip.open(path, "wt") as gz_file:
                        writer = csv.DictWriter(gz_file, fieldnames=list(headers))
                        await writer.writeheader()
                        writer.writerows(json.loads(row[0]) for row in first_rows)

                        while True:
                            rows = await cursor.fetchmany(chunk_size)
                            new_rows: list = []
                            if not rows:
                                break

                            for row in rows:
                                data = json.loads(row[0])
                                for key in data:
                                    headers[key] = None
                                new_rows.append(data)

                            writer = csv.DictWriter(gz_file, fieldnames=list(headers))
                            writer.writerows(new_rows)
                else:
                    async with await open_file(path, mode="w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=headers)
                        await writer.writeheader()
                        buffer = StringIO()
                        csv_writer = csv.DictWriter(buffer, fieldnames=list(headers))
                        csv_writer.writerows(json.loads(row[0]) for row in first_rows)
                        await f.write(buffer.getvalue())

                        while True:
                            rows = await cursor.fetchmany(chunk_size)
                            new_rows: list = []
                            if not rows:
                                break

                            for row in rows:
                                data = json.loads(row[0])
                                for key in data:
                                    headers[key] = None
                                new_rows.append(data)

                            buffer = StringIO()
                            csv_writer = csv.DictWriter(
                                buffer, fieldnames=list(headers)
                            )
                            csv_writer.writerows(new_rows)
                            await f.write(buffer.getvalue())

            self._last_processed_timestamp = cutoff_time

            if self.verbose is True:
                msg = f"DATABASE INFO:      Interval for period ending {cutoff_time} saved to: {path}"
                sys.stdout.write(msg + "\n")
                sys.stdout.flush()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.database.logger.error(
                "Error exporting database: %s", str(e), exc_info=True
            )
            sys.exit(1)

    def _run_export_event(self):
        """Run the export event loop in a separate process."""
        run_async(self._start_export_task)

    def start_export_task(self):
        """Public method to start the background export task."""
        if (
            hasattr(self, "export_thread")
            and self.export_thread
            and self.export_thread.is_alive()
        ):
            if not self._export_running:
                self._export_running = True
            return

        self._export_running = True
        self.export_thread = threading.Thread(
            target=self._run_export_event, name="ExportThread", daemon=True
        )
        self.export_thread.start()

    def stop_export_task(self):
        """Public method to stop the background export task."""
        if hasattr(self, "export_thread") and self.export_thread:
            self.export_thread.join(timeout=1)
            if self.export_thread.is_alive():
                kill_thread(self.export_thread)
        self._export_running = False
        self.export_thread = None

    def _run_prune_event(self):
        """Run the prune event loop in a separate process."""
        run_async(self._start_prune_task)

    def start_prune_task(self):
        """Public method to start the background pruning task."""
        if (
            hasattr(self, "prune_thread")
            and self.prune_thread
            and self.prune_thread.is_alive()
        ):
            return

        try:
            self._prune_running = True
            prune_thread = threading.Thread(target=self._run_prune_event)
            prune_thread.daemon = True
            prune_thread.name = "WebSocketPruneThread"
            self.prune_thread = prune_thread
            self.prune_thread.start()
        finally:
            self.prune_thread.join(timeout=1)

    def stop_prune_task(self):
        """Public method to stop the background pruning task."""
        if hasattr(self, "prune_thread") and self.prune_thread:
            self.prune_thread.join(timeout=1)
            if self.prune_thread.is_alive():
                kill_thread(self.prune_thread)
        self._prune_running = False
        self.prune_thread = None

    async def _start_prune_task(self):
        """Start the background prune task."""
        # pylint: disable=import-outside-toplevel
        import sys  # noqa
        from pandas import to_datetime

        if not self._prune_running or not self.prune_thread:
            return

        try:
            minutes = (
                self.prune_interval
                if self.prune_interval
                else self.export_interval * 2 if self.export_interval else 10
            )
            while self._prune_running is True:
                if self.prune_thread is None:
                    self._prune_running = False
                    break

                # Stagger the prune task slightly to avoid things happening exactly on the minute.
                await asyncio.sleep(minutes * 60)
                await asyncio.sleep(7)

                if not self._last_processed_timestamp:
                    last_date = await self.database._query_db(
                        f"SELECT json_extract(message, '$.date') FROM {self.database.table_name} ORDER BY json_extract(message, '$.date') DESC LIMIT 1"  # noqa
                    )
                    if not last_date:
                        continue
                    last_date = to_datetime(last_date[0])
                    last_processed_timestamp = last_date.replace(
                        second=0, microsecond=0
                    )
                else:
                    last_processed_timestamp = self._last_processed_timestamp

                cutoff_time = last_processed_timestamp - timedelta(minutes=minutes)
                cutoff_timestamp = cutoff_time.isoformat()

                async with self.database.get_connection("write") as conn:

                    if self.verbose is True:
                        msg = f"DATABASE INFO:      Pruning database of records before: {cutoff_timestamp}"
                        sys.stdout.write(msg + "\n")
                        sys.stdout.flush()

                    async with conn.execute(
                        f"DELETE FROM {self.database.table_name} WHERE json_extract(message, '$.date') < ?",  # noqa
                        (cutoff_timestamp,),
                    ):
                        await conn.commit()
        finally:
            if self.prune_thread is not None:
                self.prune_thread.join(timeout=1)

    async def _start_export_task(self):
        """Start a background task to prune the database periodically."""
        from pandas import to_datetime

        minutes = self.export_interval or 5

        while self.export_thread is not None:
            # Get the initial row to determine the "first time"
            try:
                query = f"SELECT json_extract(message, '$.date') FROM {self.database.table_name} ORDER BY json_extract(message, '$.date') ASC LIMIT 1"  # noqa
                initial_row = await self.database._query_db(query)
                if not initial_row:
                    await asyncio.sleep(1)
                    initial_row = await self.database._query_db(query)
                    if not initial_row:
                        continue

                first_time = to_datetime(initial_row[0])
                if not first_time:
                    await asyncio.sleep(1)
                self._first_timestamp = first_time.replace(second=0, microsecond=0)
                self._last_processed_timestamp = self._first_timestamp

                while not self._shutdown:
                    if self.export_thread is None:
                        break
                    # Check if the next interval has been reached and export immediately if available.
                    next_interval = self._last_processed_timestamp + timedelta(
                        minutes=minutes
                    )
                    cutoff_timestamp = next_interval.isoformat()
                    query = f"SELECT COUNT(*) FROM {self.database.table_name} WHERE json_extract(message, '$.date') >= ?"  # noqa
                    count = await self.database._query_db(query, (cutoff_timestamp,))

                    if count[0] > 0:
                        await self._export_database()
                    else:
                        await asyncio.sleep(minutes * 60)
                        # Stagger slightly so things don't happen exactly on the minute.
                        await asyncio.sleep(3)
            except asyncio.CancelledError:
                break
            finally:
                if self.export_thread is not None:
                    self.export_thread.join(timeout=1)


class BatchProcessor(threading.Thread):
    """
    This class is a thread intended for use as a subprocess and is called by `DatabaseWriter.start_writer()`.
    """

    def __init__(
        self, database_writer: DatabaseWriter, num_workers=120, collection_time=0.25
    ):
        """Initialize the BatchProcessor class."""
        # pylint: disable=import-outside-toplevel
        import queue

        super().__init__(daemon=True, name="BatchProcessor")
        self.writer = database_writer
        self.write_queue: queue.Queue = queue.Queue()
        self.running = True
        self.loop = None
        self.num_workers = num_workers
        self.workers: list = []
        self.collection_time = collection_time
        self._shutdown = threading.Event()

    def run(self):
        """Run the batch processor as tasks."""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            # Create worker tasks
            while self.running and not self._shutdown.is_set():
                try:
                    self.loop.run_until_complete(self._worker())
                except (SystemExit, KeyboardInterrupt):
                    self.running = False
                    break
                except Exception as e:
                    self.writer.database.logger.error(f"Batch processing error: {e}")
                    break
        finally:
            self._cleanup()

    def stop(self):
        """Signal thread to stop gracefully."""
        self.running = False
        self._shutdown.set()
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    def _cleanup(self):
        """Clean up resources on shutdown"""
        if self.loop:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            self.loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
            self.loop.close()

    async def _worker(self):
        # pylint: disable=import-outside-toplevel
        import time

        batch_size = 200
        while self.running:
            try:
                batch: list = []
                total = 0
                collection_start = time.time()

                while (
                    time.time() - collection_start < self.collection_time
                    and total < batch_size
                ):
                    if not self.write_queue.empty():
                        msg = self.write_queue.get_nowait()
                        batch.append(msg)
                        total += len(msg)
                    else:
                        await asyncio.sleep(0.01)

                if batch:
                    await self._write_batch(batch)

            except Exception as e:  # pylint: disable=broad-except
                self.writer.database.logger.error(f"Worker error: {e}")
                self.running = False
                await asyncio.sleep(0.1)
                break

    async def _write_batch(self, batch):
        """Write the batch of messages to the database."""
        try:
            query = f"""
                INSERT INTO {self.writer.database.table_name} (message)
                VALUES (?)
            """  # noqa
            values: list = []
            for b in batch:
                values.extend([(msg,) for msg in b])
            async with self.writer.database.get_connection("write") as conn:
                await conn.execute("PRAGMA temp_store=memory")
                async with conn.cursor() as cursor:
                    await cursor.executemany(query, values)
                await conn.commit()
        except Exception as e:  # pylint: disable=broad-except
            self.writer.database.logger.error(f"Error writing batch: {e}")
            await asyncio.sleep(0.1)
