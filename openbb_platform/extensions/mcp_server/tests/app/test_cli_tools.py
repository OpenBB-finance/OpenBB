"""Tests for ``openbb_mcp_server.app.cli_tools``."""

import sys

import pytest
from fastmcp import Client, FastMCP
from openbb_core.api.rest_api import app as rest_app

from openbb_mcp_server.app.cli_tools import _openbb_cli_available, register_cli_tools

CLI_TOOLS = {
    "openbb_dispatch",
    "openbb_batch_dispatch",
    "openbb_list_commands",
    "openbb_describe_command",
}
FIXTURE_COMMANDS = [
    {
        "name": "mcp_fixture.echo",
        "description": "Return deterministic rows for a symbol",
    },
    {
        "name": "mcp_fixture.fail",
        "description": "Raise an OpenBBError with the given message",
    },
    {
        "name": "mcp_fixture.scale",
        "description": "Multiply the ``index`` of every row by ``factor``",
    },
]


class _RecordingApp:
    """ASGI wrapper that records every requested HTTP path."""

    def __init__(self, app) -> None:
        self.app = app
        self.paths: list[str] = []

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            self.paths.append(scope["path"])
        await self.app(scope, receive, send)


@pytest.fixture(scope="module")
def rest_server(serve):
    """Serve the OpenBB REST API and yield ``(base_url, recording_app)``."""
    recording = _RecordingApp(rest_app)
    with serve(recording) as url:
        yield url, recording


@pytest.fixture
def cli_server(monkeypatch):
    """Return a FastMCP server carrying only the CLI tools."""
    monkeypatch.delenv("OPENBB_SERVER_URL", raising=False)
    mcp = FastMCP("cli")
    assert register_cli_tools(mcp) is True
    return mcp


@pytest.fixture
def without_openbb_cli(monkeypatch):
    """Make ``openbb_cli`` unimportable."""
    monkeypatch.setitem(sys.modules, "openbb_cli", None)
    monkeypatch.setitem(sys.modules, "openbb_cli.dispatchers", None)


async def _call(server, name: str, **arguments):
    async with Client(server) as client:
        result = await client.call_tool(name, arguments)
    content = result.structured_content or {}
    return content["result"] if name == "openbb_batch_dispatch" else content


def _fixture_commands(listing: dict) -> list[dict]:
    return [c for c in listing["result"] if c["name"].startswith("mcp_fixture.")]


class TestOpenbbCliAvailable:
    """Detecting the optional ``openbb-cli`` dependency."""

    def test_available_when_installed(self):
        """The installed ``openbb-cli`` is detected."""
        assert _openbb_cli_available() is True

    @pytest.mark.usefixtures("without_openbb_cli")
    def test_unavailable_when_missing(self):
        """A missing ``openbb-cli`` is reported."""
        assert _openbb_cli_available() is False


class TestRegisterCliTools:
    """Registering the dispatcher tools."""

    @pytest.mark.asyncio
    async def test_registers_the_dispatcher_tools(self, cli_server):
        """All four dispatcher tools are exposed."""
        async with Client(cli_server) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert names == CLI_TOOLS

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("without_openbb_cli")
    async def test_skips_registration_without_openbb_cli(self, caplog):
        """Without ``openbb-cli`` nothing is registered and the skip is logged."""
        mcp = FastMCP("cli")
        with caplog.at_level("INFO", logger="openbb_mcp_server.cli_tools"):
            assert register_cli_tools(mcp) is False
        async with Client(mcp) as client:
            assert await client.list_tools() == []
        assert "openbb-cli not installed" in caplog.text


