"""Test the provider helpers."""

import pytest
import requests
from openbb_core.provider.utils.client import ClientSession
from openbb_core.provider.utils.helpers import (
    amake_request,
    amake_requests,
    get_querystring,
    make_request,
    to_snake_case,
)


class MockResponse:
    def __init__(self):
        self.status_code = 200
        self.status = 200

    async def json(self):
        return {"test": "test"}


class MockSession:
    def __init__(self):
        self.response = MockResponse()

    async def request(self, *args, **kwargs):
        if kwargs.get("raise_for_status", False):
            raise Exception("Test")

        return self.response

    @staticmethod
    async def mock_callback(response, session):
        """Mock the response_callback."""
        assert response.status == 200
        return await response.json()


def test_get_querystring_exclude():
    """Test the get_querystring helper."""
    items = {
        "key1": "value1",
        "key2": "value2",
        "key3": None,
        "key4": ["value3", "value4"],
    }
    exclude = ["key2"]

    querystring = get_querystring(items, exclude)
    assert querystring == "key1=value1&key4=value3&key4=value4"


def test_get_querystring_no_exclude():
    """Test the get_querystring helper with no exclude list."""
    items = {
        "key1": "value1",
        "key2": "value2",
        "key3": None,
        "key4": ["value3", "value4"],
    }

    querystring = get_querystring(items, [])
    assert querystring == "key1=value1&key2=value2&key4=value3&key4=value4"


def test_make_request(monkeypatch):
    """Test the make_request helper."""

    def mock_get(*args, **kwargs):
        """Mock the requests.get method."""
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    response = make_request("http://mock.url")
    assert response.status_code == 200

    with pytest.raises(ValueError):
        make_request("http://mock.url", method="PUT")


def test_to_snake_case():
    """Test the to_snake_case helper."""
    assert to_snake_case("SomeRandomString") == "some_random_string"
    assert to_snake_case("someRandomString") == "some_random_string"
    assert to_snake_case("already_snake_case") == "already_snake_case"


@pytest.mark.asyncio
async def test_amake_request(monkeypatch):
    """Test the amake_request helper."""

    mock_callback = MockSession.mock_callback

    client_session = MockSession()
    monkeypatch.setattr(ClientSession, "request", client_session.request)

    response = await amake_request("http://mock.url", response_callback=mock_callback)
    assert response == {"test": "test"}

    with pytest.raises(Exception):
        await amake_request(
            "http://mock.url",
            response_callback=mock_callback,
            raise_for_status=True,
        )

    with pytest.raises(ValueError):
        await amake_request("http://mock.url", method="PUT")


@pytest.mark.asyncio
async def test_amake_requests(monkeypatch):
    """Test the amake_requests helper."""

    mock_callback = MockSession.mock_callback

    client_session = MockSession()
    monkeypatch.setattr(ClientSession, "request", client_session.request)

    multi_response = await amake_requests(
        ["http://mock.url", "http://mock.url"],
        response_callback=mock_callback,
    )
    assert multi_response == [{"test": "test"}, {"test": "test"}]

    with pytest.raises(ValueError):
        await amake_requests(
            ["http://mock.url", "http://mock.url"], method="PUT", raise_for_status=True
        )
