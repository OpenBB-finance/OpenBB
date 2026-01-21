"""End-to-end deploy mode tests with real Redis and real HTTP server.

These tests:
1. Start a real Redis container via testcontainers
2. Configure deploy mode with Redis backend
3. Start the real FastAPI server
4. Register widgets in Redis via the widget store
5. Make real HTTP requests to verify content is served from Redis
6. Test WebSocket authentication with real connections
"""

# pylint: disable=redefined-outer-name,unused-argument

from __future__ import annotations

import asyncio
import json
import os
import socket
import time
import urllib.error
import urllib.request
import uuid

import pytest
import pytest_asyncio


try:
    import websockets

    from websockets.exceptions import InvalidStatusCode
except ImportError:
    websockets = None
    InvalidStatusCode = None

from pywry.config import clear_settings
from pywry.inline import HAS_FASTAPI, _start_server, _state, stop_server
from pywry.state._factory import clear_state_caches


# Skip if FastAPI not installed
pytestmark = [
    pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed"),
    pytest.mark.redis,
    pytest.mark.container,
]


# --- Helper Functions ---


def get_free_port() -> int:
    """Get a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((host, port))
                if result == 0:
                    return True
        except OSError:
            pass
        time.sleep(0.1)
    return False


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    """Make HTTP GET request, return (status_code, body)."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must use http or https scheme")
    req = urllib.request.Request(url)  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


# --- Fixtures ---


@pytest.fixture(scope="session")
def unique_prefix() -> str:
    """Generate a unique prefix for the entire test session.

    Session-scoped so ALL tests use the SAME Redis prefix.
    """
    return f"pywry-e2e-test:{uuid.uuid4().hex[:8]}:"


@pytest.fixture(scope="session")
def server_port() -> int:
    """Use a fixed port for predictable testing."""
    return 8899  # Fixed port for E2E tests


@pytest.fixture(scope="session")
def deploy_mode_env(redis_container: str, unique_prefix: str, server_port: int):
    """
    Set up REAL deploy mode with Redis for the entire test session.

    Session-scoped: Sets up once, used by all tests.
    Same Redis, same prefix, same server port.
    """
    # Clear caches BEFORE setting new environment
    clear_settings()
    clear_state_caches()

    # Clear _state internal caches
    _state._widget_store = None
    _state._connection_router = None
    _state._callback_registry = None

    print("\n=== DEPLOY MODE ENV SETUP (SESSION) ===")
    print(f"Redis container URL: {redis_container}")
    print(f"Prefix: {unique_prefix}")
    print(f"Server port: {server_port}")

    # Save original environment
    env_backup = {}
    env_keys = [
        "PYWRY_DEPLOY_MODE",
        "PYWRY_DEPLOY__STATE_BACKEND",
        "PYWRY_DEPLOY__REDIS_URL",
        "PYWRY_DEPLOY__REDIS_PREFIX",
        "PYWRY_SERVER__PORT",
        "PYWRY_SERVER__HOST",
    ]
    for key in env_keys:
        env_backup[key] = os.environ.get(key)

    # Set deploy mode environment
    os.environ["PYWRY_DEPLOY_MODE"] = "1"
    os.environ["PYWRY_DEPLOY__STATE_BACKEND"] = "redis"
    os.environ["PYWRY_DEPLOY__REDIS_URL"] = redis_container
    os.environ["PYWRY_DEPLOY__REDIS_PREFIX"] = unique_prefix
    os.environ["PYWRY_SERVER__PORT"] = str(server_port)
    os.environ["PYWRY_SERVER__HOST"] = "0.0.0.0"

    # Clear ALL caches to pick up new settings
    clear_settings()
    clear_state_caches()
    _state._widget_store = None
    _state._connection_router = None
    _state._callback_registry = None

    # Verify the configuration was applied
    from pywry.state._factory import get_state_backend, is_deploy_mode

    print(f"is_deploy_mode(): {is_deploy_mode()}")
    print(f"get_state_backend(): {get_state_backend()}")

    yield {
        "redis_url": redis_container,
        "prefix": unique_prefix,
        "port": server_port,
    }

    # Cleanup at end of session
    stop_server()
    _state.widgets.clear()
    _state.local_widgets.clear()
    _state.connections.clear()
    _state.widget_tokens.clear()
    _state._widget_store = None
    _state._connection_router = None
    _state._callback_registry = None

    # Restore environment
    for key, value in env_backup.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    clear_settings()
    clear_state_caches()


