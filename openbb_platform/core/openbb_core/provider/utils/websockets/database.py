"""Database module for serialized websockets results."""

from typing import TYPE_CHECKING, Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import run_async

if TYPE_CHECKING:
    import asyncio
    import logging

    from pydantic import BaseModel


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
    fetch_all(limit: Optional[int] = None) -> list
        Read the WebSocket message from the SQLite database.
    query(sql: str) -> list
        Run a SELECT query to the database.
    clear_results() -> None
        Clear all results from the SQLite database.
    """

    def __init__(
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
        from openbb_core.provider.utils.websockets.helpers import get_logger

        self.results_file = None
        self.table_exists = False
        self._exception = None
        self.logger = logger if logger else get_logger("openbb.websocket.database")

        if not results_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                self.results_path = Path(temp_file_path).absolute()
                self.results_file = temp_file_path
        elif results_file and "://" in results_file:
            self.results_file = results_file
            self.results_path = results_file  # type: ignore
            kwargs["uri"] = True
        else:
            self.results_path = Path(results_file).absolute()
            self.results_file = results_file

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
                        self._exception = e
                        raise OpenBBError(msg) from e

            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                cursor = await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL
                    )
                """
                )
                await cursor.close()
                await conn.commit()
                self.table_exists = True
        except Exception as e:
            msg = (
                "Unexpected error while creating SQLite database ->"
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            self._exception = e  # type: ignore
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

            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                cursor = await conn.execute("PRAGMA journal_mode=WAL;")
                await cursor.close()
                if not self.table_exists:
                    cursor = await conn.execute(
                        f"""
                        CREATE TABLE IF NOT EXISTS {self.table_name} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            message TEXT NOT NULL
                        )
                    """
                    )
                    await conn.commit()
                    await cursor.close()
                    self.table_exists = True
                cursor = await conn.execute(
                    f"""
                    INSERT INTO {self.table_name} (message)
                    VALUES (?)
                """,  # noqa
                    (message,),
                )
                await conn.commit()
                await cursor.close()

                if self.limit is not None:
                    count = await conn.execute(
                        f"SELECT COUNT(*) FROM {self.table_name}"  # noqa
                    )
                    current_count = int((await count.fetchone())[0])
                    await count.close()
                    limit = 0 if int(self.limit) < 0 else int(self.limit)

                    if current_count > limit and limit != 0:
                        del_cursor = await conn.execute(
                            f"""
                            DELETE FROM {self.table_name}
                            WHERE id IN (
                                SELECT id FROM {self.table_name}
                                ORDER BY id DESC
                                LIMIT -1 OFFSET ?
                            )
                        """,  # noqa: S608
                            (limit,),
                        )
                        await del_cursor.close()

                    await conn.commit()

        except Exception as e:  # pylint: disable=broad-except
            raise e from e

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
            self._exception = e  # type: ignore
            raise OpenBBError(msg) from e

    async def _fetch_all(self, limit: Optional[int] = None) -> list:
        """Read the WebSocket message from the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite  # noqa

        try:
            rows: list = []
            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn:
                query = (
                    f"SELECT message FROM {self.table_name} ORDER BY id DESC"  # noqa
                )
                if limit:
                    query += f" LIMIT {limit}"
                async with conn.execute(query) as cursor:
                    async for row in cursor:
                        rows.append(self.deserialize_row(row))

            return rows

        except Exception as e:
            raise e from e

    def deserialize_row(self, row: str) -> Union["BaseModel", Any]:
        """Deserialize a row from the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import json

        try:
            return (
                self.data_model.model_validate_json(row[0])
                if self.data_model is not None
                else (
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
            )
        except Exception as e:
            msg = (
                "Unexpected error while deserializing row -> "
                f" {e.__class__.__name__ if hasattr(e, '__class__') else e} -> {e.args}"
            )
            self.logger.error(msg)
            self._exception = e  # type: ignore
            raise OpenBBError(msg) from e

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
            self._exception = e  # type: ignore
            raise OpenBBError(msg) from e

    async def _query_db(self, sql) -> list:
        """Query the SQLite database."""
        # pylint: disable=import-outside-toplevel
        import aiosqlite  # noqa
        import json

        query = (
            sql
            if sql.startswith("SELECT")
            else f"SELECT message FROM {self.table_name} WHERE {sql}"  # noqa
        )
        if not query.endswith(";"):
            query += ";"

        if not query.startswith("SELECT"):
            raise OpenBBError(
                "Operation not allowed. Only 'SELECT' operations allowed."
            )
        rows: list = []
        try:
            async with aiosqlite.connect(
                self.results_file, loop=self.loop, **self.kwargs
            ) as conn, conn.execute(query) as cursor:
                async for row in cursor:
                    rows.append(
                        self.data_model.model_validate_json(row[0])
                        if self.data_model is not None
                        and query.startswith(
                            f"SELECT message FROM {self.table_name}"  # noqa
                        )
                        else (
                            json.loads(row[0])
                            if (
                                (
                                    isinstance(row[0], str)
                                    and (
                                        row[0].startswith("{") or row[0].startswith("[")
                                    )
                                )
                                or isinstance(row[0], bytes)
                            )
                            else row[0]
                        )
                    )
            return rows
        except Exception as e:  # pylint: disable=broad-except
            raise e from e

    def query(self, sql: str) -> list:
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
            return run_async(self._query_db, sql)
        except Exception as e:  # pylint: disable=broad-except
            msg = f"Unexpected error while querying SQLite database -> {e.__class__.__name__}: {e}"
            self.logger.error(msg)
            raise OpenBBError(e) from e

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
            raise e from e

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
