"""Deploy mode integration tests with real Redis and full stack.

These tests validate the complete authentication, RBAC, and session
management system in deploy mode with Redis as the state backend.

Run with: pytest tests/test_deploy_mode_integration.py -v

Tests cover real deployment scenarios:
- Full ServerStateManager with Redis backend
- Widget registration and access control
- Session-based authentication flow
- Cross-worker routing and event broadcasting
- Connection management with RBAC enforcement
- Real HTTP/WebSocket authentication scenarios
"""

# pylint: disable=too-many-lines,redefined-outer-name,unused-argument

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import pytest_asyncio

from pywry.state.auth import (
    AuthConfig,
    AuthMiddleware,
    generate_session_token,
    generate_widget_token,
)


# Tests now support both Redis and Memory backends - no skip marks needed


def _should_use_memory_backend() -> bool:
    """Check if memory backend should be used based on env var."""
    # Only use memory if explicitly set (e.g., on macOS ARM)
    return os.environ.get("PYWRY_DEPLOY__STATE_BACKEND", "").lower() == "memory"


# --- Fixtures ---


@pytest.fixture
def unique_prefix() -> str:
    """Generate a unique prefix for test isolation."""
    return f"pywry-deploy-test:{uuid.uuid4().hex[:8]}:"


@pytest.fixture
def auth_secret() -> str:
    """Generate a consistent secret for token signing."""
    return "deploy-test-secret-key-for-signing"


@pytest.fixture
def deploy_env_vars(redis_container: str, unique_prefix: str):
    """Set up deploy mode environment variables using session-scoped Redis.

    Uses the session-scoped redis_container fixture.
    Tests will be skipped if Docker is not available.
    """
    env_backup = {
        "PYWRY_DEPLOY_MODE": os.environ.get("PYWRY_DEPLOY_MODE"),
        "PYWRY_DEPLOY__STATE_BACKEND": os.environ.get("PYWRY_DEPLOY__STATE_BACKEND"),
        "PYWRY_DEPLOY__REDIS_URL": os.environ.get("PYWRY_DEPLOY__REDIS_URL"),
        "PYWRY_DEPLOY__REDIS_PREFIX": os.environ.get("PYWRY_DEPLOY__REDIS_PREFIX"),
        "PYWRY_DEPLOY__AUTH_ENABLED": os.environ.get("PYWRY_DEPLOY__AUTH_ENABLED"),
    }

    # Set deploy mode environment
    os.environ["PYWRY_DEPLOY_MODE"] = "1"
    os.environ["PYWRY_DEPLOY__AUTH_ENABLED"] = "1"
    os.environ["PYWRY_DEPLOY__STATE_BACKEND"] = "redis"
    os.environ["PYWRY_DEPLOY__REDIS_URL"] = redis_container
    os.environ["PYWRY_DEPLOY__REDIS_PREFIX"] = unique_prefix

    yield {
        "backend": "redis",
        "redis_url": redis_container,
        "prefix": unique_prefix,
    }

    # Restore original environment
    for key, value in env_backup.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest_asyncio.fixture
async def redis_cleanup(redis_container: str, unique_prefix: str):
    """Clean up Redis keys after tests."""
    yield

    import redis.asyncio as aioredis

    client = aioredis.from_url(redis_container, decode_responses=True)
    try:
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor, match=f"{unique_prefix}*", count=100)
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def session_store(redis_container: str, unique_prefix: str, redis_cleanup):
    """Create a session store for testing using Redis from testcontainers."""
    from pywry.state.redis import RedisSessionStore

    store = RedisSessionStore(
        redis_url=redis_container,
        prefix=unique_prefix,
        default_ttl=3600,
    )
    yield store
    await store.close()


@pytest_asyncio.fixture
async def widget_store(redis_container: str, unique_prefix: str, redis_cleanup):
    """Create a widget store for testing using Redis from testcontainers."""
    from pywry.state.redis import RedisWidgetStore

    store = RedisWidgetStore(
        redis_url=redis_container,
        prefix=unique_prefix,
        widget_ttl=3600,
    )
    yield store
    await store.close()