@pytest_asyncio.fixture
async def redis_widget_store(deploy_mode_env):
    """Get the widget store that the server uses.

    Depends on deploy_mode_env to ensure environment is set up first.
    Does NOT clean up keys between tests - session uses same Redis.

    Yields a dict with:
    - store: The RedisWidgetStore instance
    - config: The deploy_mode_env config (redis_url, prefix, port)
    """
    from pywry.state import get_widget_store
    from pywry.state.redis import RedisWidgetStore

    # Get the store that the server will use
    store = get_widget_store()
    print("\n=== WIDGET STORE INFO ===")
    print(f"Store type: {type(store).__name__}")
    print(f"Is RedisWidgetStore: {isinstance(store, RedisWidgetStore)}")
    if isinstance(store, RedisWidgetStore):
        print(f"Redis URL: {store._redis_url}")
        print(f"Prefix: {store._prefix}")

    # Verify Redis connection by pinging
    import redis.asyncio as aioredis

    redis_url = deploy_mode_env["redis_url"]
    client = aioredis.from_url(redis_url, decode_responses=True)
    try:
        pong = await client.ping()
        print(f"Redis PING response: {pong}")
    finally:
        await client.aclose()

    yield {"store": store, "config": deploy_mode_env}


# ============================================================================
# PART 1: Verify Deploy Mode is Active
# ============================================================================


class TestDeployModeConfiguration:
    """Verify deploy mode is properly configured."""

    def test_deploy_mode_is_active(self, deploy_mode_env) -> None:
        """Deploy mode should be active after env setup."""
        from pywry.state._factory import is_deploy_mode

        assert is_deploy_mode() is True

    def test_redis_backend_is_selected(self, deploy_mode_env) -> None:
        """Redis backend should be selected."""
        from pywry.state._factory import get_state_backend

        backend = get_state_backend()
        assert str(backend) == "StateBackend.REDIS"

    def test_widget_store_is_redis(self, deploy_mode_env) -> None:
        """Widget store should be RedisWidgetStore."""
        from pywry.state import get_widget_store
        from pywry.state.redis import RedisWidgetStore

        store = get_widget_store()
        assert isinstance(store, RedisWidgetStore)


# ============================================================================
# PART 2: Widget Registration in Redis
# ============================================================================


class TestWidgetRegistrationInRedis:
    """Test that widgets are properly stored in Redis."""

    @pytest.mark.asyncio
    async def test_register_widget_in_redis(self, redis_widget_store) -> None:
        """Widget should be stored in Redis."""
        store = redis_widget_store["store"]
        widget_id = f"test-widget-{uuid.uuid4().hex[:8]}"
        html = "<div>Hello from Redis!</div>"
        token = f"token-{uuid.uuid4().hex[:16]}"

        await store.register(widget_id, html, token=token)

        # Verify it exists
        exists = await store.exists(widget_id)
        assert exists

        # Verify HTML
        stored_html = await store.get_html(widget_id)
        assert stored_html == html

        # Verify token
        stored_token = await store.get_token(widget_id)
        assert stored_token == token

    @pytest.mark.asyncio
    async def test_redis_keys_created(self, redis_widget_store) -> None:
        """Verify actual Redis keys are created."""
        import redis.asyncio as aioredis

        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        widget_id = f"test-widget-{uuid.uuid4().hex[:8]}"
        await store.register(widget_id, "<p>Test</p>", token="tok123")

        # Check Redis directly
        client = aioredis.from_url(config["redis_url"], decode_responses=True)
        try:
            keys = [key async for key in client.scan_iter(f"{config['prefix']}*")]

            assert len(keys) > 0, f"No keys found with prefix {config['prefix']}"

            # Should have widget hash and active set
            key_str = " ".join(keys)
            assert "widget" in key_str.lower() or widget_id in key_str
        finally:
            await client.aclose()


# ============================================================================
# PART 3: Server Serves Widgets from Redis
# ============================================================================


