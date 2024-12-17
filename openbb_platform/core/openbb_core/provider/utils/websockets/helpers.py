"""WebSocket Helper Functions."""

# pylint: disable=protected-access

import logging
import re

from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

AUTH_TOKEN_FILTER = re.compile(
    r"(auth_token=)([^&]*)",
    re.IGNORECASE | re.MULTILINE,
)


def clean_message(message: str) -> str:
    """Clean the message."""
    return AUTH_TOKEN_FILTER.sub(r"\1********", message)


def get_logger(name, level=logging.INFO):
    """Get a logger instance."""
    # pylint: disable=import-outside-toplevel
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


def handle_termination_signal(logger):
    """Handle termination signals to ensure graceful shutdown."""
    # pylint: disable=import-outside-toplevel
    import sys

    logger.info(
        "PROVIDER INFO:      Termination signal received. WebSocket connection closed."
    )
    sys.exit(0)


def parse_kwargs() -> dict:
    """
    Parse command line keyword arguments supplied to a script file.

    Accepts arguments in the form of `key=value` or `--key value`.

    Keys and values should not contain spaces.

    Returns
    -------
    dict
        A Python dictionary with the parsed kwargs.
    """
    # pylint: disable=import-outside-toplevel
    import json
    import sys

    args = sys.argv[1:].copy()
    _kwargs: dict = {}
    for i, arg in enumerate(args):
        if arg.startswith("url") or arg.startswith("uri"):
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
                    value = value.lower() == "true"  # type: ignore
                elif isinstance(value, str) and value.lower() == "none":
                    value = None
                _kwargs[key] = value
            else:
                _kwargs[key] = True

    return _kwargs


async def setup_database(results_path, table_name):
    """Create the SQLite database, if required."""
    # pylint: disable=import-outside-toplevel
    import os  # noqa
    import aiosqlite

    if os.path.exists(results_path):
        async with aiosqlite.connect(results_path) as conn:
            try:
                await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            except aiosqlite.DatabaseError as e:
                raise OpenBBError(
                    "Unexpected error caused by an invalid SQLite database file."
                    "Please check the path, and inspect the file if it exists."
                    + f" -> {e}"
                ) from e

    async with aiosqlite.connect(results_path) as conn:
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message JSON
            )
        """
        )
        await conn.commit()


async def write_to_db(message, results_path, table_name, limit):
    """Write the WebSocket message to the SQLite database."""
    # pylint: disable=import-outside-toplevel
    import aiosqlite

    conn = await aiosqlite.connect(results_path)
    await conn.execute("PRAGMA journal_mode=WAL;")
    try:
        # Check if the table exists and create it if it doesn't
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message JSON
            )
        """
        )
        await conn.commit()

        await conn.execute(
            f"INSERT INTO {table_name} (message) VALUES (?)",  # noqa
            (message,),
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
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(
            f"Unexpected error encountered while inserting message into the database. -> {e.__class__.__name__}: {e}"
        ) from e

    finally:
        await conn.close()
