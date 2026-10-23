"""Integration-test fixtures for openbb-famafrench.

The API-interface tests (``test_famafrench_api.py``) need a live HTTP server.
This module runs ``openbb_core.api.rest_api:app`` in a background thread for
the duration of the integration session and exposes the auth ``headers``.
"""

import base64
import threading
import time

import pytest


@pytest.fixture(scope="session")
def api_server(pytestconfig):
    """Run the OpenBB REST API on localhost:8000 for the integration session."""
    if pytestconfig.getoption("markexpr") == "not integration":
        yield None
        return

    import uvicorn
    from openbb_core.api.rest_api import app

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 60
    while time.time() < deadline:
        if server.started:
            break
        time.sleep(0.25)
    else:  # pragma: no cover
        raise RuntimeError("The OpenBB REST API did not start within 60s.")

    yield server

    server.should_exit = True
    thread.join(timeout=15)


@pytest.fixture(scope="session")
def headers(api_server):
    """HTTP Basic auth headers; depends on api_server so the server is live."""
    from openbb_core.env import Env

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
