"""Test WebSockets API Integration."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        (
            {
                "name": "test_fmp",
                "provider": "fmp",
                "symbol": "btcusd,dogeusd",
                "asset_type": "crypto",
                "auth_token": None,
                "results_file": None,
                "save_results": False,
                "table_name": "records",
                "limit": 10,
                "sleep_time": 0.25,
                "broadcast_host": "0.0.0.0",  # noqa: S104
                "broadcast_port": 6666,
                "start_broadcast": False,
                "connect_kwargs": None,
            }
        ),
        (
            {
                "name": "test_tiingo",
                "provider": "tiingo",
                "symbol": "btcusd,dogeusd",
                "asset_type": "crypto",
                "feed": "trade_and_quote",
                "auth_token": None,
                "results_file": None,
                "save_results": False,
                "table_name": "records",
                "limit": 10,
                "sleep_time": 0.25,
                "broadcast_host": "0.0.0.0",  # noqa: S104
                "broadcast_port": 6666,
                "start_broadcast": False,
                "connect_kwargs": None,
            }
        ),
        (
            {
                "name": "test_polygon",
                "provider": "polygon",
                "symbol": "btcusd,dogeusd",
                "asset_type": "crypto",
                "feed": "quote",
                "auth_token": None,
                "results_file": None,
                "save_results": False,
                "table_name": "records",
                "limit": 10,
                "sleep_time": 0.25,
                "broadcast_host": "0.0.0.0",  # noqa: S104
                "broadcast_port": 6666,
                "start_broadcast": False,
                "connect_kwargs": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_websockets_create_connection(params, headers):
    """Test the websockets_create_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/create_connection?{query_str}"

    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
    res = result.json()["results"]
    assert isinstance(res, dict)
    assert res.get("status", {}).get("is_running")
    assert not res.get("status", {}).get("is_broadcasting")


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_get_results(params, headers):
    """Test the websockets_get_results endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/get_results?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_clear_results(params, headers):
    """Test the websockets_clear_results endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/clear_results?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "symbol": "ethusd",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "symbol": "ethusd",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "symbol": "ethusd",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_subscribe(params, headers):
    """Test the websockets_subscribe endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/subscribe?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": 6666,
            "uvicorn_kwargs": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": 6667,
            "uvicorn_kwargs": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": 6668,
            "uvicorn_kwargs": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_start_broadcasting(params, headers):
    """Test the websockets_start_broadcasting endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/start_broadcasting?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
            "symbol": "ethusd",
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
            "symbol": "ethusd",
        },
        {
            "name": "test_polygon",
            "auth_token": None,
            "symbol": "ethusd",
        },
    ],
)
@pytest.mark.integration
def test_websockets_unsubscribe(params, headers):
    """Test the websockets_unsubscribe endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/unsubscribe?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_stop_connection(params, headers):
    """Test the websockets_stop_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/stop_connection?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_restart_connection(params, headers):
    """Test the websockets_restart_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/restart_connection?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_stop_broadcasting(params, headers):
    """Test the websockets_stop_broadcasting endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/stop_broadcasting?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_kill(params, headers):
    """Test the websockets_kill endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/websockets/kill?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
