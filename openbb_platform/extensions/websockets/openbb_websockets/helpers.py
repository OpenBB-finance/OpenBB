"""WebSockets helpers."""

import logging
import re
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import UnauthorizedError
from pydantic import ValidationError

AUTH_TOKEN_FILTER = re.compile(
    r"(auth_token=)([^&]*)",
    re.IGNORECASE | re.MULTILINE,
)

connected_clients: dict = {}


def clean_message(message: str) -> str:
    """Clean the message."""
    return AUTH_TOKEN_FILTER.sub(r"\1********", message)


def get_logger(name, level=logging.INFO):
    """Get a logger instance."""
    # pylint: disable=import-outside-toplevel
    import logging
    import uuid

    logger = logging.getLogger(f"{name}-{uuid.uuid4()}")
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(message)s\n")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger


def handle_validation_error(logger: logging.Logger, error: ValidationError):
    """Log and raise a Pydantic ValidationError from a provider connection."""
    err = f"{error.__class__.__name__} -> {error.title}: {error.json()}"
    logger.error(err)
    raise error from error


async def get_status(name: Optional[str] = None, client: Optional[Any] = None) -> dict:
    """Get the status of a client."""
    if name and name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    if not name and not client:
        raise OpenBBError("Either name or client must be provided.")
    client = client if client else connected_clients[name]
    provider_pid = client._psutil_process.pid if client.is_running else None
    broadcast_pid = (
        client._psutil_broadcast_process.pid if client.is_broadcasting else None
    )
    status = {
        "name": client.name,
        "auth_required": client._auth_token is not None,
        "subscribed_symbols": client.symbol,
        "is_running": client.is_running,
        "provider_pid": provider_pid,
        "is_broadcasting": client.is_broadcasting,
        "broadcast_address": client.broadcast_address,
        "broadcast_pid": broadcast_pid,
        "results_file": client.results_file,
        "table_name": client.table_name,
        "save_results": client.save_results,
    }
    return status


def encrypt_value(key, iv, value):
    """Encrypt a value before storing."""
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted_value = encryptor.update(value.encode()) + encryptor.finalize()
    return base64.b64encode(encrypted_value).decode()


def decrypt_value(key, iv, encrypted_value):
    """Decrypt the value for use."""
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_value = (
        decryptor.update(base64.b64decode(encrypted_value)) + decryptor.finalize()
    )
    return decrypted_value.decode()


async def check_auth(name: str, auth_token: Optional[str] = None) -> bool:
    """Check the auth token."""
    if name not in connected_clients:
        raise OpenBBError(f"Client {name} not connected.")
    client = connected_clients[name]
    if client._auth_token is None:
        return True
    if auth_token is None:
        raise UnauthorizedError(f"Client authorization token is required for {name}.")
    if auth_token != client._decrypt_value(client._auth_token):
        raise UnauthorizedError(f"Invalid client authorization token for {name}.")
    return True


def handle_termination_signal(logger):
    """Handle termination signals to ensure graceful shutdown."""
    # pylint: disable=import-outside-toplevel
    import sys

    logger.info(
        "PROVIDER INFO:      Termination signal received. WebSocket connection closed."
    )
    sys.exit(0)


def parse_kwargs():
    """Parse command line keyword arguments."""
    # pylint: disable=import-outside-toplevel
    import json
    import sys

    args = sys.argv[1:].copy()
    _kwargs: dict = {}
    for i, arg in enumerate(args):
        if arg.startswith("url"):
            _kwargs["url"] = arg[4:]
            continue
        if "=" in arg:
            key, value = arg.split("=")

            if key == "connect_kwargs":
                value = {} if value == "None" else json.loads(value)

            _kwargs[key] = value
        elif arg.startswith("--"):
            key = arg[2:]

            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]

                if isinstance(value, str) and value.lower() in ["false", "true"]:
                    value = value.lower() == "true"
                elif isinstance(value, str) and value.lower() == "none":
                    value = None
                _kwargs[key] = value
            else:
                _kwargs[key] = True

    return _kwargs


async def setup_database(results_path, table_name):
    """Setup the SQLite database."""
    # pylint: disable=import-outside-toplevel
    import os  # noqa
    import aiosqlite

    async with aiosqlite.connect(results_path) as conn:
        if os.path.exists(results_path):
            try:
                await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            except aiosqlite.DatabaseError:
                os.remove(results_path)

    async with aiosqlite.connect(results_path) as conn:
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT
            )
        """
        )
        await conn.commit()


async def write_to_db(message, results_path, table_name, limit):
    """Write the WebSocket message to the SQLite database."""
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    import aiosqlite

    conn = await aiosqlite.connect(results_path)

    # Check if the table exists and create it if it doesn't
    await conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
    """
    )
    await conn.commit()

    await conn.execute(
        f"INSERT INTO {table_name} (message) VALUES (?)",  # noqa
        (json.dumps(message),),
    )
    await conn.commit()

    records = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa
    count = (await records.fetchone())[0]
    count = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa
    current_count = int((await count.fetchone())[0])
    limit = 0 if limit is None else int(limit)

    if current_count > limit and limit != 0:
        await conn.execute(
            f"""
            DELETE FROM {table_name}
            WHERE id IN (
                SELECT id FROM {table_name}
                ORDER BY id DESC
                LIMIT -1 OFFSET ?
            )
        """,  # noqa: S608
            (limit,),
        )

    await conn.commit()
    await conn.close()


class StdOutSink:
    """Filter stdout for PII."""

    def write(self, message):
        """Write to stdout."""
        # pylint: disable=import-outside-toplevel
        import sys

        cleaned_message = AUTH_TOKEN_FILTER.sub(r"\1********", message)
        if cleaned_message != message:
            cleaned_message = f"{cleaned_message}\n"
        sys.__stdout__.write(cleaned_message)

    def flush(self):
        """Flush stdout."""
        # pylint: disable=import-outside-toplevel
        import sys

        sys.__stdout__.flush()


class AuthTokenFilter(logging.Formatter):
    """Custom logging formatter to filter auth tokens."""

    def format(self, record):
        """Format the log record."""
        original_message = super().format(record)
        cleaned_message = AUTH_TOKEN_FILTER.sub(r"\1********", original_message)
        return cleaned_message


class MessageQueue:
    def __init__(self, max_size: int = 1000, max_retries=5, backoff_factor=0.5):
        """Initialize the MessageQueue."""
        # pylint: disable=import-outside-toplevel
        from asyncio import Queue

        self.queue = Queue(maxsize=max_size)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = get_logger("openbb.websocket.queue")

    async def dequeue(self):
        """Dequeue a message."""
        return await self.queue.get()

    async def enqueue(self, message):
        """Enqueue a message."""
        # pylint: disable=import-outside-toplevel
        from asyncio import sleep
        from queue import Full

        retries = 0
        while retries < self.max_retries:
            try:
                await self.queue.put(message)
                return
            except Full:
                retries += 1
                msg = f"Queue is full. Retrying {retries}/{self.max_retries}..."
                self.logger.warning(msg)
                await sleep(self.backoff_factor * retries)
        self.logger.error("Failed to enqueue message after maximum retries.")

    async def process_queue(self, handler):
        """Process the message queue."""
        while True:
            message = await self.queue.get()
            await self._process_message(message, handler)
            self.queue.task_done()

    async def _process_message(self, message, handler):
        """Process the message with the handler coroutine."""
        await handler(message)
