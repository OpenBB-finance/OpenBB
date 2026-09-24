"""Small infrastructure helpers shared across the API extension.

Kept deliberately tiny — these are the bits that don't belong with the
FastAPI app boot path (``app/``), the higher-level service flows
(``service/``), or the spec-shaping utilities (``openapi.py``,
``widgets.py``). Pure functions only, no side effects beyond the
network probe.
"""

import json
import socket
from pathlib import Path


def check_port(host: str, port: int | str) -> int:
    """Return the first free port at or above ``port`` on ``host``.

    Walks upward one port at a time until ``socket.connect_ex`` reports
    "nothing listening" (a non-zero result code). Used by ``launch_api``
    to gracefully fall through to the next port when the user's
    requested one is already taken.
    """
    port = int(port)
    not_free = True
    while not_free:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex((host, port))
            if res != 0:
                not_free = False
            else:
                port += 1
    return port


def get_user_settings(current_user_settings: str) -> dict:
    """Load the user's ``user_settings.json`` (or return a clean default).

    The Workspace launcher needs ``preferences.data_directory`` to
    decide where ``apps.json`` lives. When the file doesn't exist
    (fresh install, or running in a sandbox) we hand back the
    canonical empty shape so callers can still ``.get("preferences", {})``
    without ``KeyError``.
    """
    if Path(current_user_settings).exists():
        with open(current_user_settings, encoding="utf-8") as f:
            user_settings = json.load(f)
    else:
        user_settings = {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }
    return user_settings
