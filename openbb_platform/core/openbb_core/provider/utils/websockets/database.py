"""Database module for serialized websockets results."""

from typing import TYPE_CHECKING, Any, Iterable, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import run_async

if TYPE_CHECKING:
    import asyncio
    import logging

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

    The table always contains two columns:
        "id" - an auto-incrementing ID
        "message" - a JSON serialized row of data

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
        loop: Optional["asyncio.AbstractEventLoop"] = None,
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
        self.logger = logger if logger else get_logger("openbb.websocket.database")

        if not results_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path
        if ":" in results_file:
            self.results_file = results_file
            self.results_path = results_file  # type: ignore
            kwargs["uri"] = True
        else:
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
        run_async(self._setup_database)
        self.data_model = data_model

    async def _setup_database(self):
        """Create the SQLite database, if required."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        import aiosqlite

        try:
            if self.results_file is not None and os.path.exists(self.results_file):  # type: ignore
                async with aiosqlite.connect(
                    self.results_file, loop=self.loop, **self.kwargs
                ) as conn:
                    try:
                        cursor = await conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table';"
                        )
                        await cursor.close()
                    except aiosqlite.DatabaseError as e:
                        msg = (
                            "Unexpected error caused by an invalid SQLite database file."
                            "Please check the path, and inspect the file if it exists."
                            + f" -> {e}"
                        )
                        self.logger.error(msg)
                        raise OpenBBError(msg) from e

            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                cursor = await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL
                    );
                """
                )
                await conn.commit()
                await cursor.close()
                self.table_exists = True

        except Exception as e:
            msg = (
                "Unexpected error while creating SQLite database ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            raise OpenBBError(msg) from e

    async def _write_to_db(self, message) -> None:
        """Write the WebSocket message to the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite  # noqa
        import json

        try:
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            if not isinstance(message, str):
                message = json.dumps(message)

            if not self.table_exists:
                raise aiosqlite.OperationalError(
                    "Attempt to write to non-existent table."
                )

            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                await conn.execute("PRAGMA journal_mode=WAL;")
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
        """Write the WebSocket message to the SQLite database."""
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
        # pylint: disable=import-outside-toplevel
        import aiosqlite  # noqa

        try:
            rows: list = []
            conn_kwargs = self.kwargs.copy()

            if not conn_kwargs.get("check_same_thread"):
                conn_kwargs["check_same_thread"] = False

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

            async with aiosqlite.connect(
                results_file,
                loop=self.loop,
                **conn_kwargs,
            ) as conn:
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
                        rows.append(await self.deserialize_row(row))

            return rows

        except Exception as e:
            raise OpenBBError(e) from e

    async def deserialize_row(self, row: str) -> dict:
        """Deserialize a row from the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import json

        try:
            return (
                json.loads(row[0])
                if (
                    (
                        isinstance(row[0], str)
                        and (row[0].startswith("{") or row[0].startswith("["))
                    )
                    or isinstance(row[0], bytes)
                )
                else row[0]
            )
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
            msg = (
                "Unexpected error while getting latest records ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)

    async def _query_db(self, sql, parameters: Optional[Iterable[Any]] = None) -> list:
        """Query the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite  # noqa
        import json

        if not sql or sql in ("", "''"):
            raise OpenBBError("Empty query not allowed.")
        query = (
            sql
            if sql.startswith("SELECT")
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
            conn_kwargs = self.kwargs.copy()
            if not conn_kwargs.get("check_same_thread"):
                conn_kwargs["check_same_thread"] = False

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

            async with aiosqlite.connect(
                results_file,
                loop=self.loop,
                **conn_kwargs,
            ) as conn, conn.execute(query, parameters) as cursor:
                async for row in cursor:
                    rows.append(
                        json.loads(row[0])
                        if (
                            (
                                isinstance(row[0], str)
                                and (row[0].startswith("{") or row[0].startswith("["))
                            )
                            or isinstance(row[0], bytes)
                        )
                        else row[0]
                    )
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
                "FROM test_table WHERE json_extract (message, '$.type') = 'trade';"
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
        # pylint: disable=import-outside-toplevel
        import aiosqlite

        try:
            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                cursor = await conn.execute("PRAGMA journal_mode=WAL;")
                await cursor.close()
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
