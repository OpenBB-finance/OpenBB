import asyncio
import contextlib
import logging
from typing import Any, AsyncIterator, Optional

from sqlalchemy import Index
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import insert, text
from sqlalchemy.types import JSON

DATABASE_URL = "sqlite+aiosqlite:///" + __file__.replace("database.py", "sqlite.db")

JSON_Base: DeclarativeMeta = declarative_base(
    type_annotation_map={
        dict[str, Any]: JSON,
    }
)

logger = logging.getLogger(__name__)


class WebSocketMessages(JSON_Base):
    """Table to store messages from the WebSocket server."""

    __tablename__ = "records"

    id: Mapped[Optional[int]] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    message: Mapped[dict[str, Any]] = mapped_column(type_=JSON, nullable=False)

    __table_args__ = (
        Index("idx_symbol", text("message->>'symbol'")),
        Index("idx_date", text("message->>'date'")),
    )


class DatabaseSessionManager:
    """Manages the database connection and session creation."""

    def __init__(self, host: str, **engine_kwargs: Any):
        """
        Initialize the DatabaseSessionManager.

        Parameters
        ----------
        host : str
            The database URL.
        **engine_kwargs : Any
            Additional keyword arguments to pass to the engine.
        """
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def close(self):
        """Close the database connection."""
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    async def create_all(self):
        """Create all tables in the database."""
        base = [JSON_Base]
        async with self._engine.begin() as conn:
            for b in base:
                await conn.run_sync(b.metadata.create_all)

    async def set_pragmas(self, connection: AsyncConnection, read_only: bool = False):
        """Set the PRAGMA statements for the connection."""
        pragmas = [
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=off",
        ]
        if read_only:
            await connection.execute(text("PRAGMA query_only=ON"))
        else:
            for pragma in pragmas:
                await connection.execute(text(pragma))

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Connect to the database."""
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            await self.set_pragmas(connection)
            yield connection

    @contextlib.asynccontextmanager
    async def read_session(self) -> AsyncIterator[AsyncSession]:
        """Create a read-only session."""
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.connect() as connection:
            await self.set_pragmas(connection, read_only=True)
            async with self._sessionmaker(bind=connection) as session:
                yield session

    @contextlib.asynccontextmanager
    async def write_session(self) -> AsyncIterator[AsyncSession]:
        """Create a write session."""
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            await self.set_pragmas(connection)
            async with self._sessionmaker(bind=connection) as session:
                try:
                    yield session
                    await session.flush()  # Explicitly flush before the transaction commits
                except Exception:
                    # Let the engine.begin() context manager handle rollback
                    raise


class WebSocketDatabaseSession:
    """Manages the database connection and session creation for the WebSocket client."""

    def __init__(
        self,
        host: str,
        batch_size: int = 100,
        batch_interval: int = 1,
        echo=False,
        poolclass=NullPool,
        queue: asyncio.Queue = None,
        logger: logging.Logger = None,
        **kw: Any,
    ):
        """
        Initialize the WebSocketDatabaseSession.

        Parameters
        ----------
        host : str
            The database URL.
        batch_size : int, optional
            The number of messages to write to the database at once, by default 100.
        batch_interval : int, optional
            The interval in seconds to write messages to the database, by default 1.
        echo : bool, optional
            Echo SQL statements to the console, by default False.
        poolclass : Pool, optional
            The pool class to use for the database connection, by default NullPool.
        queue : asyncio.Queue, optional
            The queue to store messages, by default None.
        logger : logging.Logger, optional
            The logger to use for logging, by default None.
        **kw : Any
            Additional keyword arguments to pass to the DatabaseSessionManager.
        """
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.queue = queue or asyncio.Queue()
        self.writer_task_running = False
        self.prune_task_running = False

        if "sqlite+aiosqlite:///" not in host:
            raise ValueError("Only SQLite databases are supported")

        self._session_manager = DatabaseSessionManager(
            host, echo=echo, poolclass=poolclass, **kw
        )
        self.get_read_session = self._session_manager.read_session
        self.get_write_session = self._session_manager.write_session

    async def create_all(self):
        """Create all tables in the database."""
        await self._session_manager.create_all()

    async def close(self):
        """Close the database connection."""
        await self._session_manager.close()

    async def stop_writer_task(self):
        """Stop the writer task."""
        self.writer_task_running = False

    async def start_writer_task(self):
        """Start the writer task."""
        self.writer_task_running = True
        while True:
            messages: list = []
            if self.writer_task_running is False:
                break
            try:
                # Collect messsages in batches
                while len(messages) < self.batch_size:
                    try:
                        message = await asyncio.wait_for(
                            self.queue.get(), timeout=self.batch_interval
                        )
                        if message:
                            messages.append(message)
                    except asyncio.TimeoutError:
                        break
            except Exception as e:
                logger.error(f"Error in write_messages_to_db: {e}")
                # Continue to the next iteration of the outer loop
            if messages:
                try:
                    async with self._session_manager.write_session() as session:
                        try:
                            # Batch insert for more efficiency
                            await session.execute(
                                insert(WebSocketMessages),
                                [{"message": msg} for msg in messages],
                            )
                            # The context manager will handle the commit
                        except Exception as e:
                            logger.error(f"Error writing messages to database: {e}")
                            logger.error(f"Messages: {messages}")
                            # The context manager will handle rollback
                            raise
                except Exception as e:
                    logger.error(f"Error in database transaction: {e}")

        self.writer_task_running = False

    async def prune_database(self):
        """Prune the database at a set interval."""
        pass
