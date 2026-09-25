"""Shared fixtures and ``openbb_core`` submodule bindings for the test suite."""

import importlib
import logging
import shutil
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, distribution
from importlib.util import find_spec
from pathlib import Path

FIXTURE_EXTENSION = Path(__file__).parent / "fixtures" / "openbb_mcp_fixture"


def _pip_install_command() -> list[str]:
    """Return the command that installs packages into the running interpreter.

    Returns
    -------
    list[str]
        ``uv pip install`` when uv is available, otherwise ``pip install``.
    """
    if find_spec("uv"):
        return [
            sys.executable,
            "-m",
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
        ]
    if uv := shutil.which("uv"):
        return [uv, "pip", "install", "--python", sys.executable]
    return [sys.executable, "-m", "pip", "install"]


def _install_fixture_extension() -> None:
    """Install the ``openbb-mcp-fixture`` extension the tests dispatch against."""
    try:
        distribution("openbb-mcp-fixture")
    except PackageNotFoundError:
        subprocess.run(  # noqa: S603
            [
                *_pip_install_command(),
                "--no-deps",
                "--editable",
                str(FIXTURE_EXTENSION),
            ],
            check=True,
        )
        if str(FIXTURE_EXTENSION) not in sys.path:
            sys.path.append(str(FIXTURE_EXTENSION))
        importlib.invalidate_caches()
        from openbb_core.app.extension_loader import ExtensionLoader

        type(ExtensionLoader)._instances.pop(ExtensionLoader, None)


_install_fixture_extension()

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
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]})
    thread.start()
    while not server.started:
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
