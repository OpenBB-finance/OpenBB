"""Test WebSockets Python Integration."""

# pylint: disable=redefined-outer-name, inconsistent-return-statements, import-outside-toplevel

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject
from openbb_websockets.models import WebSocketConnectionStatus


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


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
        (
            {
                "name": "test_intrinio",
                "provider": "intrinio",
                "symbol": "spy,qqq,iwm,tsla,nvda",
                "asset_type": "stock",
                "feed": "realtime",
                "trades_only": True,
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
def test_websockets_create_connection(params, obb):
    """Test the websockets_create_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.create_connection(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None
    assert isinstance(result.results.status, WebSocketConnectionStatus)
    assert result.results.status.is_running is True
    assert result.results.status.is_broadcasting is False


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_get_results(params, obb):
    """Test the websockets_get_results endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.get_results(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
def test_websockets_clear_results(params, obb):
    """Test the websockets_clear_results endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.clear_results(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "symbol": "amzn",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_subscribe(params, obb):
    """Test the websockets_subscribe endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.subscribe(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": None,
            "uvicorn_kwargs": None,
        },
        {
            "name": "test_tiingo",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": None,
            "uvicorn_kwargs": None,
        },
        {
            "name": "test_polygon",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": None,
            "uvicorn_kwargs": None,
        },
        {
            "name": "test_intrinio",
            "auth_token": None,
            "host": "0.0.0.0",  # noqa: S104
            "port": None,
            "uvicorn_kwargs": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_start_broadcasting(params, obb):
    """Test the websockets_start_broadcasting endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.start_broadcasting(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "symbol": "amzn",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_unsubscribe(params, obb):
    """Test the websockets_unsubscribe endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.unsubscribe(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_get_client(params, obb):
    """Test the websockets_get_client endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.get_client(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        {
            "name": "test_fmp",
        },
        {
            "name": "test_tiingo",
        },
        {
            "name": "test_polygon",
        },
        {
            "name": "test_intrinio",
        },
    ],
)
@pytest.mark.integration
def test_websockets_get_client_status(params, obb):
    """Test the websockets_get_client endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.get_client_status(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_stop_connection(params, obb):
    """Test the websockets_stop_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.stop_connection(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_restart_connection(params, obb):
    """Test the websockets_restart_connection endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.restart_connection(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_stop_broadcasting(params, obb):
    """Test the websockets_stop_broadcasting endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.stop_broadcasting(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


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
        {
            "name": "test_intrinio",
            "auth_token": None,
        },
    ],
)
@pytest.mark.integration
def test_websockets_kill(params, obb):
    """Test the websockets_kill endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.websockets.kill(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None