@pytest_asyncio.fixture
async def connection_router(redis_container: str, unique_prefix: str, redis_cleanup):
    """Create a connection router for testing using Redis from testcontainers."""
    from pywry.state.redis import RedisConnectionRouter

    router = RedisConnectionRouter(
        redis_url=redis_container,
        prefix=unique_prefix,
        connection_ttl=3600,
    )
    yield router
    await router.close()


@pytest_asyncio.fixture
async def event_bus(redis_container: str, unique_prefix: str, redis_cleanup):
    """Create an event bus for testing using Redis from testcontainers."""
    from pywry.state.redis import RedisEventBus

    bus = RedisEventBus(
        redis_url=redis_container,
        prefix=unique_prefix,
    )
    yield bus
    await bus.close()


# ============================================================================
# PART 1: Deploy Mode Detection and Factory Functions
# ============================================================================


class TestDeployModeDetection:
    """Tests for deploy mode detection and configuration.

    These tests require Redis because they test Redis-specific detection logic.
    Tests will be skipped if redis_container fixture fails.
    """

    def test_deploy_mode_via_env_flag(self, redis_container: str) -> None:
        """Test deploy mode is detected via PYWRY_DEPLOY_MODE=1."""
        from pywry.state._factory import clear_state_caches, is_deploy_mode

        original = os.environ.get("PYWRY_DEPLOY_MODE")
        try:
            os.environ["PYWRY_DEPLOY_MODE"] = "1"
            clear_state_caches()
            assert is_deploy_mode() is True
        finally:
            if original is None:
                os.environ.pop("PYWRY_DEPLOY_MODE", None)
            else:
                os.environ["PYWRY_DEPLOY_MODE"] = original
            clear_state_caches()

    def test_deploy_mode_via_redis_backend(self, redis_container: str) -> None:
        """Test deploy mode is implied when Redis backend is configured."""
        from pywry.state._factory import clear_state_caches, is_deploy_mode

        original_mode = os.environ.get("PYWRY_DEPLOY_MODE")
        original_backend = os.environ.get("PYWRY_DEPLOY__STATE_BACKEND")
        try:
            os.environ.pop("PYWRY_DEPLOY_MODE", None)
            os.environ["PYWRY_DEPLOY__STATE_BACKEND"] = "redis"
            clear_state_caches()
            assert is_deploy_mode() is True
        finally:
            if original_mode is None:
                os.environ.pop("PYWRY_DEPLOY_MODE", None)
            else:
                os.environ["PYWRY_DEPLOY_MODE"] = original_mode
            if original_backend is None:
                os.environ.pop("PYWRY_DEPLOY__STATE_BACKEND", None)
            else:
                os.environ["PYWRY_DEPLOY__STATE_BACKEND"] = original_backend
            clear_state_caches()

    def test_local_mode_default(self) -> None:
        """Test local mode is default when no deploy settings."""
        from pywry.state._factory import clear_state_caches, is_deploy_mode

        original_mode = os.environ.get("PYWRY_DEPLOY_MODE")
        original_backend = os.environ.get("PYWRY_DEPLOY__STATE_BACKEND")
        original_headless = os.environ.get("PYWRY_HEADLESS")
        try:
            os.environ.pop("PYWRY_DEPLOY_MODE", None)
            os.environ.pop("PYWRY_DEPLOY__STATE_BACKEND", None)
            os.environ.pop("PYWRY_HEADLESS", None)
            clear_state_caches()
            assert is_deploy_mode() is False
        finally:
            for key, val in [
                ("PYWRY_DEPLOY_MODE", original_mode),
                ("PYWRY_DEPLOY__STATE_BACKEND", original_backend),
                ("PYWRY_HEADLESS", original_headless),
            ]:
                if val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = val
            clear_state_caches()


# ============================================================================
# PART 2: Full Stack Widget Management in Deploy Mode
# ============================================================================


