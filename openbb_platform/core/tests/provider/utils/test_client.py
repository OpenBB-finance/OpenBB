import gzip
import json
import zlib

import aiohttp
import pytest
from multidict import CIMultiDict, CIMultiDictProxy
from openbb_core.provider.utils import client
from yarl import URL


def test_obfuscate():
    """Test the obfuscate helper."""
    params = {
        "api_key": "1234",
        "token": "1234",
        "auth": "1234",
        "auth_token": "1234",
        "c": "1234",
        "api_key2": "1234",
    }

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

    # pylint: disable=unused-argument,signature-differs
    def __del__(self):  # type: ignore
        """Delete the session."""

    async def request(  # type: ignore
        self, *args, raise_for_status: bool = False, **kwargs
    ) -> client.ClientResponse:
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
