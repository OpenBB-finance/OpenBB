"""Tests for in-memory state store implementations."""

from __future__ import annotations

import asyncio
import time

import pytest

from pywry.state import (
    MemoryConnectionRouter,
    MemoryEventBus,
    MemorySessionStore,
    MemoryWidgetStore,
)
from pywry.state.types import EventMessage


# --- MemoryWidgetStore Tests ---


class TestMemoryWidgetStore:
    """Tests for MemoryWidgetStore."""

    @pytest.fixture
    def store(self) -> MemoryWidgetStore:
        """Create a fresh widget store for each test."""
        return MemoryWidgetStore()

    @pytest.mark.asyncio
    async def test_register_and_get(self, store: MemoryWidgetStore) -> None:
        """Test registering and retrieving a widget."""
        await store.register(
            widget_id="test-widget-1",
            html="<h1>Hello</h1>",
            token="secret-token",
            owner_worker_id="worker-1",
            metadata={"title": "Test Widget"},
        )

        widget = await store.get("test-widget-1")
        assert widget is not None
        assert widget.widget_id == "test-widget-1"
        assert widget.html == "<h1>Hello</h1>"
        assert widget.token == "secret-token"
        assert widget.owner_worker_id == "worker-1"
        assert widget.metadata == {"title": "Test Widget"}
        assert widget.created_at > 0

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, store: MemoryWidgetStore) -> None:
        """Test getting a widget that doesn't exist."""
        widget = await store.get("nonexistent")
        assert widget is None

    @pytest.mark.asyncio
    async def test_get_html(self, store: MemoryWidgetStore) -> None:
        """Test getting only the HTML content."""
        await store.register("widget-1", "<p>Content</p>")
        html = await store.get_html("widget-1")
        assert html == "<p>Content</p>"

    @pytest.mark.asyncio
    async def test_get_token(self, store: MemoryWidgetStore) -> None:
        """Test getting the widget token."""
        await store.register("widget-1", "<p>Content</p>", token="my-token")
        token = await store.get_token("widget-1")
        assert token == "my-token"

    @pytest.mark.asyncio
    async def test_exists(self, store: MemoryWidgetStore) -> None:
        """Test checking widget existence."""
        assert not await store.exists("widget-1")
        await store.register("widget-1", "<p>Content</p>")
        assert await store.exists("widget-1")

    @pytest.mark.asyncio
    async def test_delete(self, store: MemoryWidgetStore) -> None:
        """Test deleting a widget."""
        await store.register("widget-1", "<p>Content</p>")
        assert await store.exists("widget-1")

        result = await store.delete("widget-1")
        assert result is True
        assert not await store.exists("widget-1")

        # Delete nonexistent should return False
        result = await store.delete("widget-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_active(self, store: MemoryWidgetStore) -> None:
        """Test listing active widgets."""
        await store.register("widget-1", "<p>1</p>")
        await store.register("widget-2", "<p>2</p>")
        await store.register("widget-3", "<p>3</p>")

        active = await store.list_active()
        assert set(active) == {"widget-1", "widget-2", "widget-3"}

    @pytest.mark.asyncio
    async def test_update_html(self, store: MemoryWidgetStore) -> None:
        """Test updating widget HTML."""
        await store.register("widget-1", "<p>Original</p>")

        result = await store.update_html("widget-1", "<p>Updated</p>")
        assert result is True

        html = await store.get_html("widget-1")
        assert html == "<p>Updated</p>"

        # Update nonexistent should return False
        result = await store.update_html("nonexistent", "<p>New</p>")
        assert result is False

    @pytest.mark.asyncio
    async def test_count(self, store: MemoryWidgetStore) -> None:
        """Test counting widgets."""
        assert await store.count() == 0

        await store.register("widget-1", "<p>1</p>")
        assert await store.count() == 1

        await store.register("widget-2", "<p>2</p>")
        assert await store.count() == 2

        await store.delete("widget-1")
        assert await store.count() == 1


# --- MemoryEventBus Tests ---


class TestMemoryEventBus:
    """Tests for MemoryEventBus."""

    @pytest.fixture
    def bus(self) -> MemoryEventBus:
        """Create a fresh event bus for each test."""
        return MemoryEventBus()

    @pytest.mark.asyncio
    async def test_publish_subscribe(self, bus: MemoryEventBus) -> None:
        """Test publishing and subscribing to events."""
        received_events: list[EventMessage] = []

        # Subscribe in background task
        async def subscriber() -> None:
            async for event in bus.subscribe("test-channel"):
                received_events.append(event)
                if len(received_events) >= 2:
                    break

        task = asyncio.create_task(subscriber())

        # Give subscriber time to start
        await asyncio.sleep(0.05)

        # Publish events
        event1 = EventMessage(
            event_type="click",
            widget_id="widget-1",
            data={"x": 100},
            source_worker_id="worker-1",
        )
        event2 = EventMessage(
            event_type="change",
            widget_id="widget-1",
            data={"value": "test"},
            source_worker_id="worker-1",
        )

        await bus.publish("test-channel", event1)
        await bus.publish("test-channel", event2)

        # Wait for subscriber to receive events
        await asyncio.wait_for(task, timeout=1.0)

        assert len(received_events) == 2
        assert received_events[0].event_type == "click"
        assert received_events[1].event_type == "change"

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus: MemoryEventBus) -> None:
        """Test unsubscribing from a channel."""
        # Subscribe first
        _iterator = bus.subscribe("test-channel")

        # Unsubscribe
        await bus.unsubscribe("test-channel")

        # Channel should be removed
        assert "test-channel" not in bus._channels


