"""Serve the OpenBB REST API for the Deribit integration tests."""

import pytest


def _free_port() -> int:
    """Return a local port nothing is listening on."""
    import socket

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))

        return probe.getsockname()[1]


@pytest.fixture(scope="session")
def api():
    """Run the REST API on a free local port.

    Yields
    ------
    dict
        The base URL of the API and the authorization headers to call it with.

    Raises
    ------
    RuntimeError
        If the server does not start within a minute.
    """
    import base64
    import threading
    import time

    import uvicorn
    from openbb_core.api.rest_api import app
    from openbb_core.env import Env

    from openbb_deribit.utils.constants import API_PREFIX

    port = _free_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 60

    while not server.started:
        if time.monotonic() > deadline:
            raise RuntimeError("The OpenBB REST API did not start within 60 seconds.")

        time.sleep(0.25)

    credentials = base64.b64encode(
        f"{Env().API_USERNAME}:{Env().API_PASSWORD}".encode("ascii")
    ).decode("ascii")

    yield {
        "base": f"http://127.0.0.1:{port}{API_PREFIX}",
        "headers": {"Authorization": f"Basic {credentials}"},
    }

    server.should_exit = True
    thread.join(timeout=15)


@pytest.fixture(scope="session")
def obb():
    """Return the Python interface, built with this extension installed."""
    from openbb import obb as interface

    return interface
