"""Tests for ``openbb_mcp_server.app.auth``."""

import base64

import httpx
import pytest
from fastapi import FastAPI
from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.app.auth import TokenAuthProvider, get_auth_provider
from openbb_mcp_server.models.settings import MCPSettings

INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "0"},
    },
}
MCP_HEADERS = {"Accept": "application/json, text/event-stream"}


def _token(credentials: str) -> str:
    return base64.b64encode(credentials.encode("utf-8")).decode("ascii")


def _serve_mcp(serve, auth):
    settings = MCPSettings(default_skills_dir=None)
    server = create_mcp_server(settings, FastAPI(), auth=auth)
    return serve(server.http_app(path="/mcp"))


class TestTokenAuthProvider:
    """Verifying ``base64(username:password)`` Bearer tokens."""

    @pytest.mark.asyncio
    async def test_valid_credentials(self):
        """Matching credentials yield an access token for the username."""
        provider = TokenAuthProvider(("testuser", "p:ss"))
        token = _token("testuser:p:ss")
        access = await provider.verify_token(token)
        assert access is not None
        assert (access.token, access.client_id, access.scopes) == (
            token,
            "testuser",
            [],
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "token",
        [
            _token("wronguser:testpass"),
            _token("testuser:wrongpass"),
            _token("testuser"),
            "not%base64$",
            "ünïcode",
        ],
        ids=["wrong-user", "wrong-password", "no-separator", "bad-base64", "non-ascii"],
    )
    async def test_rejected_tokens(self, token):
        """Wrong, malformed, or undecodable tokens are rejected."""
        provider = TokenAuthProvider(("testuser", "testpass"))
        assert await provider.verify_token(token) is None


class TestGetAuthProvider:
    """Normalizing the ``auth`` argument of ``create_mcp_server``."""

    def test_none_disables_auth(self):
        """``None`` means no authentication."""
        assert get_auth_provider(None) is None

    def test_auth_provider_passes_through(self):
        """A FastMCP auth provider is used unchanged."""
        verifier = StaticTokenVerifier(tokens={"secret": {"client_id": "c"}})
        assert get_auth_provider(verifier) is verifier

    @pytest.mark.asyncio
    @pytest.mark.parametrize("credentials", [("user", "pass"), ["user", "pass"]])
    async def test_credential_pair_builds_token_provider(self, credentials):
        """A ``(username, password)`` tuple or list builds a token provider for it."""
        provider = get_auth_provider(credentials)
        assert isinstance(provider, TokenAuthProvider)
        assert await provider.verify_token(_token("user:pass")) is not None

    @pytest.mark.parametrize(
        "auth",
        [("user",), ("user", "pass", "extra"), ("user", ""), ("user", 1), "user:pass"],
    )
    def test_invalid_auth_raises(self, auth):
        """Anything else is rejected."""
        with pytest.raises(TypeError, match="auth must be a fastmcp AuthProvider"):
            get_auth_provider(auth)


class TestServerAuthentication:
    """The HTTP transport enforcing the configured auth."""

    @pytest.mark.asyncio
    async def test_credentials_are_enforced(self, serve):
        """Requests need a Bearer token carrying the configured credentials."""
        with _serve_mcp(serve, ("user", "pass")) as url:
            async with httpx.AsyncClient(base_url=url, headers=MCP_HEADERS) as http:
                anonymous = await http.post("/mcp", json=INITIALIZE)
                wrong = await http.post(
                    "/mcp",
                    json=INITIALIZE,
                    headers={"Authorization": f"Bearer {_token('user:nope')}"},
                )
            async with Client(f"{url}/mcp", auth=BearerAuth(_token("user:pass"))) as c:
                tools = {tool.name for tool in await c.list_tools()}
        assert anonymous.status_code == 401
        assert wrong.status_code == 401
        assert "install_skill" in tools

    @pytest.mark.asyncio
    async def test_custom_auth_provider_is_enforced(self, serve):
        """A custom FastMCP auth provider guards the server."""
        verifier = StaticTokenVerifier(tokens={"secret": {"client_id": "c"}})
        with _serve_mcp(serve, verifier) as url:
            async with httpx.AsyncClient(base_url=url, headers=MCP_HEADERS) as http:
                basic = await http.post(
                    "/mcp",
                    json=INITIALIZE,
                    headers={"Authorization": f"Bearer {_token('user:pass')}"},
                )
            async with Client(f"{url}/mcp", auth=BearerAuth("secret")) as client:
                tools = {tool.name for tool in await client.list_tools()}
        assert basic.status_code == 401
        assert "install_skill" in tools

    @pytest.mark.asyncio
    async def test_no_auth_serves_anonymous_requests(self, serve):
        """Without auth, anonymous requests are served."""
        with _serve_mcp(serve, None) as url:
            async with Client(f"{url}/mcp") as client:
                tools = {tool.name for tool in await client.list_tools()}
        assert "install_skill" in tools
