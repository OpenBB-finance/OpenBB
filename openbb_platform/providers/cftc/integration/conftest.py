import base64
import threading
import time

import pytest


@pytest.fixture(scope="session")
def api_server(pytestconfig):
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
    from openbb_core.env import Env

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    base64_bytes = base64.b64encode(userpass.encode("ascii"))

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
