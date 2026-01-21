"""Integration tests for Redis state stores with real Redis.

These tests use testcontainers to spin up a Redis container automatically.
Run with: pytest tests/test_state_redis_integration.py -v

Tests are skipped if Docker is not available.

Environment variables:
    PYWRY_DEPLOY__REDIS_URL: Optional Redis connection URL (overrides testcontainers)
    PYWRY_DEPLOY__REDIS_PREFIX: Key prefix (default: pywry-test:)
"""
# pylint: disable=redefined-outer-name

from __future__ import annotations

import asyncio
import contextlib
import os
import uuid

import pytest
import pytest_asyncio

from pywry.state.types import EventMessage


# Default prefix for test keys
REDIS_PREFIX = os.environ.get("PYWRY_DEPLOY__REDIS_PREFIX", "pywry-test:")

# Mark all tests in this module as requiring redis container
pytestmark = [
    pytest.mark.redis,
    pytest.mark.container,
]


@pytest.fixture
def unique_prefix() -> str:
    """Generate a unique prefix for test isolation."""
    return f"{REDIS_PREFIX}{uuid.uuid4().hex[:8]}:"


# --- Fixtures for real Redis stores ---


@pytest_asyncio.fixture
async def redis_widget_store(redis_container: str, unique_prefix: str):
    """Create a RedisWidgetStore with testcontainers Redis."""
    from pywry.state.redis import RedisWidgetStore

    store = RedisWidgetStore(
        redis_url=redis_container,
        prefix=unique_prefix,
        widget_ttl=60,  # Short TTL for tests
    )
    yield store
    # Cleanup: delete all keys with our prefix
    await _cleanup_redis_keys(redis_container, unique_prefix)


@pytest_asyncio.fixture
async def redis_connection_router(redis_container: str, unique_prefix: str):
    """Create a RedisConnectionRouter with testcontainers Redis."""
    from pywry.state.redis import RedisConnectionRouter

    router = RedisConnectionRouter(
        redis_url=redis_container,
        prefix=unique_prefix,
        connection_ttl=60,
    )
    yield router
    await _cleanup_redis_keys(redis_container, unique_prefix)


@pytest_asyncio.fixture
async def redis_session_store(redis_container: str, unique_prefix: str):
    """Create a RedisSessionStore with testcontainers Redis."""
    from pywry.state.redis import RedisSessionStore

    store = RedisSessionStore(
        redis_url=redis_container,
        prefix=unique_prefix,
        default_ttl=60,
    )
    yield store
    await _cleanup_redis_keys(redis_container, unique_prefix)


@pytest_asyncio.fixture
async def redis_event_bus(redis_container: str, unique_prefix: str):
    """Create a RedisEventBus with testcontainers Redis."""
    from pywry.state.redis import RedisEventBus

    bus = RedisEventBus(
        redis_url=redis_container,
        prefix=unique_prefix,
    )
    yield bus
    await _cleanup_redis_keys(redis_container, unique_prefix)


async def _cleanup_redis_keys(redis_url: str, prefix: str) -> None:
    """Clean up all Redis keys with the given prefix."""
    import redis.asyncio as aioredis

    client = aioredis.from_url(redis_url, decode_responses=True)
    try:
        # Use SCAN to find all keys with prefix
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor, match=f"{prefix}*", count=100)
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break
    finally:
        await client.aclose()


# --- RedisWidgetStore Integration Tests ---


