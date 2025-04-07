"""WebSocket Helper Functions."""

# pylint: disable=protected-access

import logging
import re
from typing import TYPE_CHECKING

from pydantic import ValidationError

if TYPE_CHECKING:
    import threading

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
    formatter = logging.Formatter("%(message)s")
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
    logger.info(
        "PROVIDER INFO:      Termination signal received. WebSocket connection closed."
    )
    raise SystemExit("Termination signal received.")


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


def kill_thread(thread: "threading.Thread") -> None:
    """Kill thread by setting a stop flag."""
    # pylint: disable=import-outside-toplevel
    import asyncio
    import ctypes

    if hasattr(thread, "loop") and thread.loop:
        for task in asyncio.all_tasks(thread.loop):
            task.cancel()

    if not thread.is_alive():
        return

    thread_id = thread.ident
    if thread_id is None:
        return

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id), ctypes.py_object(SystemExit)
    )
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
