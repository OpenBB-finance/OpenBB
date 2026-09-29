"""Test the client helper."""

import asyncio
import gzip
import json
import zlib
from unittest.mock import patch

import aiohttp
import pytest
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from openbb_core.provider.utils import client


def test_obfuscate():
    """Test the obfuscate helper."""
    params = CIMultiDict(
        {
            "api_key": "1234",
            "token": "1234",
            "auth": "1234",
            "auth_token": "1234",
            "c": "1234",
            "api_key2": "1234",
        }
    )

    assert client.obfuscate(params) == {
        "api_key": "********",
        "token": "********",
        "auth": "********",
        "auth_token": "********",
        "c": "********",
        "api_key2": "********",
    }


def test_get_user_agent():
    """Test the get_user_agent helper."""
    user_agent = client.get_user_agent()
    assert "Mozilla/5.0" in user_agent


class MockResponse:
    """Mock response class."""

    def __init__(self, method, url, **kwargs):
        """Initialize."""
        self.url = URL(url)
        self.method = method
        self.body = kwargs.get("body", {"test": "test"})
        self.status = kwargs.get("status", 200)
        self.headers = kwargs.get("headers", {})

        request_info = aiohttp.RequestInfo(
            url=self.url,
            method=method,
            headers=CIMultiDictProxy(CIMultiDict(self.headers)),
            real_url=self.url,
        )
        self.request_info = client.ClientResponse.obfuscate_request_info(request_info)

    async def json(self, **_):
        """Return the json response."""
        return self.body

    async def read(self):
        """Return the response body."""
        return self.body

    def raise_for_status(self):
        """Raise an exception."""
        raise Exception("Test")


class MockClientSession(client.ClientSession):
    """Mock ClientSession."""

    def __del__(self):  # type: ignore
        """Delete the session."""

    async def request(
        self, *args, raise_for_status: bool = False, **kwargs
    ) -> client.ClientResponse:
        """Mock the request method."""
        response = MockResponse(*args, **kwargs)

        if raise_for_status:
            response.raise_for_status()

        encoding = response.headers.get("Content-Encoding", "")
        if encoding in ("gzip", "deflate") and not self.auto_decompress:
            response_body = await response.read()
            wbits = 16 + zlib.MAX_WBITS if encoding == "gzip" else -zlib.MAX_WBITS
            response.body = json.loads(
                zlib.decompress(response_body, wbits).decode("utf-8")
            )

        return response  # type: ignore


class _BaseResponseMock:
    def __init__(self, *, body: bytes = b"{}", encoding: str = ""):
        self.headers = {"Content-Encoding": encoding} if encoding else {}
        self._raw = body
        self._body = None
        self.status_raised = False

    async def read(self):
        return self._raw

    def raise_for_status(self):
        self.status_raised = True
        raise RuntimeError("raised")


@pytest.mark.parametrize(
    "url_params, obfuscated_params",
    [
        (
            "?api_key=1234&token=1234",
            "?api_key=********&token=********",
        ),
        (
            "?symbol=TSLA&api_key=1234",
            "?symbol=TSLA&api_key=********",
        ),
        (
            "?auth_token=1234&c=1234",
            "?auth_token=********&c=********",
        ),
        (
            "?auth=1234&c=1234",
            "?auth=********&c=********",
        ),
        (
            "?api_key2=1234&cc=1234&some_token=1234",
            "?api_key2=********&cc=1234&some_token=********",
        ),
    ],
)
@pytest.mark.asyncio
async def test_client_response_obfuscate_request_info(url_params, obfuscated_params):
    """Test the ClientSession post helper."""
    headers = {"Authorization": "Bearer 1234"}

    response = await MockClientSession().get(
        f"http://mock.url{url_params}", headers=headers
    )

    assert isinstance(response, MockResponse)
    assert response.request_info.url == URL(f"http://mock.url{obfuscated_params}")

    assert response.request_info.headers == CIMultiDictProxy(
        CIMultiDict({"Authorization": "********"})
    )


@pytest.mark.asyncio
async def test_client_get():
    """Test the ClientSession get helper."""
    response = await MockClientSession().get("http://mock.url")
    assert isinstance(response, MockResponse)
    assert response.method == "GET"
    assert response.status == 200
    assert response.body == {"test": "test"}
    assert response.request_info.url == URL("http://mock.url")