class TestServerServesFromRedis:
    """Test that the FastAPI server serves widgets from Redis in deploy mode."""

    @pytest.mark.asyncio
    async def test_server_fetches_widget_from_redis(self, redis_widget_store) -> None:
        """Server should serve widget HTML from Redis."""
        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        widget_id = f"http-test-{uuid.uuid4().hex[:8]}"
        html_content = f"<h1>Widget {widget_id} from Redis</h1>"

        # Register widget directly in Redis
        await store.register(widget_id, html_content)

        # Start server
        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port), "Server did not start"

        # Fetch widget via HTTP
        status, body = http_get(f"http://127.0.0.1:{port}/widget/{widget_id}")

        assert status == 200, f"Expected 200, got {status}"
        assert f"Widget {widget_id} from Redis" in body

    @pytest.mark.asyncio
    async def test_server_returns_404_for_missing_widget(self, redis_widget_store) -> None:
        """Server should return 404 for non-existent widget."""
        config = redis_widget_store["config"]
        port = config["port"]

        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        status, _ = http_get(f"http://127.0.0.1:{port}/widget/nonexistent-widget")
        assert status == 404

    @pytest.mark.asyncio
    async def test_multiple_widgets_from_redis(self, redis_widget_store) -> None:
        """Multiple widgets should be served correctly from Redis."""
        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]

        widgets = {}
        for i in range(5):
            wid = f"multi-widget-{i}-{uuid.uuid4().hex[:6]}"
            html = f"<div>Widget number {i}</div>"
            await store.register(wid, html)
            widgets[wid] = html

        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        for wid in widgets:
            status, body = http_get(f"http://127.0.0.1:{port}/widget/{wid}")
            assert status == 200
            assert "Widget number" in body


# ============================================================================
# PART 4: Real Plotly Content from Redis
# ============================================================================


class TestPlotlyContentFromRedis:
    """Test real Plotly HTML content served from Redis."""

    @pytest.mark.asyncio
    async def test_plotly_html_served_from_redis(self, redis_widget_store) -> None:
        """Plotly HTML should be served from Redis."""
        import plotly.graph_objects as go

        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        widget_id = f"plotly-widget-{uuid.uuid4().hex[:8]}"

        # Create real Plotly figure
        fig = go.Figure(
            data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode="lines+markers")],
            layout=go.Layout(title="E2E Plotly from Redis"),
        )

        # Generate HTML from Plotly
        plotly_html = fig.to_html(include_plotlyjs="cdn", full_html=True)

        # Store in Redis
        await store.register(widget_id, plotly_html)

        # Start server and fetch
        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        status, body = http_get(f"http://127.0.0.1:{port}/widget/{widget_id}")

        assert status == 200
        assert "E2E Plotly from Redis" in body
        assert "plotly" in body.lower()


# ============================================================================
# PART 5: Real DataFrame/Table Content from Redis
# ============================================================================


