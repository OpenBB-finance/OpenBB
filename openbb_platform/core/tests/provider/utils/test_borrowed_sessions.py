"""Session ownership is observable with real local HTTP requests."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from aiohttp import web

from openbb_core.provider.utils import helpers
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
@pytest.mark.parametrize("batch", [False, True])
async def test_borrowed_session_is_reusable_without_allocation(monkeypatch, batch):
    async def unexpected_factory(**kwargs):
        raise AssertionError("borrowed session must not allocate a second session")

    monkeypatch.setattr(helpers, "get_async_requests_session", unexpected_factory)

    async def handler(request):
        return web.json_response({"value": 1})

    async with serving(handler) as url, ClientSession() as session:
        result = (
            await helpers.amake_requests([url], session=session)
            if batch
            else await helpers.amake_request(url, session=session)
        )
        assert result == [{"value": 1}] if batch else result == {"value": 1}
        assert not session.closed
        assert await (await session.get(url)).json() == {"value": 1}


@pytest.mark.asyncio
@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("explicit_none", [False, True])
async def test_owned_sessions_close_after_request(monkeypatch, batch, explicit_none):
    sessions = []

    async def factory(**kwargs):
        session = ClientSession()
        sessions.append(session)
        return session

    monkeypatch.setattr(helpers, "get_async_requests_session", factory)

    async def handler(request):
        return web.json_response({"value": 1})

    async with serving(handler) as url:
        if batch:
            await helpers.amake_requests(
                [url], **({"session": None} if explicit_none else {})
            )
        elif explicit_none:
            await helpers.amake_request(url, session=None)
        else:
            await helpers.amake_request(url)
    try:
        assert len(sessions) == 1
        assert sessions[0].closed
    finally:
        for session in sessions:
            await session.close()