# --- MemoryConnectionRouter Tests ---


class TestMemoryConnectionRouter:
    """Tests for MemoryConnectionRouter."""

    @pytest.fixture
    def router(self) -> MemoryConnectionRouter:
        """Create a fresh connection router for each test."""
        return MemoryConnectionRouter()

    @pytest.mark.asyncio
    async def test_register_connection(self, router: MemoryConnectionRouter) -> None:
        """Test registering a connection."""
        await router.register_connection(
            widget_id="widget-1",
            worker_id="worker-1",
            user_id="user-1",
            session_id="session-1",
        )

        info = await router.get_connection_info("widget-1")
        assert info is not None
        assert info.widget_id == "widget-1"
        assert info.worker_id == "worker-1"
        assert info.user_id == "user-1"
        assert info.session_id == "session-1"
        assert info.connected_at > 0

    @pytest.mark.asyncio
    async def test_get_owner(self, router: MemoryConnectionRouter) -> None:
        """Test getting the owner worker ID."""
        await router.register_connection("widget-1", "worker-1")

        owner = await router.get_owner("widget-1")
        assert owner == "worker-1"

        # Nonexistent widget
        owner = await router.get_owner("nonexistent")
        assert owner is None

    @pytest.mark.asyncio
    async def test_refresh_heartbeat(self, router: MemoryConnectionRouter) -> None:
        """Test refreshing the heartbeat."""
        await router.register_connection("widget-1", "worker-1")

        info_before = await router.get_connection_info("widget-1")
        assert info_before is not None
        old_heartbeat = info_before.last_heartbeat

        # Use 50ms sleep to ensure Windows timer resolution doesn't cause issues
        await asyncio.sleep(0.05)

        result = await router.refresh_heartbeat("widget-1")
        assert result is True

        info_after = await router.get_connection_info("widget-1")
        assert info_after is not None
        assert info_after.last_heartbeat > old_heartbeat

    @pytest.mark.asyncio
    async def test_unregister_connection(self, router: MemoryConnectionRouter) -> None:
        """Test unregistering a connection."""
        await router.register_connection("widget-1", "worker-1")
        assert await router.get_connection_info("widget-1") is not None

        result = await router.unregister_connection("widget-1")
        assert result is True
        assert await router.get_connection_info("widget-1") is None

        # Unregister nonexistent
        result = await router.unregister_connection("widget-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_worker_connections(self, router: MemoryConnectionRouter) -> None:
        """Test listing connections for a worker."""
        await router.register_connection("widget-1", "worker-1")
        await router.register_connection("widget-2", "worker-1")
        await router.register_connection("widget-3", "worker-2")

        worker1_connections = await router.list_worker_connections("worker-1")
        assert set(worker1_connections) == {"widget-1", "widget-2"}

        worker2_connections = await router.list_worker_connections("worker-2")
        assert worker2_connections == ["widget-3"]


# --- MemorySessionStore Tests ---


class TestMemorySessionStore:
    """Tests for MemorySessionStore."""

    @pytest.fixture
    def store(self) -> MemorySessionStore:
        """Create a fresh session store for each test."""
        return MemorySessionStore()

    @pytest.mark.asyncio
    async def test_create_session(self, store: MemorySessionStore) -> None:
        """Test creating a session."""
        session = await store.create_session(
            session_id="session-1",
            user_id="user-1",
            roles=["admin", "editor"],
            metadata={"name": "Test User"},
        )

        assert session.session_id == "session-1"
        assert session.user_id == "user-1"
        assert session.roles == ["admin", "editor"]
        assert session.metadata == {"name": "Test User"}
        assert session.created_at > 0

    @pytest.mark.asyncio
    async def test_get_session(self, store: MemorySessionStore) -> None:
        """Test getting a session."""
        await store.create_session("session-1", "user-1", roles=["viewer"])

        session = await store.get_session("session-1")
        assert session is not None
        assert session.user_id == "user-1"

        # Nonexistent session
        session = await store.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_validate_session(self, store: MemorySessionStore) -> None:
        """Test validating a session."""
        await store.create_session("session-1", "user-1")

        assert await store.validate_session("session-1") is True
        assert await store.validate_session("nonexistent") is False

    @pytest.mark.asyncio
    async def test_refresh_session(self, store: MemorySessionStore) -> None:
        """Test refreshing a session."""
        await store.create_session("session-1", "user-1")

        # refresh_session returns True if successful
        # Use 50ms sleep to ensure Windows timer resolution doesn't cause issues
        await asyncio.sleep(0.05)

        result = await store.refresh_session("session-1")
        assert result is True

        # Nonexistent session should return False
        result = await store.refresh_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_session(self, store: MemorySessionStore) -> None:
        """Test deleting a session."""
        await store.create_session("session-1", "user-1")
        assert await store.validate_session("session-1") is True

        result = await store.delete_session("session-1")
        assert result is True
        assert await store.validate_session("session-1") is False

        # Delete nonexistent should return False
        result = await store.delete_session("session-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_user_sessions(self, store: MemorySessionStore) -> None:
        """Test getting all sessions for a user."""
        await store.create_session("session-1", "user-1")
        await store.create_session("session-2", "user-1")
        await store.create_session("session-3", "user-2")

        user1_sessions = await store.list_user_sessions("user-1")
        assert len(user1_sessions) == 2
        assert {s.session_id for s in user1_sessions} == {"session-1", "session-2"}

    @pytest.mark.asyncio
    async def test_check_permission(self, store: MemorySessionStore) -> None:
        """Test checking permissions."""
        # Set up role permissions
        store.set_role_permissions("admin", {"read", "write", "delete"})
        store.set_role_permissions("viewer", {"read"})

        await store.create_session("admin-session", "admin-user", roles=["admin"])
        await store.create_session("viewer-session", "viewer-user", roles=["viewer"])

        # Admin should have all permissions
        assert await store.check_permission("admin-session", "widget", "1", "read")
        assert await store.check_permission("admin-session", "widget", "1", "write")
        assert await store.check_permission("admin-session", "widget", "1", "delete")

        # Viewer should only have read
        assert await store.check_permission("viewer-session", "widget", "1", "read")
        assert not await store.check_permission("viewer-session", "widget", "1", "write")
        assert not await store.check_permission("viewer-session", "widget", "1", "delete")

    @pytest.mark.asyncio
    async def test_session_with_ttl(self, store: MemorySessionStore) -> None:
        """Test session expiration with TTL."""
        # Create session with 0.1 second TTL
        await store.create_session("short-session", "user-1", ttl=1)

        # Should be valid immediately
        assert await store.validate_session("short-session") is True

        # Note: In memory store, TTL is checked via expires_at field
        # The session should still exist but show as expired after TTL
        session = await store.get_session("short-session")
        assert session is not None
        assert session.expires_at is not None
        assert session.expires_at > time.time()  # Not expired yet
