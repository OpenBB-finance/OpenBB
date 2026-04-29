"""Tests targeting the real ClientSession.request method (lines 111-137)."""

import asyncio
import gzip
import zlib
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from openbb_core.provider.utils import client


def _fake_response(headers=None, body=b"", status=200):
    resp = MagicMock(spec=aiohttp.ClientResponse)
    resp.headers = headers or {}
    resp.status = status
    resp._body = body
    resp.read = AsyncMock(return_value=body)
    resp.raise_for_status = MagicMock()
    return resp


@pytest.mark.asyncio
async def test_request_sets_default_headers_and_user_agent():
    session = client.ClientSession()
    fake = _fake_response()
    captured = {}

    async def fake_super_request(self, *args, **kwargs):
        captured["args"] = args
        captured["headers"] = kwargs["headers"]
        return fake

    with patch.object(aiohttp.ClientSession, "request", fake_super_request):
        await session.request("GET", "http://x")
    await session.close()

    assert captured["headers"]["Accept"] == "application/json"
    assert captured["headers"]["Accept-Encoding"] == "gzip, deflate"
    assert "User-Agent" in captured["headers"]
    assert "Mozilla" in captured["headers"]["User-Agent"]


@pytest.mark.asyncio
async def test_request_preserves_user_agent_when_provided():
    session = client.ClientSession()
    fake = _fake_response()
    captured = {}

    async def fake_super_request(self, *args, **kwargs):
        captured["headers"] = kwargs["headers"]
        return fake

    with patch.object(aiohttp.ClientSession, "request", fake_super_request):
        await session.request("GET", "http://x", headers={"User-Agent": "custom/1.0"})
    await session.close()

    assert captured["headers"]["User-Agent"] == "custom/1.0"


@pytest.mark.asyncio
async def test_request_raise_for_status_propagates():
    session = client.ClientSession()
    fake = _fake_response()
    fake.raise_for_status.side_effect = RuntimeError("boom")

    async def fake_super_request(self, *args, **kwargs):
        return fake

    with (
        patch.object(aiohttp.ClientSession, "request", fake_super_request),
        pytest.raises(RuntimeError, match="boom"),
    ):
        await session.request("GET", "http://x", raise_for_status=True)
    await session.close()


@pytest.mark.asyncio
async def test_request_gzip_decompression():
    session = client.ClientSession()
    payload = b'{"k":"v"}'
    body = gzip.compress(payload)
    fake = _fake_response(headers={"Content-Encoding": "gzip"}, body=body)

    async def fake_super_request(self, *args, **kwargs):
        return fake

    with patch.object(aiohttp.ClientSession, "request", fake_super_request):
        resp = await session.request("GET", "http://x")
    await session.close()

    assert resp._body == payload


@pytest.mark.asyncio
async def test_request_deflate_decompression():
    session = client.ClientSession()
    payload = b'{"k":"v"}'
    body = zlib.compress(payload)[2:-4]  # raw deflate (no zlib header/trailer)
    fake = _fake_response(headers={"Content-Encoding": "deflate"}, body=body)

    async def fake_super_request(self, *args, **kwargs):
        return fake

    with patch.object(aiohttp.ClientSession, "request", fake_super_request):
        resp = await session.request("GET", "http://x")
    await session.close()

    assert resp._body == payload


@pytest.mark.asyncio
async def test_request_no_decompression_when_auto_decompress():
    session = client.ClientSession(auto_decompress=True)
    body = gzip.compress(b'{"k":"v"}')
    fake = _fake_response(headers={"Content-Encoding": "gzip"}, body=body)

    async def fake_super_request(self, *args, **kwargs):
        return fake

    with patch.object(aiohttp.ClientSession, "request", fake_super_request):
        resp = await session.request("GET", "http://x")
    await session.close()

    # Body unchanged (still compressed) since auto_decompress=True bypassed our path.
    assert resp._body == body


def test_client_response_init_sets_obfuscated_request_info():
    """Trigger ClientResponse.__init__ override (lines 44-45)."""
    url = URL("http://x?api_key=secret&symbol=AAPL")
    request_info = aiohttp.RequestInfo(
        url=url,
        method="GET",
        headers=CIMultiDictProxy(CIMultiDict({"Authorization": "Bearer xyz"})),
        real_url=url,
    )
    # Call obfuscation directly — verifies behavior covered by line 44-45 path.
    obf = client.ClientResponse.obfuscate_request_info(request_info)
    assert "********" in str(obf.url)
    assert obf.headers["Authorization"] == "********"


def test_client_response_init_obfuscates_before_super(monkeypatch):
    url = URL("http://x?api_key=secret")
    request_info = aiohttp.RequestInfo(
        url=url,
        method="GET",
        headers=CIMultiDictProxy(CIMultiDict({"Authorization": "Bearer xyz"})),
        real_url=url,
    )
    captured = {}

    def _fake_super_init(self, *args, **kwargs):
        captured["request_info"] = kwargs["request_info"]

    monkeypatch.setattr(aiohttp.ClientResponse, "__init__", _fake_super_init)
    client.ClientResponse(
        "GET",
        URL("http://x"),
        request_info=request_info,
        writer=None,
        continue100=None,
        timer=None,
        traces=[],
        loop=None,
        session=None,
    )

    assert "********" in str(captured["request_info"].url)


def test_client_session_del_schedules_close(monkeypatch):
    calls = {"count": 0}

    class _Session(client.ClientSession):
        def __init__(self):
            pass

        @property
        def closed(self):
            return False

        async def close(self):
            return None

    def _create_task(coro):
        calls["count"] += 1
        coro.close()

    monkeypatch.setattr(asyncio, "create_task", _create_task)
    _Session().__del__()
    assert calls["count"] >= 1


@pytest.mark.asyncio
async def test_client_response_json_calls_super():
    """Cover ClientResponse.json (line 60)."""

    async def fake_super_json(self, **kw):
        return {"ok": True}

    class Sub(client.ClientResponse):
        def __init__(self):  # bypass real init
            pass

    with patch.object(aiohttp.ClientResponse, "json", fake_super_json):
        result = await Sub().json()
    assert result == {"ok": True}
