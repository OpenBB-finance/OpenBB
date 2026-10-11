"""Verify decompression against actual HTTP response bodies."""

import asyncio
import gzip
import zlib
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
    "encoding,body",
    [
        ("deflate", zlib.compress(b'{"value":42}')),
        ("deflate", zlib.compress(b'{"value":42}')[2:-4]),
        ("gzip", gzip.compress(b'{"value":42}')),
    ],
)
async def test_native_compressed_json_response(encoding, body):
    async def handler(request):
        return web.Response(
            body=body,
            content_type="application/json",
            headers={"Content-Encoding": encoding},
        )

    async with serving(handler) as url, ClientSession() as session:
        assert await (await session.get(url)).json() == {"value": 42}
