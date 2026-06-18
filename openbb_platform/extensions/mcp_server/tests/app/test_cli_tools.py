"""Tests for ``openbb_mcp_server.app.cli_tools``."""

import sys
import types
from typing import Any

import pytest

from openbb_mcp_server.app import cli_tools


@pytest.fixture
def fake_dispatchers(monkeypatch):
    """Stub out ``openbb_cli.dispatchers`` for capture-and-replay testing."""

    class FakeRequest:
        def __init__(self, command, params=None, id=None):
            self.command = command
            self.params = params or {}
            self.id = id

    class FakeResponse:
        def __init__(self, *, id=None, ok=True, result=None, error=None):
            self.id = id
            self.ok = ok
            self.result = result
            self.error = error

        def model_dump(self, mode="json"):  # noqa: ARG002
            return {"id": self.id, "ok": self.ok, "result": self.result}

    class FakeLocalDispatcher:
        instances: list = []

        def __init__(self):
            self.dispatched: list = []
            FakeLocalDispatcher.instances.append(self)

        async def dispatch(self, request):
            self.dispatched.append(("local", request.command, request.params))
            return FakeResponse(
                id=request.id, ok=True, result={"echo": request.command}
            )

        async def describe(self, command):
            return {"local_describe": command}

    class FakeHttpDispatcher:
        instances: list = []

        def __init__(self, *, base_url):
            self.server_url = base_url
            self.dispatched: list = []
            FakeHttpDispatcher.instances.append(self)

        async def dispatch(self, request):
            self.dispatched.append(("http", self.server_url, request.command))
            return FakeResponse(
                id=request.id, ok=True, result={"http_url": self.server_url}
            )

        async def describe(self, command):
            return {"http_describe": command, "url": self.server_url}

    fake_dispatchers_pkg = types.ModuleType("openbb_cli.dispatchers")
    fake_dispatchers_pkg.LocalDispatcher = FakeLocalDispatcher  # type: ignore
    fake_dispatchers_pkg.HttpDispatcher = FakeHttpDispatcher  # type: ignore
    fake_dispatchers_pkg.Request = FakeRequest  # type: ignore

    fake_openbb_cli = types.ModuleType("openbb_cli")
    fake_openbb_cli.dispatchers = fake_dispatchers_pkg  # type: ignore

    monkeypatch.setitem(sys.modules, "openbb_cli", fake_openbb_cli)
    monkeypatch.setitem(sys.modules, "openbb_cli.dispatchers", fake_dispatchers_pkg)

    return {
        "Request": FakeRequest,
        "Response": FakeResponse,
        "Local": FakeLocalDispatcher,
        "Http": FakeHttpDispatcher,
    }


class FakeMCP:
    """Minimal stand-in for ``FastMCP`` capturing tool registrations."""

    def __init__(self):
        self.tools: dict = {}

    def tool(self, *, tags=None):
        del tags

        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


def test_openbb_cli_available_reports_false_when_missing(monkeypatch):
    """``_openbb_cli_available`` is False when ``openbb_cli`` isn't importable."""
    monkeypatch.setitem(sys.modules, "openbb_cli", None)
    monkeypatch.setitem(sys.modules, "openbb_cli.dispatchers", None)
    assert cli_tools._openbb_cli_available() is False


def test_openbb_cli_available_reports_true_when_present(fake_dispatchers):
    """With the stubbed package present, the gate returns True."""
    assert cli_tools._openbb_cli_available() is True


def test_register_cli_tools_returns_false_when_missing(monkeypatch, caplog):
    """No openbb-cli installed: ``register_cli_tools`` returns False."""
    monkeypatch.setitem(sys.modules, "openbb_cli", None)
    monkeypatch.setitem(sys.modules, "openbb_cli.dispatchers", None)

    mcp = FakeMCP()
    out = cli_tools.register_cli_tools(mcp)
    assert out is False
    assert mcp.tools == {}


def test_register_cli_tools_registers_three_tools(fake_dispatchers):
    """With openbb-cli present, three tools are registered."""
    mcp = FakeMCP()
    out = cli_tools.register_cli_tools(mcp)
    assert out is True
    assert set(mcp.tools) == {
        "openbb_dispatch",
        "openbb_batch_dispatch",
        "openbb_describe_command",
    }


@pytest.mark.asyncio
async def test_dispatch_local_path(fake_dispatchers, monkeypatch):
    """No ``server_url`` routes through ``LocalDispatcher``."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out: dict[str, Any] = await mcp.tools["openbb_dispatch"](
        command="equity.price.historical",
        params={"symbol": "AAPL"},
    )
    assert out["ok"] is True
    assert out["result"] == {"echo": "equity.price.historical"}
    assert fake_dispatchers["Local"].instances[-1].dispatched == [
        ("local", "equity.price.historical", {"symbol": "AAPL"})
    ]


@pytest.mark.asyncio
async def test_dispatch_uses_explicit_server_url(fake_dispatchers, monkeypatch):
    """``server_url`` arg routes through HttpDispatcher."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_dispatch"](
        command="economy.gdp", server_url="https://api.example.com"
    )
    assert out["result"] == {"http_url": "https://api.example.com"}
    assert fake_dispatchers["Http"].instances[-1].server_url == (
        "https://api.example.com"
    )