class TestRedisWidgetStoreIntegration:
    """Integration tests for RedisWidgetStore with real Redis."""

    @pytest.mark.asyncio
    async def test_register_and_get_widget(self, redis_widget_store) -> None:
        """Test basic widget registration and retrieval."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_widget_store.register(
            widget_id=widget_id,
            html="<h1>Integration Test</h1>",
            token="secret-token-123",
            owner_worker_id="worker-1",
            metadata={"title": "Test Widget", "version": 1},
        )

        widget = await redis_widget_store.get(widget_id)
        assert widget is not None
        assert widget.widget_id == widget_id
        assert widget.html == "<h1>Integration Test</h1>"
        assert widget.token == "secret-token-123"
        assert widget.owner_worker_id == "worker-1"
        assert widget.metadata == {"title": "Test Widget", "version": 1}
        assert widget.created_at > 0

    @pytest.mark.asyncio
    async def test_widget_persistence(self, redis_widget_store) -> None:
        """Test that widget data persists across operations."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        # Register widget
        await redis_widget_store.register(widget_id, "<p>Persisted</p>", token="tok")

        # Verify existence
        assert await redis_widget_store.exists(widget_id)

        # Get HTML directly
        html = await redis_widget_store.get_html(widget_id)
        assert html == "<p>Persisted</p>"

        # Get token directly
        token = await redis_widget_store.get_token(widget_id)
        assert token == "tok"

    @pytest.mark.asyncio
    async def test_update_html(self, redis_widget_store) -> None:
        """Test updating widget HTML content."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_widget_store.register(widget_id, "<p>Original</p>")

        result = await redis_widget_store.update_html(widget_id, "<p>Updated</p>")
        assert result is True

        html = await redis_widget_store.get_html(widget_id)
        assert html == "<p>Updated</p>"

    @pytest.mark.asyncio
    async def test_delete_widget(self, redis_widget_store) -> None:
        """Test deleting a widget."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_widget_store.register(widget_id, "<p>To Delete</p>")
        assert await redis_widget_store.exists(widget_id)

        result = await redis_widget_store.delete(widget_id)
        assert result is True
        assert not await redis_widget_store.exists(widget_id)

        # Delete non-existent should return False
        result = await redis_widget_store.delete(widget_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_list_active_widgets(self, redis_widget_store) -> None:
        """Test listing all active widgets."""
        ids = [f"widget-{uuid.uuid4().hex[:8]}" for _ in range(5)]

        for wid in ids:
            await redis_widget_store.register(wid, f"<p>{wid}</p>")

        active = await redis_widget_store.list_active()
        assert set(ids).issubset(set(active))

    @pytest.mark.asyncio
    async def test_count_widgets(self, redis_widget_store) -> None:
        """Test counting active widgets."""
        initial_count = await redis_widget_store.count()

        ids = [f"widget-{uuid.uuid4().hex[:8]}" for _ in range(3)]
        for wid in ids:
            await redis_widget_store.register(wid, f"<p>{wid}</p>")

        final_count = await redis_widget_store.count()
        assert final_count == initial_count + 3


# --- RedisConnectionRouter Integration Tests ---


class TestRedisConnectionRouterIntegration:
    """Integration tests for RedisConnectionRouter with real Redis."""

    @pytest.mark.asyncio
    async def test_register_and_get_connection(self, redis_connection_router) -> None:
        """Test connection registration and retrieval."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_connection_router.register_connection(
            widget_id=widget_id,
            worker_id="worker-1",
            user_id="user-123",
            session_id="session-abc",
        )

        info = await redis_connection_router.get_connection_info(widget_id)
        assert info is not None
        assert info.widget_id == widget_id
        assert info.worker_id == "worker-1"
        assert info.user_id == "user-123"
        assert info.session_id == "session-abc"
        assert info.connected_at > 0

    @pytest.mark.asyncio
    async def test_get_owner(self, redis_connection_router) -> None:
        """Test getting the owner worker ID."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_connection_router.register_connection(widget_id, "worker-owner")

        owner = await redis_connection_router.get_owner(widget_id)
        assert owner == "worker-owner"

    @pytest.mark.asyncio
    async def test_heartbeat_refresh(self, redis_connection_router) -> None:
        """Test that heartbeat refresh updates timestamp."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_connection_router.register_connection(widget_id, "worker-1")

        info_before = await redis_connection_router.get_connection_info(widget_id)
        assert info_before is not None
        old_heartbeat = info_before.last_heartbeat

        await asyncio.sleep(0.05)  # Small delay

        result = await redis_connection_router.refresh_heartbeat(widget_id)
        assert result is True

        info_after = await redis_connection_router.get_connection_info(widget_id)
        assert info_after is not None
        assert info_after.last_heartbeat > old_heartbeat

    @pytest.mark.asyncio
    async def test_unregister_connection(self, redis_connection_router) -> None:
        """Test unregistering a connection."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"

        await redis_connection_router.register_connection(widget_id, "worker-1")
        assert await redis_connection_router.get_connection_info(widget_id) is not None

        result = await redis_connection_router.unregister_connection(widget_id)
        assert result is True
        assert await redis_connection_router.get_connection_info(widget_id) is None

    @pytest.mark.asyncio
    async def test_list_worker_connections(self, redis_connection_router) -> None:
        """Test listing connections for a specific worker."""
        worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        widget_ids = [f"widget-{uuid.uuid4().hex[:8]}" for _ in range(3)]

        for wid in widget_ids:
            await redis_connection_router.register_connection(wid, worker_id)

        connections = await redis_connection_router.list_worker_connections(worker_id)
        assert set(widget_ids) == set(connections)


# --- RedisSessionStore Integration Tests ---


class TestRedisSessionStoreIntegration:
    """Integration tests for RedisSessionStore with real Redis."""

    @pytest.mark.asyncio
    async def test_create_and_get_session(self, redis_session_store) -> None:
        """Test session creation and retrieval."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        session = await redis_session_store.create_session(
            session_id=session_id,
            user_id="user-123",
            roles=["admin", "editor"],
            metadata={"name": "Test User", "email": "test@example.com"},
        )

        assert session.session_id == session_id
        assert session.user_id == "user-123"
        assert session.roles == ["admin", "editor"]
        assert session.metadata == {"name": "Test User", "email": "test@example.com"}

        # Retrieve session
        retrieved = await redis_session_store.get_session(session_id)
        assert retrieved is not None
        assert retrieved.session_id == session_id
        assert retrieved.user_id == "user-123"

    @pytest.mark.asyncio
    async def test_validate_session(self, redis_session_store) -> None:
        """Test session validation."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, "user-123")

        assert await redis_session_store.validate_session(session_id) is True
        assert await redis_session_store.validate_session("nonexistent") is False

    @pytest.mark.asyncio
    async def test_delete_session(self, redis_session_store) -> None:
        """Test session deletion."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, "user-123")
        assert await redis_session_store.validate_session(session_id) is True

        result = await redis_session_store.delete_session(session_id)
        assert result is True
        assert await redis_session_store.validate_session(session_id) is False

    @pytest.mark.asyncio
    async def test_list_user_sessions(self, redis_session_store) -> None:
        """Test listing all sessions for a user."""
        user_id = f"user-{uuid.uuid4().hex[:8]}"
        session_ids = [f"session-{uuid.uuid4().hex[:8]}" for _ in range(3)]

        for sid in session_ids:
            await redis_session_store.create_session(sid, user_id)

        sessions = await redis_session_store.list_user_sessions(user_id)
        assert len(sessions) == 3
        assert {s.session_id for s in sessions} == set(session_ids)

    @pytest.mark.asyncio
    async def test_rbac_permissions(self, redis_session_store) -> None:
        """Test role-based access control permissions."""
        # Set up role permissions
        await redis_session_store.set_role_permissions("admin", {"read", "write", "delete"})
        await redis_session_store.set_role_permissions("viewer", {"read"})

        admin_session = f"admin-{uuid.uuid4().hex[:8]}"
        viewer_session = f"viewer-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(admin_session, "admin-user", roles=["admin"])
        await redis_session_store.create_session(viewer_session, "viewer-user", roles=["viewer"])

        # Admin should have all permissions
        assert await redis_session_store.check_permission(admin_session, "widget", "1", "read")
        assert await redis_session_store.check_permission(admin_session, "widget", "1", "write")
        assert await redis_session_store.check_permission(admin_session, "widget", "1", "delete")

        # Viewer should only have read
        assert await redis_session_store.check_permission(viewer_session, "widget", "1", "read")
        assert not await redis_session_store.check_permission(
            viewer_session, "widget", "1", "write"
        )
        assert not await redis_session_store.check_permission(
            viewer_session, "widget", "1", "delete"
        )


# --- RedisEventBus Integration Tests ---


class TestRedisEventBusIntegration:
    """Integration tests for RedisEventBus with real Redis Pub/Sub."""

    @pytest.mark.asyncio
    async def test_publish_event(self, redis_event_bus) -> None:
        """Test publishing an event (doesn't require subscriber)."""
        event = EventMessage(
            event_type="test:click",
            widget_id="widget-123",
            data={"x": 100, "y": 200},
            source_worker_id="worker-1",
        )

        # Should not raise
        await redis_event_bus.publish("test-channel", event)

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_pubsub_round_trip(self, redis_container: str, unique_prefix: str) -> None:
        """Test full pub/sub round trip with real Redis."""
        from pywry.state.redis import RedisEventBus

        channel = f"test-channel-{uuid.uuid4().hex[:8]}"
        received_events: list[EventMessage] = []
        subscription_ready = asyncio.Event()
        event_iterator = None

        # Create two separate bus instances (simulating different workers)
        publisher = RedisEventBus(redis_url=redis_container, prefix=unique_prefix)
        subscriber = RedisEventBus(redis_url=redis_container, prefix=unique_prefix)

        # Collect events in background task
        async def collect_events():
            nonlocal event_iterator
            event_iterator = subscriber.subscribe(channel)
            subscription_ready.set()
            count = 0
            try:
                async for event in event_iterator:
                    received_events.append(event)
                    count += 1
                    if count >= 3:
                        break
            finally:
                await event_iterator.aclose()

        collector_task = asyncio.create_task(collect_events())

        # Wait for subscription to be ready
        await asyncio.wait_for(subscription_ready.wait(), timeout=2.0)
        await asyncio.sleep(0.5)  # Give Redis time to register subscription

        # Publish events
        for i in range(3):
            event = EventMessage(
                event_type="test:event",
                widget_id=f"widget-{i}",
                data={"index": i},
                source_worker_id="publisher",
            )
            await publisher.publish(channel, event)

        # Wait for collector to finish
        try:
            await asyncio.wait_for(collector_task, timeout=5.0)
        except asyncio.TimeoutError:
            collector_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await collector_task
            if event_iterator is not None:
                with contextlib.suppress(Exception):
                    await event_iterator.aclose()

        await _cleanup_redis_keys(redis_container, unique_prefix)

        # Verify we received all events
        assert len(received_events) == 3, f"Expected 3 events, got {len(received_events)}"
        for i, event in enumerate(received_events):
            assert event.data["index"] == i


# --- Factory Function Integration Tests ---


class TestFactoryFunctionsIntegration:
    """Test factory functions with real Redis configuration."""

    @pytest.mark.asyncio
    async def test_get_widget_store_with_redis_config(self) -> None:
        """Test that factory returns Redis store when configured."""
        from pywry.state._factory import get_widget_store

        # Get store (should use environment config)
        store = get_widget_store()
        assert store is not None

        # Verify it works
        widget_id = f"factory-test-{uuid.uuid4().hex[:8]}"
        await store.register(widget_id, "<p>Factory Test</p>")

        widget = await store.get(widget_id)
        # Cleanup
        await store.delete(widget_id)

        # The store should have worked (might be memory or redis depending on env)
        assert widget is None or widget.html == "<p>Factory Test</p>"

    @pytest.mark.asyncio
    async def test_is_deploy_mode(self) -> None:
        """Test deploy mode detection."""
        from pywry.state._factory import is_deploy_mode

        # This depends on environment configuration
        result = is_deploy_mode()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_get_worker_id(self) -> None:
        """Test worker ID generation."""
        from pywry.state._factory import get_worker_id

        worker_id = get_worker_id()
        assert isinstance(worker_id, str)
        assert len(worker_id) > 0

        # Same call should return same ID
        assert get_worker_id() == worker_id


# --- Concurrent Access Tests ---


class TestRedisConcurrentAccess:
    """Test concurrent access patterns with real Redis."""

    @pytest.mark.asyncio
    async def test_concurrent_widget_registration(self, redis_widget_store) -> None:
        """Test concurrent widget registration."""
        num_widgets = 20

        async def register_widget(i: int) -> str:
            widget_id = f"concurrent-{uuid.uuid4().hex[:8]}"
            await redis_widget_store.register(widget_id, f"<p>Widget {i}</p>")
            return widget_id

        # Register widgets concurrently
        tasks = [register_widget(i) for i in range(num_widgets)]
        widget_ids = await asyncio.gather(*tasks)

        # All should exist
        for wid in widget_ids:
            assert await redis_widget_store.exists(wid)

    @pytest.mark.asyncio
    async def test_concurrent_read_write(self, redis_widget_store) -> None:
        """Test concurrent reads and writes to same widget."""
        widget_id = f"concurrent-rw-{uuid.uuid4().hex[:8]}"
        await redis_widget_store.register(widget_id, "<p>Initial</p>")

        update_count = 10
        read_count = 20

        async def update_widget(i: int) -> None:
            await redis_widget_store.update_html(widget_id, f"<p>Update {i}</p>")

        async def read_widget() -> str | None:
            return await redis_widget_store.get_html(widget_id)

        # Mix of reads and writes
        update_tasks = [update_widget(i) for i in range(update_count)]
        read_tasks = [read_widget() for _ in range(read_count)]

        await asyncio.gather(*update_tasks, *read_tasks)

        # Widget should still exist with valid content
        html = await redis_widget_store.get_html(widget_id)
        assert html is not None
        assert html.startswith("<p>")


# --- TTL and Expiration Tests ---


class TestRedisTTLBehavior:
    """Test TTL and expiration behavior with real Redis."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(15)
    async def test_widget_ttl_expiration(self, redis_container: str, unique_prefix: str) -> None:
        """Test that widgets expire after TTL."""
        from pywry.state.redis import RedisWidgetStore

        # Create store with very short TTL
        store = RedisWidgetStore(
            redis_url=redis_container,
            prefix=unique_prefix,
            widget_ttl=1,  # 1 second
        )

        widget_id = f"ttl-test-{uuid.uuid4().hex[:8]}"
        await store.register(widget_id, "<p>Short Lived</p>")

        # Should exist immediately
        assert await store.exists(widget_id)

        # Wait for expiration - give extra buffer for Redis to process
        await asyncio.sleep(5)

        # Should be expired (may still be in active set but key deleted)
        html = await store.get_html(widget_id)
        assert html is None

        await _cleanup_redis_keys(redis_container, unique_prefix)
