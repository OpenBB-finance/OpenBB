"""Test the provider helpers."""

import pytest
import requests
from openbb_core.provider.utils.helpers import (
    get_querystring,
    get_user_agent,
    make_request,
    to_snake_case,
)


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


def test_get_user_agent():
    """Test the get_user_agent helper."""
    user_agent = get_user_agent()
    assert "Mozilla/5.0" in user_agent


def test_make_request(monkeypatch):
    """Test the make_request helper."""

    class MockResponse:
        def __init__(self):
            self.status_code = 200

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