@pytest.mark.asyncio
async def test_dispatch_falls_back_to_env_url(fake_dispatchers, monkeypatch):
    """``OPENBB_SERVER_URL`` env var is consulted when no arg supplied."""
    monkeypatch.setenv("OPENBB_SERVER_URL", "https://from-env.example.com")
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_dispatch"](command="economy.gdp")
    assert out["result"]["http_url"] == "https://from-env.example.com"


@pytest.mark.asyncio
async def test_dispatch_caches_local_singleton(fake_dispatchers, monkeypatch):
    """Repeated local dispatch reuses the same LocalDispatcher instance."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    await mcp.tools["openbb_dispatch"](command="a.b")
    await mcp.tools["openbb_dispatch"](command="c.d")
    assert len(fake_dispatchers["Local"].instances) == 1


@pytest.mark.asyncio
async def test_dispatch_caches_http_per_url(fake_dispatchers, monkeypatch):
    """Distinct server URLs → distinct HttpDispatcher instances."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    await mcp.tools["openbb_dispatch"](command="a", server_url="https://one")
    await mcp.tools["openbb_dispatch"](command="b", server_url="https://two")
    await mcp.tools["openbb_dispatch"](command="c", server_url="https://one")
    instances = fake_dispatchers["Http"].instances
    urls = sorted({i.server_url for i in instances})
    assert urls == ["https://one", "https://two"]


@pytest.mark.asyncio
async def test_batch_dispatch_runs_each_request(fake_dispatchers, monkeypatch):
    """Batch returns one result per input, in the same order."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_batch_dispatch"](
        requests=[
            {"command": "a.b", "id": "r1"},
            {"command": "c.d", "params": {"x": 1}, "id": "r2"},
        ],
    )
    assert [r["id"] for r in out] == ["r1", "r2"]
    assert all(r["ok"] for r in out)


@pytest.mark.asyncio
async def test_batch_dispatch_routes_to_http_when_url_set(
    fake_dispatchers, monkeypatch
):
    """``server_url`` flows through to the HTTP dispatcher."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_batch_dispatch"](
        requests=[{"command": "x"}], server_url="https://api"
    )
    assert out[0]["result"] == {"http_url": "https://api"}


@pytest.mark.asyncio
async def test_describe_local(fake_dispatchers, monkeypatch):
    """Local describe returns the local dispatcher's metadata."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_describe_command"](command="equity.price")
    assert out == {"local_describe": "equity.price"}


@pytest.mark.asyncio
async def test_describe_http(fake_dispatchers, monkeypatch):
    """HTTP describe routes through the URL'd dispatcher."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_describe_command"](
        command="x", server_url="https://api.example.com"
    )
    assert out == {"http_describe": "x", "url": "https://api.example.com"}


@pytest.mark.asyncio
async def test_describe_local_missing_method(fake_dispatchers, monkeypatch):
    """Older openbb-cli without ``describe`` raises a clear RuntimeError."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    fake_dispatchers["Local"].describe = None  # type: ignore
    delattr(fake_dispatchers["Local"], "describe")
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    with pytest.raises(RuntimeError, match="Local describe"):
        await mcp.tools["openbb_describe_command"](command="x")


@pytest.mark.asyncio
async def test_describe_http_missing_method(fake_dispatchers, monkeypatch):
    """Older HTTP dispatcher missing ``describe`` raises RuntimeError."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    delattr(fake_dispatchers["Http"], "describe")
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    with pytest.raises(RuntimeError, match="Remote describe"):
        await mcp.tools["openbb_describe_command"](
            command="x", server_url="https://api"
        )


@pytest.mark.asyncio
async def test_describe_local_sync_method(fake_dispatchers, monkeypatch):
    """``describe`` may be a sync function; the tool should not await it."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)

    def sync_describe(self, command):
        return {"sync_describe": command}

    fake_dispatchers["Local"].describe = sync_describe  # type: ignore

    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_describe_command"](command="x")
    assert out == {"sync_describe": "x"}


@pytest.mark.asyncio
async def test_describe_http_sync_method(fake_dispatchers, monkeypatch):
    """Same path on the HTTP side."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)

    def sync_http_describe(self, command):
        return {"sync_http": command}

    fake_dispatchers["Http"].describe = sync_http_describe  # type: ignore

    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    out = await mcp.tools["openbb_describe_command"](
        command="y", server_url="https://api"
    )
    assert out == {"sync_http": "y"}


def test_is_coroutine_function_helper():
    """``_is_coroutine_function`` mirrors ``inspect.iscoroutinefunction``."""

    async def coro():  # pragma: no cover
        return None

    def sync():  # pragma: no cover
        return None

    assert cli_tools._is_coroutine_function(coro) is True
    assert cli_tools._is_coroutine_function(sync) is False


@pytest.mark.asyncio
async def test_dispatch_invokes_with_default_params(fake_dispatchers, monkeypatch):
    """``params=None`` defaults to an empty dict on the dispatcher."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FakeMCP()
    cli_tools.register_cli_tools(mcp)
    await mcp.tools["openbb_dispatch"](command="x")
    assert fake_dispatchers["Local"].instances[-1].dispatched[-1][2] == {}