class TestDeployModeWidgetManagement:
    """Integration tests for widget management in deploy mode."""

    @pytest.mark.asyncio
    async def test_register_widget_with_auth_token(
        self, widget_store, session_store, auth_secret: str
    ) -> None:
        """Test registering a widget with authentication token in deploy mode."""
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"
        widget_token = generate_widget_token(widget_id, auth_secret, ttl=3600)

        await widget_store.register(
            widget_id=widget_id,
            html="<div>Protected Dashboard</div>",
            token=widget_token,
            owner_worker_id="worker-1",
            metadata={"title": "Dashboard", "protected": True},
        )

        # Retrieve and verify
        widget = await widget_store.get(widget_id)
        assert widget is not None
        assert widget.widget_id == widget_id
        assert widget.token == widget_token
        assert widget.metadata["protected"] is True

    @pytest.mark.asyncio
    async def test_widget_access_with_valid_session(
        self, widget_store, session_store, auth_secret: str
    ) -> None:
        """Test widget access with a valid authenticated session."""
        # Create an admin session
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        user_id = f"admin-{uuid.uuid4().hex[:8]}"

        _session = await session_store.create_session(
            session_id=session_id,
            user_id=user_id,
            roles=["admin"],
            metadata={"name": "Admin User"},
        )

        # Set up role permissions
        await session_store.set_role_permissions("admin", {"read", "write", "delete", "admin"})

        # Register a protected widget
        widget_id = f"widget-{uuid.uuid4().hex[:8]}"
        await widget_store.register(
            widget_id=widget_id,
            html="<div>Admin Dashboard</div>",
            token=generate_widget_token(widget_id, auth_secret),
            owner_worker_id="worker-1",
        )

        # Verify admin can access
        can_read = await session_store.check_permission(session_id, "widget", widget_id, "read")
        can_write = await session_store.check_permission(session_id, "widget", widget_id, "write")

        assert can_read is True
        assert can_write is True

    @pytest.mark.asyncio
    async def test_widget_access_denied_for_viewer(
        self, widget_store, session_store, auth_secret: str
    ) -> None:
        """Test that viewer role cannot write to widgets."""
        # Create a viewer session
        session_id = f"viewer-session-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(
            session_id=session_id,
            user_id="viewer-user",
            roles=["viewer"],
        )

        # Set up role permissions
        await session_store.set_role_permissions("viewer", {"read"})

        widget_id = f"widget-{uuid.uuid4().hex[:8]}"
        await widget_store.register(
            widget_id=widget_id,
            html="<div>Read-Only Widget</div>",
            token=generate_widget_token(widget_id, auth_secret),
            owner_worker_id="worker-1",
        )

        # Viewer can read but not write
        can_read = await session_store.check_permission(session_id, "widget", widget_id, "read")
        can_write = await session_store.check_permission(session_id, "widget", widget_id, "write")

        assert can_read is True
        assert can_write is False


# ============================================================================
# PART 3: Cross-Worker Session Sharing in Deploy Mode
# ============================================================================


