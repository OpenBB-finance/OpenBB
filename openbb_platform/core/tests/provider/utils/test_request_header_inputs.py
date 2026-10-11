"""Verify caller-owned request headers through a real server."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from aiohttp import web

from openbb_core.provider.utils.client import ClientSession


@asynccontextmanager
async def serving(handler):
    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        assert isinstance(site._server, asyncio.Server)
        yield f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers", [None, {"user-agent": "custom-client"}, {"X-Custom": "preserved"}]
)
async def test_header_inputs_are_supported_without_mutation(headers):
    original = None if headers is None else headers.copy()

    async def handler(request):
        return web.json_response(
            {
                "agents": request.headers.getall("User-Agent", []),
                "custom": request.headers.get("X-Custom"),
            }
        )

    async with serving(handler) as url, ClientSession() as session:
        payload = await (await session.get(url, headers=headers)).json()
    assert headers == original
    assert len(payload["agents"]) == 1
    if headers and "user-agent" in headers:
        assert payload["agents"] == ["custom-client"]
    if headers and "X-Custom" in headers:
        assert payload["custom"] == "preserved"
