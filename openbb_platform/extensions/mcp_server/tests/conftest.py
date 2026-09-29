"""Shared fixtures and ``openbb_core`` submodule bindings for the test suite."""

import atexit
import importlib
import logging
import shutil
import socket
import sys
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _register_fixture_extension() -> None:
    """Expose ``openbb_mcp_fixture.router`` as an ``openbb_core_extension`` entry point."""
    metadata_root = Path(tempfile.mkdtemp(prefix="openbb_mcp_fixture_"))
    atexit.register(shutil.rmtree, metadata_root, ignore_errors=True)
    dist_info = metadata_root / "openbb_mcp_fixture-0.0.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: openbb-mcp-fixture\nVersion: 0.0.0\n",
        encoding="utf-8",
    )
    (dist_info / "entry_points.txt").write_text(
        "[openbb_core_extension]\nmcp_fixture = openbb_mcp_fixture.router:router\n",
        encoding="utf-8",
    )
    sys.path[:0] = [str(FIXTURES_DIR), str(metadata_root)]
    importlib.invalidate_caches()
    from openbb_core.app.extension_loader import ExtensionLoader

    type(ExtensionLoader)._instances.pop(ExtensionLoader, None)


_register_fixture_extension()

import openbb_core.api
import openbb_core.api.app_loader
import openbb_core.api.exception_handlers
import openbb_core.app.model
import openbb_core.app.model.credentials
import openbb_core.app.service
import openbb_core.app.service.system_service
import openbb_core.app.service.user_service  # noqa: F401
import pytest
import uvicorn

for _parent, _children in (
    ("openbb_core.api", ("app_loader", "exception_handlers")),
    ("openbb_core.app.model", ("credentials",)),
    ("openbb_core.app.service", ("system_service", "user_service")),
):
    _pkg = sys.modules[_parent]
    for _child in _children:
        setattr(_pkg, _child, sys.modules[f"{_parent}.{_child}"])


@pytest.fixture
def app_caplog(caplog):
    """Return ``caplog`` with the fastmcp logger chain propagating to the root logger.

    Yields
    ------
    pytest.LogCaptureFixture
        The capture fixture, now receiving ``openbb_mcp_server.app.app`` records.
    """
    from openbb_mcp_server.app.app import logger as app_logger

    chain = []
    current: logging.Logger | None = app_logger
    while current is not None and current is not logging.root:
        chain.append((current, current.propagate))
        current.propagate = True
        current = current.parent
    yield caplog
    for chained, propagate in chain:
        chained.propagate = propagate


@pytest.fixture
def isolated_config(tmp_path, monkeypatch):
    """Point every ``openbb-core`` config layer at empty temporary locations.

    Returns
    -------
    pathlib.Path
        The empty working directory the test now runs in.
    """
    from openbb_core.app.config import loader

    from openbb_mcp_server.app.config import EXPLICIT_CONFIG_ENVS

    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setattr(loader, "USER_OPENBB_DIR", tmp_path / "openbb_platform")
    for name in (*EXPLICIT_CONFIG_ENVS, loader.EXPLICIT_ENV_FILE_ENV):
        monkeypatch.delenv(name, raising=False)
    return work


@contextmanager
def serve_app(app) -> Iterator[str]:
    """Serve an ASGI app with uvicorn on a free loopback port.

    Parameters
    ----------
    app : ASGIApp
        The application to serve.

    Yields
    ------
    str
        The server's base URL.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning", ws="none"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]})
    thread.start()
    while thread.is_alive() and not server.started:
        time.sleep(0.01)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join()
        sock.close()


@pytest.fixture(scope="session")
def serve():
    """Return the ``serve_app`` context manager for module-scoped server fixtures."""
    return serve_app