class TestCrossWorkerDeployMode:
    """Tests for cross-worker functionality in deploy mode.

    These tests require Redis because they test cross-worker scenarios
    where multiple store instances share state via Redis.
    Tests will be skipped if redis_container fixture fails.
    """

    @pytest.mark.asyncio
    async def test_session_created_on_worker1_accessible_on_worker2(
        self, redis_container: str, unique_prefix: str, redis_cleanup
    ) -> None:
        """Test sessions are shared across workers via Redis."""
        from pywry.state.redis import RedisSessionStore

        # Simulate two workers with separate store instances
        worker1_sessions = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_sessions = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        # Worker 1 creates session
        session_id = f"cross-worker-{uuid.uuid4().hex[:8]}"
        _session = await worker1_sessions.create_session(
            session_id=session_id,
            user_id="shared-user",
            roles=["editor"],
            metadata={"origin": "worker-1"},
        )

        # Worker 2 validates and retrieves
        assert await worker2_sessions.validate_session(session_id) is True

        session2 = await worker2_sessions.get_session(session_id)
        assert session2 is not None
        assert session2.user_id == "shared-user"
        assert session2.roles == ["editor"]
        assert session2.metadata["origin"] == "worker-1"

        await worker1_sessions.close()
        await worker2_sessions.close()

    @pytest.mark.asyncio
    async def test_widget_registered_on_worker1_accessible_on_worker2(
        self, redis_container: str, unique_prefix: str, redis_cleanup
    ) -> None:
        """Test widgets are shared across workers via Redis."""
        from pywry.state.redis import RedisWidgetStore

        worker1_widgets = RedisWidgetStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_widgets = RedisWidgetStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        # Worker 1 registers widget
        widget_id = f"shared-widget-{uuid.uuid4().hex[:8]}"
        await worker1_widgets.register(
            widget_id=widget_id,
            html="<div>Shared Widget</div>",
            token="shared-token",
            owner_worker_id="worker-1",
        )

        # Worker 2 can retrieve
        widget = await worker2_widgets.get(widget_id)
        assert widget is not None
        assert widget.widget_id == widget_id
        assert widget.owner_worker_id == "worker-1"

        await worker1_widgets.close()
        await worker2_widgets.close()

    @pytest.mark.asyncio
    async def test_connection_routing_across_workers(
        self, redis_container: str, unique_prefix: str, redis_cleanup
    ) -> None:
        """Test connection routing tracks widget-worker relationships."""
        from pywry.state.redis import RedisConnectionRouter

        worker1_router = RedisConnectionRouter(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_router = RedisConnectionRouter(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        # Widget connects to Worker 1
        widget_id = f"routed-widget-{uuid.uuid4().hex[:8]}"
        await worker1_router.register_connection(
            widget_id=widget_id,
            worker_id="worker-1",
            user_id="user-123",
            session_id="session-abc",
        )

        # Worker 2 can find out which worker owns the connection
        owner = await worker2_router.get_owner(widget_id)
        assert owner == "worker-1"

        connection_info = await worker2_router.get_connection_info(widget_id)
        assert connection_info is not None
        assert connection_info.worker_id == "worker-1"
        assert connection_info.user_id == "user-123"
        assert connection_info.session_id == "session-abc"

        await worker1_router.close()
        await worker2_router.close()


# ============================================================================
# PART 4: Event Broadcasting in Deploy Mode
# ============================================================================


class TestDeployModeEventBroadcasting:
    """Tests for Redis Pub/Sub event broadcasting.

    These tests require Redis because they test Redis Pub/Sub functionality.
    Tests will be skipped if redis_container fixture fails.
    """

    @pytest.mark.asyncio
    async def test_event_published_on_worker1_received_on_worker2(
        self, redis_container: str, unique_prefix: str, redis_cleanup
    ) -> None:
        """Test events are broadcast across workers via Redis Pub/Sub."""
        from pywry.state.redis import RedisEventBus
        from pywry.state.types import EventMessage

        worker1_bus = RedisEventBus(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_bus = RedisEventBus(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        widget_id = f"event-widget-{uuid.uuid4().hex[:8]}"
        channel = f"widget:{widget_id}"
        received_events: list[EventMessage] = []

        async def receiver():
            async for event in worker2_bus.subscribe(channel):
                received_events.append(event)
                if len(received_events) >= 1:
                    break

        # Start receiver in background
        receiver_task = asyncio.create_task(receiver())

        # Give subscriber time to connect
        await asyncio.sleep(0.1)

        # Worker 1 publishes event
        event = EventMessage(
            event_type="test_event",
            widget_id=widget_id,
            data={"message": "Hello from worker 1"},
            source_worker_id="worker-1",
        )
        await worker1_bus.publish(channel, event)

        # Wait for receiver with timeout
        try:
            await asyncio.wait_for(receiver_task, timeout=2.0)
        except asyncio.TimeoutError:
            receiver_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await receiver_task

        # Verify event received
        assert len(received_events) >= 1
        assert received_events[0].event_type == "test_event"
        assert received_events[0].widget_id == widget_id
        assert received_events[0].data["message"] == "Hello from worker 1"

        await worker2_bus.unsubscribe(channel)
        await worker1_bus.close()
        await worker2_bus.close()


# ============================================================================
# PART 5: Real Authentication Flow with Sessions
# ============================================================================


class TestRealAuthenticationFlow:
    """Tests for real-world authentication scenarios."""

    @pytest.mark.asyncio
    async def test_user_login_creates_session(self, session_store) -> None:
        """Test simulated user login creates proper session."""
        user_id = "user@example.com"
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        # Simulate login - create session with user roles from auth provider
        session = await session_store.create_session(
            session_id=session_id,
            user_id=user_id,
            roles=["editor"],
            metadata={
                "login_method": "oauth",
                "provider": "google",
                "name": "Test User",
                "email": user_id,
            },
        )

        assert session.session_id == session_id
        assert session.user_id == user_id
        assert "editor" in session.roles
        assert session.metadata["provider"] == "google"

    @pytest.mark.asyncio
    async def test_session_token_auth_flow(self, session_store, auth_secret: str) -> None:
        """Test bearer token authentication flow."""
        user_id = f"api-user-{uuid.uuid4().hex[:8]}"
        session_id = f"api-session-{uuid.uuid4().hex[:8]}"

        # Create session
        await session_store.create_session(
            session_id=session_id,
            user_id=user_id,
            roles=["admin"],
        )

        # Generate bearer token for user
        token = generate_session_token(user_id, auth_secret, expires_at=None)

        # Validate token
        from pywry.state.auth import validate_session_token

        is_valid, extracted_user_id, _error = validate_session_token(token, auth_secret)

        assert is_valid is True
        assert extracted_user_id == user_id

        # Look up user's sessions
        sessions = await session_store.list_user_sessions(user_id)
        assert len(sessions) == 1
        assert sessions[0].session_id == session_id

    @pytest.mark.asyncio
    async def test_session_expiry_denies_access(self, session_store) -> None:
        """Test that expired sessions deny access."""
        session_id = f"expiring-{uuid.uuid4().hex[:8]}"

        # Create session with very short TTL
        await session_store.create_session(
            session_id=session_id,
            user_id="expiring-user",
            roles=["admin"],
            ttl=1,  # 1 second
        )

        # Initially valid
        assert await session_store.validate_session(session_id) is True

        # Wait for expiry
        await asyncio.sleep(1.5)

        # Now invalid
        assert await session_store.validate_session(session_id) is False

    @pytest.mark.asyncio
    async def test_session_logout_invalidates_access(self, session_store) -> None:
        """Test that logout (session deletion) invalidates access."""
        session_id = f"logout-{uuid.uuid4().hex[:8]}"

        await session_store.create_session(
            session_id=session_id,
            user_id="logout-user",
            roles=["editor"],
        )

        # Valid before logout
        assert await session_store.validate_session(session_id) is True

        # Simulate logout
        await session_store.delete_session(session_id)

        # Invalid after logout
        assert await session_store.validate_session(session_id) is False


# ============================================================================
# PART 6: RBAC Enforcement in Deploy Mode
# ============================================================================


class TestRBACEnforcementDeployMode:
    """Tests for RBAC enforcement with real Redis."""

    @pytest.mark.asyncio
    async def test_role_hierarchy_admin_has_all_permissions(self, session_store) -> None:
        """Test admin role has full permissions."""
        # Configure roles
        await session_store.set_role_permissions(
            "admin",
            {"read", "write", "delete", "admin", "manage_users", "configure"},
        )
        await session_store.set_role_permissions("editor", {"read", "write"})
        await session_store.set_role_permissions("viewer", {"read"})

        # Create admin session
        admin_session = f"admin-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(admin_session, "admin-user", roles=["admin"])

        # Admin has all permissions
        for perm in ["read", "write", "delete", "admin", "manage_users", "configure"]:
            assert await session_store.check_permission(
                admin_session, "system", "settings", perm
            ), f"Admin should have {perm} permission"

    @pytest.mark.asyncio
    async def test_role_hierarchy_editor_limited_permissions(self, session_store) -> None:
        """Test editor role has limited permissions."""
        await session_store.set_role_permissions("editor", {"read", "write"})

        editor_session = f"editor-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(editor_session, "editor-user", roles=["editor"])

        # Editor can read and write
        assert await session_store.check_permission(editor_session, "widget", "w1", "read")
        assert await session_store.check_permission(editor_session, "widget", "w1", "write")

        # But not delete or admin
        assert not await session_store.check_permission(editor_session, "widget", "w1", "delete")
        assert not await session_store.check_permission(editor_session, "widget", "w1", "admin")

    @pytest.mark.asyncio
    async def test_resource_specific_permissions(self, session_store) -> None:
        """Test resource-specific permission grants via metadata."""
        session_id = f"specific-{uuid.uuid4().hex[:8]}"

        # Create session with specific widget access
        await session_store.create_session(
            session_id=session_id,
            user_id="specific-user",
            roles=[],  # No role-based permissions
            metadata={
                "permissions": {
                    "widget:dashboard-1": ["read", "write"],
                    "widget:dashboard-2": ["read"],
                }
            },
        )

        # Can access dashboard-1 with read/write
        assert await session_store.check_permission(session_id, "widget", "dashboard-1", "read")
        assert await session_store.check_permission(session_id, "widget", "dashboard-1", "write")

        # Can only read dashboard-2
        assert await session_store.check_permission(session_id, "widget", "dashboard-2", "read")
        assert not await session_store.check_permission(
            session_id, "widget", "dashboard-2", "write"
        )

        # No access to other dashboards
        assert not await session_store.check_permission(session_id, "widget", "dashboard-3", "read")


# ============================================================================
# PART 7: Auth Middleware Integration
# ============================================================================


class TestAuthMiddlewareIntegration:
    """Tests for AuthMiddleware with real session store."""

    @pytest.mark.asyncio
    async def test_middleware_extracts_session_from_cookie(self, session_store) -> None:
        """Test middleware extracts session from cookie."""
        session_id = f"cookie-test-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(session_id, "cookie-user", roles=["viewer"])

        config = AuthConfig(
            enabled=True,
            session_cookie="pywry_session",
            token_secret="test-secret",
        )

        # Create middleware
        captured_session = {}

        async def mock_app(scope, receive, send):
            captured_session["session"] = scope.get("session")

        middleware = AuthMiddleware(mock_app, session_store, config)

        # Simulate HTTP request with cookie
        scope = {
            "type": "http",
            "headers": [(b"cookie", f"pywry_session={session_id}".encode())],
            "query_string": b"",
        }

        await middleware(scope, None, None)

        assert captured_session["session"] is not None
        assert captured_session["session"].user_id == "cookie-user"

    @pytest.mark.asyncio
    async def test_middleware_extracts_session_from_bearer_token(
        self, session_store, auth_secret: str
    ) -> None:
        """Test middleware extracts session from Authorization header."""
        user_id = f"bearer-test-{uuid.uuid4().hex[:8]}"
        session_id = f"bearer-session-{uuid.uuid4().hex[:8]}"

        await session_store.create_session(session_id, user_id, roles=["admin"])

        token = generate_session_token(user_id, auth_secret)

        config = AuthConfig(
            enabled=True,
            token_secret=auth_secret,
            auth_header="authorization",  # Use lowercase to match ASGI header format
        )

        captured_session = {}

        async def mock_app(scope, receive, send):
            captured_session["session"] = scope.get("session")

        middleware = AuthMiddleware(mock_app, session_store, config)

        # ASGI headers are list of (name, value) tuples with lowercase names
        scope = {
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
            "query_string": b"",
        }

        await middleware(scope, None, None)

        assert captured_session["session"] is not None
        assert captured_session["session"].user_id == user_id

    @pytest.mark.asyncio
    async def test_middleware_websocket_query_param_auth(self, session_store) -> None:
        """Test middleware extracts session from WebSocket query param."""
        session_id = f"ws-session-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(session_id, "ws-user", roles=["viewer"])

        config = AuthConfig(enabled=True, token_secret="test-secret")

        captured_session = {}

        async def mock_app(scope, receive, send):
            captured_session["session"] = scope.get("session")

        middleware = AuthMiddleware(mock_app, session_store, config)

        scope = {
            "type": "websocket",
            "headers": [],
            "query_string": f"session={session_id}".encode(),
        }

        await middleware(scope, None, None)

        assert captured_session["session"] is not None
        assert captured_session["session"].session_id == session_id

    @pytest.mark.asyncio
    async def test_middleware_disabled_skips_auth(self, session_store) -> None:
        """Test middleware skips auth when disabled."""
        config = AuthConfig(enabled=False)

        captured_session = {}

        async def mock_app(scope, receive, send):
            captured_session["session"] = scope.get("session")

        middleware = AuthMiddleware(mock_app, session_store, config)

        scope = {
            "type": "http",
            "headers": [],
            "query_string": b"",
        }

        await middleware(scope, None, None)

        # Session should be None when auth is disabled
        assert captured_session["session"] is None


# ============================================================================
# PART 8: Dashboard Access Control Scenarios
# ============================================================================


class TestDashboardAccessScenarios:
    """Real-world dashboard access control scenarios."""

    @pytest.mark.asyncio
    async def test_multi_tenant_dashboard_isolation(self, widget_store, session_store) -> None:
        """Test dashboards are isolated between tenants."""
        # Create tenant A and B with their own dashboards
        tenant_a_session = f"tenant-a-{uuid.uuid4().hex[:8]}"
        tenant_b_session = f"tenant-b-{uuid.uuid4().hex[:8]}"

        await session_store.create_session(
            tenant_a_session,
            "user@tenant-a.com",
            metadata={
                "permissions": {
                    "widget:tenant-a-dashboard": ["read", "write"],
                }
            },
        )
        await session_store.create_session(
            tenant_b_session,
            "user@tenant-b.com",
            metadata={
                "permissions": {
                    "widget:tenant-b-dashboard": ["read", "write"],
                }
            },
        )

        # Tenant A can access their dashboard
        assert await session_store.check_permission(
            tenant_a_session, "widget", "tenant-a-dashboard", "read"
        )

        # Tenant A cannot access Tenant B's dashboard
        assert not await session_store.check_permission(
            tenant_a_session, "widget", "tenant-b-dashboard", "read"
        )

        # And vice versa
        assert await session_store.check_permission(
            tenant_b_session, "widget", "tenant-b-dashboard", "read"
        )
        assert not await session_store.check_permission(
            tenant_b_session, "widget", "tenant-a-dashboard", "read"
        )

    @pytest.mark.asyncio
    async def test_shared_dashboard_multiple_users(self, widget_store, session_store) -> None:
        """Test multiple users can access shared dashboards."""
        # Create a shared dashboard
        shared_widget_id = f"shared-{uuid.uuid4().hex[:8]}"
        await widget_store.register(
            widget_id=shared_widget_id,
            html="<div>Shared Analytics Dashboard</div>",
            owner_worker_id="worker-main",
        )

        # Configure roles
        await session_store.set_role_permissions("analyst", {"read"})
        await session_store.set_role_permissions("data_scientist", {"read", "write"})

        # Create multiple users with different roles
        sessions = {}
        for i, role in enumerate(["analyst", "analyst", "data_scientist"]):
            sid = f"user-{i}-{uuid.uuid4().hex[:8]}"
            await session_store.create_session(sid, f"user-{i}@corp.com", roles=[role])
            sessions[f"user_{i}"] = sid

        # All can read
        for name, sid in sessions.items():
            assert await session_store.check_permission(sid, "widget", shared_widget_id, "read"), (
                f"{name} should be able to read"
            )

        # Only data scientist can write
        assert not await session_store.check_permission(
            sessions["user_0"], "widget", shared_widget_id, "write"
        )
        assert await session_store.check_permission(
            sessions["user_2"], "widget", shared_widget_id, "write"
        )

    @pytest.mark.asyncio
    async def test_admin_user_has_override_access(self, widget_store, session_store) -> None:
        """Test admin users can access all dashboards."""
        # Configure admin with full access
        await session_store.set_role_permissions(
            "admin",
            {"read", "write", "delete", "admin", "manage_users"},
        )

        admin_session = f"super-admin-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(
            admin_session,
            "admin@platform.com",
            roles=["admin"],
        )

        # Create various widgets from different "tenants"
        for tenant in ["alpha", "beta", "gamma"]:
            await widget_store.register(
                widget_id=f"tenant-{tenant}-widget",
                html=f"<div>{tenant.upper()} Dashboard</div>",
                owner_worker_id="worker-main",
            )

        # Admin can access all
        for tenant in ["alpha", "beta", "gamma"]:
            assert await session_store.check_permission(
                admin_session,
                "widget",
                f"tenant-{tenant}-widget",
                "read",
            )
            assert await session_store.check_permission(
                admin_session,
                "widget",
                f"tenant-{tenant}-widget",
                "write",
            )
            assert await session_store.check_permission(
                admin_session,
                "widget",
                f"tenant-{tenant}-widget",
                "delete",
            )

    @pytest.mark.asyncio
    async def test_anonymous_user_no_access(self, session_store) -> None:
        """Test anonymous users have no access."""
        await session_store.set_role_permissions("anonymous", set())

        anon_session = f"anon-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(anon_session, "anonymous", roles=["anonymous"])

        # No access to any resource
        assert not await session_store.check_permission(
            anon_session, "widget", "any-widget", "read"
        )
        assert not await session_store.check_permission(anon_session, "system", "config", "read")


# ============================================================================
# PART 9: Concurrent Access and Race Condition Tests
# ============================================================================


class TestConcurrentAccessDeployMode:
    """Tests for concurrent access patterns in deploy mode."""

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, session_store) -> None:
        """Test concurrent session creation is handled correctly."""
        user_id = f"concurrent-user-{uuid.uuid4().hex[:8]}"

        async def create_session(i: int):
            session_id = f"concurrent-sess-{i}-{uuid.uuid4().hex[:8]}"
            await session_store.create_session(session_id, user_id, roles=["viewer"])
            return session_id

        # Create 10 sessions concurrently
        session_ids = await asyncio.gather(*[create_session(i) for i in range(10)])

        # All sessions should exist
        sessions = await session_store.list_user_sessions(user_id)
        assert len(sessions) == 10
        assert {s.session_id for s in sessions} == set(session_ids)

    @pytest.mark.asyncio
    async def test_concurrent_permission_checks(self, session_store) -> None:
        """Test concurrent permission checks don't cause issues."""
        await session_store.set_role_permissions("editor", {"read", "write"})

        session_id = f"concurrent-perm-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(session_id, "perm-user", roles=["editor"])

        async def check_perm(resource_id: str):
            return await session_store.check_permission(session_id, "widget", resource_id, "read")

        # Check permissions for 50 different resources concurrently
        results = await asyncio.gather(*[check_perm(f"widget-{i}") for i in range(50)])

        # All should succeed
        assert all(results)

    @pytest.mark.asyncio
    async def test_concurrent_widget_registration(self, widget_store) -> None:
        """Test concurrent widget registration is handled correctly."""

        async def register_widget(i: int):
            widget_id = f"concurrent-widget-{i}-{uuid.uuid4().hex[:8]}"
            await widget_store.register(
                widget_id=widget_id,
                html=f"<div>Widget {i}</div>",
                owner_worker_id=f"worker-{i % 3}",
            )
            return widget_id

        # Register 20 widgets concurrently
        widget_ids = await asyncio.gather(*[register_widget(i) for i in range(20)])

        # All widgets should exist
        for wid in widget_ids:
            exists = await widget_store.exists(wid)
            assert exists, f"Widget {wid} should exist"

    @pytest.mark.asyncio
    async def test_session_refresh_under_load(self, session_store) -> None:
        """Test session refresh works correctly under concurrent load."""
        session_id = f"refresh-load-{uuid.uuid4().hex[:8]}"
        await session_store.create_session(session_id, "load-user", ttl=60)

        async def refresh():
            return await session_store.refresh_session(session_id)

        # Refresh 20 times concurrently
        results = await asyncio.gather(*[refresh() for _ in range(20)])

        # All refreshes should succeed
        assert all(results)

        # Session should still be valid
        assert await session_store.validate_session(session_id)