@pytest.mark.asyncio
async def test_client_post():
    """Test the ClientSession post helper."""

    response = await MockClientSession().post("http://mock.url")
    assert isinstance(response, MockResponse)
    assert response.method == "POST"
    assert response.status == 200
    assert response.body == {"test": "test"}
    assert response.request_info.url == URL("http://mock.url")


@pytest.mark.parametrize(
    "body, expected",
    [
        ([{"test": "test"}, {"test": "test"}], {"test": "test"}),
        ({"test": "test"}, {"test": "test"}),
    ],
)
@pytest.mark.asyncio
async def test_client_get_one(body, expected):
    """Test the ClientSession get_one helper."""

    response = await MockClientSession().get_one("http://mock.url", body=body)

    assert isinstance(response, dict)
    assert response == expected


@pytest.mark.asyncio
async def test_client_get_json():
    """Test the ClientSession get_json helper."""

    response = await MockClientSession().get_json("http://mock.url")

    assert isinstance(response, dict)
    assert response == {"test": "test"}


@pytest.mark.asyncio
async def test_client_content_encoding():
    """Test the ClientSession encode helper."""
    json_data = json.dumps({"test": "test"}, indent=2)

    response = await MockClientSession().get_json(
        "http://mock.url",
        body=gzip.compress(json_data.encode("utf-8")),
        headers={"Content-Encoding": "gzip"},
    )

    assert isinstance(response, dict)
    assert response == {"test": "test"}


def test_client_response_obfuscate_request_info_direct_call():
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


@pytest.mark.asyncio
async def test_client_request_sets_default_headers_and_user_agent(monkeypatch):
    seen = {}

    async def _fake_super_request(self, *args, **kwargs):
        seen["headers"] = kwargs.get("headers", {})
        return _BaseResponseMock()

    monkeypatch.setattr(aiohttp.ClientSession, "request", _fake_super_request)

    session = client.ClientSession()
    try:
        await session.request("GET", "http://mock.url")
    finally:
        await session.close()

    assert "Accept" in seen["headers"]
    assert "User-Agent" in seen["headers"]


@pytest.mark.asyncio
async def test_client_request_respects_existing_user_agent(monkeypatch):
    seen = {}

    async def _fake_super_request(self, *args, **kwargs):
        seen["headers"] = kwargs.get("headers", {})
        return _BaseResponseMock()

    monkeypatch.setattr(aiohttp.ClientSession, "request", _fake_super_request)

    session = client.ClientSession()
    try:
        await session.request(
            "GET", "http://mock.url", headers={"User-Agent": "custom-ua"}
        )
    finally:
        await session.close()

    assert seen["headers"]["User-Agent"] == "custom-ua"


@pytest.mark.asyncio
async def test_client_request_raise_for_status_branch(monkeypatch):
    async def _fake_super_request(self, *args, **kwargs):
        return _BaseResponseMock()

    monkeypatch.setattr(aiohttp.ClientSession, "request", _fake_super_request)

    session = client.ClientSession()
    try:
        with pytest.raises(RuntimeError, match="raised"):
            await session.request("GET", "http://mock.url", raise_for_status=True)
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_client_request_gzip_decompress_branch(monkeypatch):
    payload = b'{"ok": true}'
    compressed = gzip.compress(payload)

    async def _fake_super_request(self, *args, **kwargs):
        return _BaseResponseMock(body=compressed, encoding="gzip")

    monkeypatch.setattr(aiohttp.ClientSession, "request", _fake_super_request)

    session = client.ClientSession(auto_decompress=False)
    try:
        response = await session.request("GET", "http://mock.url")
    finally:
        await session.close()

    assert response._body == payload


@pytest.mark.asyncio
async def test_client_request_deflate_decompress_branch(monkeypatch):
    payload = b'{"ok": true}'
    compressed = zlib.compress(payload)[2:-4]

    async def _fake_super_request(self, *args, **kwargs):
        return _BaseResponseMock(body=compressed, encoding="deflate")

    monkeypatch.setattr(aiohttp.ClientSession, "request", _fake_super_request)

    session = client.ClientSession(auto_decompress=False)
    try:
        response = await session.request("GET", "http://mock.url")
    finally:
        await session.close()

    assert response._body == payload