class TestDataFrameContentFromRedis:
    """Test real DataFrame HTML content served from Redis."""

    @pytest.mark.asyncio
    async def test_dataframe_html_served_from_redis(self, redis_widget_store) -> None:
        """DataFrame HTML should be served from Redis."""
        import pandas as pd

        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        widget_id = f"dataframe-widget-{uuid.uuid4().hex[:8]}"

        # Create real DataFrame
        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Age": [30, 25, 35],
                "City": ["NYC", "LA", "Chicago"],
            }
        )

        # Generate HTML from DataFrame
        df_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>DataFrame Test</title></head>
        <body>
            <h1>DataFrame from Redis</h1>
            {df.to_html(classes="dataframe", index=False)}
        </body>
        </html>
        """

        # Store in Redis
        await store.register(widget_id, df_html)

        # Start server and fetch
        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        status, body = http_get(f"http://127.0.0.1:{port}/widget/{widget_id}")

        assert status == 200
        assert "DataFrame from Redis" in body
        assert "Alice" in body
        assert "Bob" in body
        assert "Charlie" in body


# ============================================================================
# PART 6: WebSocket Authentication with Tokens from Redis
# ============================================================================


@pytest.mark.skipif(websockets is None, reason="websockets not installed")
class TestWebSocketAuthFromRedis:
    """Test WebSocket authentication using tokens stored in Redis."""

    @pytest.mark.asyncio
    async def test_websocket_connects_with_redis_token(self, redis_widget_store) -> None:
        """WebSocket should connect with token from Redis."""
        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        widget_id = f"ws-widget-{uuid.uuid4().hex[:8]}"
        token = f"ws-token-{uuid.uuid4().hex[:16]}"

        # Register widget with token in Redis
        await store.register(widget_id, "<div>WS Test</div>", token=token)

        # Also need to set token in _state for WebSocket validation
        _state.widget_tokens[widget_id] = token

        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        ws_url = f"ws://127.0.0.1:{port}/ws/{widget_id}"
        subprotocol = f"pywry.token.{token}"

        async with websockets.connect(ws_url, subprotocols=[subprotocol]) as ws:
            # Connection succeeded
            await ws.send(
                json.dumps(
                    {
                        "type": "ping",
                        "data": {},
                        "widgetId": widget_id,
                    }
                )
            )
            # If we get here without exception, connection worked
            await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_websocket_rejected_with_wrong_token(self, redis_widget_store) -> None:
        """WebSocket should be rejected with wrong token."""
        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        widget_id = f"ws-reject-{uuid.uuid4().hex[:8]}"
        correct_token = f"correct-{uuid.uuid4().hex[:16]}"
        wrong_token = f"wrong-{uuid.uuid4().hex[:16]}"

        await store.register(widget_id, "<div>Test</div>", token=correct_token)
        _state.widget_tokens[widget_id] = correct_token

        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        ws_url = f"ws://127.0.0.1:{port}/ws/{widget_id}"

        with pytest.raises((InvalidStatusCode, ConnectionRefusedError, OSError, Exception)):
            async with websockets.connect(
                ws_url,
                subprotocols=[f"pywry.token.{wrong_token}"],
                close_timeout=2,
            ) as ws:
                await ws.recv()


# ============================================================================
# PART 7: Cross-Worker Widget Access via Redis
# ============================================================================


class TestCrossWorkerAccess:
    """Test that widgets registered by one 'worker' are accessible by another."""

    @pytest.mark.asyncio
    async def test_widget_accessible_from_different_store_instance(
        self, redis_widget_store
    ) -> None:
        """Widget registered by one store instance is accessible by another."""
        from pywry.state.redis import RedisWidgetStore

        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        port = config["port"]
        redis_url = config["redis_url"]
        prefix = config["prefix"]
        widget_id = f"cross-worker-{uuid.uuid4().hex[:8]}"
        html = "<div>Cross-worker content</div>"

        # Worker 1 registers the widget (use the shared store)
        await store.register(widget_id, html)

        # Worker 2 (different store instance) should see it
        store2 = RedisWidgetStore(redis_url=redis_url, prefix=prefix)
        exists = await store2.exists(widget_id)
        assert exists

        retrieved_html = await store2.get_html(widget_id)
        assert retrieved_html == html

        # Server (yet another consumer) should serve it
        _start_server(port=port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", port)

        status, body = http_get(f"http://127.0.0.1:{port}/widget/{widget_id}")
        assert status == 200
        assert "Cross-worker content" in body

        # Cleanup
        await store2.close()


# ============================================================================
# PART 8: Verify Redis Activity with Direct Inspection
# ============================================================================


class TestRedisDirectInspection:
    """Directly inspect Redis to verify data is stored correctly."""

    @pytest.mark.asyncio
    async def test_verify_redis_data_structure(self, redis_widget_store) -> None:
        """Verify the actual data structure in Redis."""
        import redis.asyncio as aioredis

        store = redis_widget_store["store"]
        config = redis_widget_store["config"]
        redis_url = config["redis_url"]
        prefix = config["prefix"]
        widget_id = f"inspect-{uuid.uuid4().hex[:8]}"
        html = "<div>Inspect me</div>"
        token = "inspect-token-123"

        await store.register(widget_id, html, token=token)

        client = aioredis.from_url(redis_url, decode_responses=True)
        try:
            # List all keys
            keys = [key async for key in client.scan_iter(f"{prefix}*")]

            print(f"\n=== Redis Keys ({len(keys)}) ===")
            for key in sorted(keys):
                key_type = await client.type(key)
                print(f"  {key} ({key_type})")

                if key_type == "hash":
                    data = await client.hgetall(key)
                    for field, value in data.items():
                        preview = value[:50] + "..." if len(value) > 50 else value
                        print(f"    {field}: {preview}")
                elif key_type == "set":
                    members = await client.smembers(key)
                    print(f"    members: {members}")

            # Verify our widget is in there
            assert any(widget_id in k for k in keys), f"Widget {widget_id} not found in keys"
        finally:
            await client.aclose()