class TestLocalDispatch:
    """Executing commands against the in-process ``obb``."""

    @pytest.mark.asyncio
    async def test_dispatch_returns_results(self, cli_server):
        """A successful command returns its serialized results."""
        out = await _call(
            cli_server,
            "openbb_dispatch",
            command="mcp_fixture.echo",
            params={"symbol": "MSFT", "rows": 2},
        )
        assert out == {
            "id": None,
            "ok": True,
            "result": {
                "results": [
                    {"symbol": "MSFT", "index": 0},
                    {"symbol": "MSFT", "index": 1},
                ]
            },
            "error": None,
        }

    @pytest.mark.asyncio
    async def test_dispatch_without_params_uses_defaults(self, cli_server):
        """Omitted params fall back to the command's defaults."""
        first = await _call(cli_server, "openbb_dispatch", command="mcp_fixture.echo")
        second = await _call(cli_server, "openbb_dispatch", command="mcp_fixture.echo")
        assert first["result"] == {"results": [{"symbol": "AAPL", "index": 0}]}
        assert second == first

    @pytest.mark.asyncio
    async def test_dispatch_reports_command_errors(self, cli_server):
        """A failing command returns a structured error instead of raising."""
        out = await _call(
            cli_server,
            "openbb_dispatch",
            command="mcp_fixture.fail",
            params={"message": "boom"},
        )
        assert out["ok"] is False
        assert out["error"]["type"] == "OpenBBError"
        assert "boom" in out["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_reports_unknown_commands(self, cli_server):
        """An unknown command returns a ``CommandNotFound`` error."""
        out = await _call(cli_server, "openbb_dispatch", command="mcp_fixture.nope")
        assert out["ok"] is False
        assert out["error"]["type"] == "CommandNotFound"

    @pytest.mark.asyncio
    async def test_batch_dispatch_keeps_input_order_and_ids(self, cli_server):
        """Batch responses follow the input order and echo each ``id``."""
        out = await _call(
            cli_server,
            "openbb_batch_dispatch",
            requests=[
                {"command": "mcp_fixture.echo", "params": {"symbol": "X"}, "id": "a"},
                {"command": "mcp_fixture.fail", "id": "b"},
                {"command": "mcp_fixture.echo"},
            ],
        )
        assert [(r["id"], r["ok"]) for r in out] == [
            ("a", True),
            ("b", False),
            (None, True),
        ]
        assert out[0]["result"] == {"results": [{"symbol": "X", "index": 0}]}


class TestLocalIntrospection:
    """Listing and describing commands of the in-process ``obb``."""

    @pytest.mark.asyncio
    async def test_list_and_describe_commands(self, cli_server):
        """The catalog lists the fixture commands and describes their parameters."""
        listing = await _call(cli_server, "openbb_list_commands")
        described = await _call(
            cli_server, "openbb_describe_command", command="mcp_fixture.echo"
        )
        assert listing["ok"] is True
        assert _fixture_commands(listing) == FIXTURE_COMMANDS
        assert described["ok"] is True
        assert described["result"]["name"] == "mcp_fixture.echo"
        assert described["result"]["parameters"] == [
            {
                "name": "symbol",
                "in": "query",
                "type": "string",
                "default": "AAPL",
                "help": "Symbol to echo back.",
            },
            {
                "name": "rows",
                "in": "query",
                "type": "integer",
                "default": 1,
                "help": "Number of rows to return.",
            },
        ]
        results = described["result"]["output_schema"]["properties"]["results"]
        rows = results["anyOf"][0]["items"]
        assert (rows["title"], rows["required"]) == ("EchoRow", ["symbol", "index"])

    @pytest.mark.asyncio
    async def test_describe_forwards_provider(self, cli_server):
        """A ``provider`` argument is forwarded to the schema lookup."""
        out = await _call(
            cli_server,
            "openbb_describe_command",
            command="mcp_fixture.echo",
            provider="fixture",
        )
        assert out["result"]["name"] == "mcp_fixture.echo"


class TestRemoteDispatch:
    """Executing and introspecting commands on a remote OpenBB REST server."""

    @pytest.mark.asyncio
    async def test_explicit_server_url(self, cli_server, rest_server):
        """``server_url`` routes every tool to the remote server."""
        url, _ = rest_server
        out = await _call(
            cli_server,
            "openbb_dispatch",
            command="mcp_fixture.echo",
            params={"symbol": "IBM", "rows": 2},
            server_url=url,
        )
        batch = await _call(
            cli_server,
            "openbb_batch_dispatch",
            requests=[{"command": "mcp_fixture.fail", "id": "f"}],
            server_url=url,
        )
        listing = await _call(cli_server, "openbb_list_commands", server_url=url)
        described = await _call(
            cli_server,
            "openbb_describe_command",
            command="mcp_fixture.echo",
            server_url=url,
        )
        assert out["ok"] is True
        assert out["result"]["results"] == [
            {"symbol": "IBM", "index": 0},
            {"symbol": "IBM", "index": 1},
        ]
        assert (batch[0]["id"], batch[0]["ok"]) == ("f", False)
        assert _fixture_commands(listing) == FIXTURE_COMMANDS
        assert described["result"]["name"] == "mcp_fixture.echo"

    @pytest.mark.asyncio
    async def test_env_server_url_fallback(self, cli_server, rest_server, monkeypatch):
        """``OPENBB_SERVER_URL`` is used when no ``server_url`` is given, and a single remote row is unwrapped."""
        url, recording = rest_server
        monkeypatch.setenv("OPENBB_SERVER_URL", url)
        recording.paths.clear()
        out = await _call(cli_server, "openbb_dispatch", command="mcp_fixture.echo")
        assert out["result"]["results"] == {"symbol": "AAPL", "index": 0}
        assert "/api/v1/mcp_fixture/echo" in recording.paths

    @pytest.mark.asyncio
    async def test_remote_spec_is_fetched_once_per_server(
        self, cli_server, rest_server
    ):
        """The remote OpenAPI document is fetched once and reused."""
        url, recording = rest_server
        recording.paths.clear()
        for _ in range(3):
            await _call(
                cli_server,
                "openbb_dispatch",
                command="mcp_fixture.echo",
                server_url=url,
            )
        assert recording.paths.count("/openapi.json") == 1
        assert recording.paths.count("/api/v1/mcp_fixture/echo") == 3
