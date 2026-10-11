"""Native HTTP SSE adaptation must preserve event boundaries."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from aiohttp import web

from openbb_cli.dispatchers.http import _HttpSSESource


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
async def test_remote_event_separators_and_multiline_data_survive():
    events = ": heartbeat\n\nid: 1\ndata: first\ndata: second\n\nevent: update\ndata: next\n\n"

    async def handler(request):
        return web.Response(
            text=events,
            content_type="text/event-stream",
            headers={"X-OpenBB-Provider": "fixture"},
        )

    async with serving(handler) as url:
        source = _HttpSSESource(url, {}, {})
        actual = "".join([chunk async for chunk in source.body_iterator])
    assert actual == events
    assert source.provider == "fixture"
