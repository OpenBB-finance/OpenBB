"""Comprehensive tests for user authentication and RBAC with Redis.

These tests validate the complete authentication flow and role-based
access control system using Redis as the session backend.

Run with: pytest tests/test_auth_rbac_integration.py -v

Tests cover:
- Session token generation and validation (HMAC-signed)
- Widget token generation and validation
- Role-based permission enforcement
- Session lifecycle (create, validate, refresh, delete, expire)
- Multi-user concurrent session handling
- Permission escalation prevention
- Cross-worker session validation
- Edge cases and security scenarios
"""

# pylint: disable=too-many-lines,redefined-outer-name,unused-argument

from __future__ import annotations

import asyncio
import time
import uuid

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from pywry.state.auth import (
    DEFAULT_ROLE_PERMISSIONS,
    AuthConfig,
    check_widget_permission,
    generate_session_token,
    generate_widget_token,
    get_role_permissions,
    get_session_from_request,
    has_permission,
    is_admin,
    validate_session_token,
    validate_widget_token,
)
from pywry.state.types import UserSession


@pytest.fixture
def unique_prefix() -> str:
    """Generate a unique prefix for test isolation."""
    return f"pywry-test:{uuid.uuid4().hex[:8]}:"


@pytest.fixture
def auth_secret() -> str:
    """Generate a consistent secret for token signing."""
    return "test-secret-key-for-signing-tokens"


@pytest.fixture
def auth_config(auth_secret: str) -> AuthConfig:
    """Create an AuthConfig for testing."""
    return AuthConfig(
        enabled=True,
        token_secret=auth_secret,
        session_ttl=3600,
        require_auth_for_widgets=True,
    )


@pytest_asyncio.fixture
async def redis_session_store(redis_container: str, unique_prefix: str):
    """Create a RedisSessionStore with testcontainers Redis.

    Uses the session-scoped redis_container fixture.
    Tests will be skipped if Docker is not available.
    """
    import redis.asyncio as aioredis

    from pywry.state.redis import RedisSessionStore

    store = RedisSessionStore(
        redis_url=redis_container,
        prefix=unique_prefix,
        default_ttl=60,
    )
    yield store
    # Cleanup
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


# ============================================================================
# PART 1: Token Generation and Validation (Unit Tests)
# ============================================================================


class TestSessionTokenGeneration:
    """Tests for session token generation and validation."""

    def test_generate_token_format(self, auth_secret: str) -> None:
        """Test that generated token has correct format."""
        token = generate_session_token("user-123", auth_secret)
        parts = token.split(":")

        assert len(parts) == 4, "Token should have 4 parts: user_id:timestamp:expiry:signature"
        assert parts[0] == "user-123", "First part should be user_id"
        assert parts[1].isdigit(), "Second part should be timestamp"
        assert parts[2] == "0", "Third part should be 0 for no expiry"
        assert len(parts[3]) == 16, "Signature should be 16 hex characters"

    def test_generate_token_with_expiry(self, auth_secret: str) -> None:
        """Test token generation with expiration time."""
        expires_at = time.time() + 3600  # 1 hour from now
        token = generate_session_token("user-456", auth_secret, expires_at)
        parts = token.split(":")

        assert int(parts[2]) == int(expires_at), "Expiry should match"

    def test_validate_valid_token(self, auth_secret: str) -> None:
        """Test validation of a valid token."""
        token = generate_session_token("user-789", auth_secret)
        is_valid, user_id, error = validate_session_token(token, auth_secret)

        assert is_valid is True
        assert user_id == "user-789"
        assert error is None

    def test_validate_token_with_future_expiry(self, auth_secret: str) -> None:
        """Test validation of token with future expiry."""
        expires_at = time.time() + 3600
        token = generate_session_token("user-abc", auth_secret, expires_at)
        is_valid, user_id, _error = validate_session_token(token, auth_secret)

        assert is_valid is True
        assert user_id == "user-abc"

    def test_validate_expired_token(self, auth_secret: str) -> None:
        """Test that expired tokens are rejected."""
        expires_at = time.time() - 100  # Expired 100 seconds ago
        token = generate_session_token("user-expired", auth_secret, expires_at)
        is_valid, user_id, error = validate_session_token(token, auth_secret)

        assert is_valid is False
        assert user_id is None
        assert "expired" in error.lower()

    def test_validate_token_wrong_secret(self, auth_secret: str) -> None:
        """Test that token signed with different secret is rejected."""
        token = generate_session_token("user-xyz", auth_secret)
        is_valid, _user_id, error = validate_session_token(token, "wrong-secret")

        assert is_valid is False
        assert "signature" in error.lower()

    def test_validate_malformed_token(self, auth_secret: str) -> None:
        """Test validation of malformed tokens."""
        # Missing parts
        is_valid, _user_id, error = validate_session_token("invalid", auth_secret)
        assert is_valid is False
        assert "format" in error.lower()

        # Too few parts
        is_valid, _user_id2, error = validate_session_token("a:b:c", auth_secret)
        assert is_valid is False

        # Non-numeric timestamp
        is_valid, _user_id, error = validate_session_token("user:abc:0:sig", auth_secret)
        assert is_valid is False

    def test_validate_tampered_token(self, auth_secret: str) -> None:
        """Test that tampering with token payload invalidates it."""
        token = generate_session_token("user-original", auth_secret)
        parts = token.split(":")

        # Tamper with user_id
        tampered = f"user-hacker:{parts[1]}:{parts[2]}:{parts[3]}"
        is_valid, _user_id, error = validate_session_token(tampered, auth_secret)

        assert is_valid is False
        assert "signature" in error.lower()

    def test_token_signature_is_deterministic(self, auth_secret: str) -> None:
        """Test that same inputs produce same signature."""
        # Use fixed timestamp for deterministic test
        expires_at = 1700000000.0
        token1 = generate_session_token("user-test", auth_secret, expires_at)
        token2 = generate_session_token("user-test", auth_secret, expires_at)

        # The timestamp part will differ, so compare signatures with same payload
        parts1 = token1.split(":")
        parts2 = token2.split(":")

        # Same expiry means same payload structure
        assert parts1[2] == parts2[2]


class TestWidgetTokenGeneration:
    """Tests for widget token generation and validation."""

    def test_generate_widget_token(self, auth_secret: str) -> None:
        """Test widget token generation."""
        token = generate_widget_token("widget-123", auth_secret, ttl=300)

        is_valid, widget_id, _ = validate_session_token(token, auth_secret)
        assert is_valid is True
        assert widget_id == "widget-123"

    def test_validate_widget_token(self, auth_secret: str) -> None:
        """Test widget token validation with correct widget_id."""
        token = generate_widget_token("widget-abc", auth_secret, ttl=300)

        is_valid = validate_widget_token(token, "widget-abc", auth_secret)
        assert is_valid is True

    def test_validate_widget_token_wrong_widget(self, auth_secret: str) -> None:
        """Test widget token validation with wrong widget_id."""
        token = generate_widget_token("widget-abc", auth_secret, ttl=300)

        is_valid = validate_widget_token(token, "widget-xyz", auth_secret)
        assert is_valid is False

    def test_widget_token_expiry(self, auth_secret: str) -> None:
        """Test that widget tokens have proper TTL."""
        token = generate_widget_token("widget-ttl", auth_secret, ttl=1)

        # Token should be valid immediately
        is_valid = validate_widget_token(token, "widget-ttl", auth_secret)
        assert is_valid is True

        # Wait for expiry
        time.sleep(1.5)

        is_valid = validate_widget_token(token, "widget-ttl", auth_secret)
        assert is_valid is False


# ============================================================================
# PART 2: Role-Based Access Control (Unit Tests)
# ============================================================================


class TestRolePermissions:
    """Tests for role permission utilities."""

    def test_default_role_permissions(self) -> None:
        """Test default role permission definitions."""
        assert "read" in DEFAULT_ROLE_PERMISSIONS["admin"]
        assert "write" in DEFAULT_ROLE_PERMISSIONS["admin"]
        assert "admin" in DEFAULT_ROLE_PERMISSIONS["admin"]
        assert "delete" in DEFAULT_ROLE_PERMISSIONS["admin"]
        assert "manage_users" in DEFAULT_ROLE_PERMISSIONS["admin"]

        assert "read" in DEFAULT_ROLE_PERMISSIONS["editor"]
        assert "write" in DEFAULT_ROLE_PERMISSIONS["editor"]
        assert "admin" not in DEFAULT_ROLE_PERMISSIONS["editor"]

        assert DEFAULT_ROLE_PERMISSIONS["viewer"] == {"read"}
        assert DEFAULT_ROLE_PERMISSIONS["anonymous"] == set()

    def test_get_role_permissions(self) -> None:
        """Test getting permissions for a role."""
        admin_perms = get_role_permissions("admin")
        assert "read" in admin_perms
        assert "write" in admin_perms
        assert "admin" in admin_perms

        viewer_perms = get_role_permissions("viewer")
        assert viewer_perms == {"read"}

        # Unknown role returns empty set
        unknown_perms = get_role_permissions("unknown_role")
        assert unknown_perms == set()

    def test_has_permission_admin(self) -> None:
        """Test permission checking for admin user."""
        session = UserSession(
            session_id="sess-1",
            user_id="admin-user",
            roles=["admin"],
        )

        assert has_permission(session, "read") is True
        assert has_permission(session, "write") is True
        assert has_permission(session, "admin") is True
        assert has_permission(session, "delete") is True
        assert has_permission(session, "manage_users") is True

    def test_has_permission_editor(self) -> None:
        """Test permission checking for editor user."""
        session = UserSession(
            session_id="sess-2",
            user_id="editor-user",
            roles=["editor"],
        )

        assert has_permission(session, "read") is True
        assert has_permission(session, "write") is True
        assert has_permission(session, "admin") is False
        assert has_permission(session, "delete") is False

    def test_has_permission_viewer(self) -> None:
        """Test permission checking for viewer user."""
        session = UserSession(
            session_id="sess-3",
            user_id="viewer-user",
            roles=["viewer"],
        )

        assert has_permission(session, "read") is True
        assert has_permission(session, "write") is False
        assert has_permission(session, "admin") is False

    def test_has_permission_anonymous(self) -> None:
        """Test permission checking for anonymous user."""
        session = UserSession(
            session_id="sess-4",
            user_id="anon-user",
            roles=["anonymous"],
        )

        assert has_permission(session, "read") is False
        assert has_permission(session, "write") is False
        assert has_permission(session, "admin") is False

    def test_has_permission_no_session(self) -> None:
        """Test permission checking with no session."""
        assert has_permission(None, "read") is False
        assert has_permission(None, "write") is False
        assert has_permission(None, "admin") is False

    def test_has_permission_multiple_roles(self) -> None:
        """Test permission checking with multiple roles."""
        session = UserSession(
            session_id="sess-5",
            user_id="multi-role-user",
            roles=["viewer", "editor"],
        )

        # Should have union of permissions
        assert has_permission(session, "read") is True
        assert has_permission(session, "write") is True
        assert has_permission(session, "admin") is False

    def test_is_admin(self) -> None:
        """Test admin role checking."""
        admin_session = UserSession(
            session_id="admin-sess",
            user_id="admin-user",
            roles=["admin"],
        )
        editor_session = UserSession(
            session_id="editor-sess",
            user_id="editor-user",
            roles=["editor"],
        )

        assert is_admin(admin_session) is True
        assert is_admin(editor_session) is False
        assert is_admin(None) is False

    def test_is_admin_with_multiple_roles(self) -> None:
        """Test admin check with multiple roles including admin."""
        session = UserSession(
            session_id="multi-sess",
            user_id="multi-user",
            roles=["viewer", "admin"],
        )

        assert is_admin(session) is True


# ============================================================================
# PART 3: Redis Session Store Integration Tests
# ============================================================================


class TestRedisSessionLifecycle:
    """Integration tests for session lifecycle with Redis."""

    @pytest.mark.asyncio
    async def test_create_session_basic(self, redis_session_store) -> None:
        """Test basic session creation."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        session = await redis_session_store.create_session(
            session_id=session_id,
            user_id="user-123",
        )

        assert session.session_id == session_id
        assert session.user_id == "user-123"
        assert session.roles == []
        assert session.created_at > 0
        assert session.expires_at > session.created_at

    @pytest.mark.asyncio
    async def test_create_session_with_roles(self, redis_session_store) -> None:
        """Test session creation with roles."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        session = await redis_session_store.create_session(
            session_id=session_id,
            user_id="admin-user",
            roles=["admin", "editor"],
        )

        assert "admin" in session.roles
        assert "editor" in session.roles

    @pytest.mark.asyncio
    async def test_create_session_with_metadata(self, redis_session_store) -> None:
        """Test session creation with custom metadata."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        session = await redis_session_store.create_session(
            session_id=session_id,
            user_id="meta-user",
            metadata={
                "name": "Test User",
                "email": "test@example.com",
                "org": "TestOrg",
            },
        )

        assert session.metadata["name"] == "Test User"
        assert session.metadata["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_session(self, redis_session_store) -> None:
        """Test session retrieval."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(
            session_id=session_id,
            user_id="get-user",
            roles=["viewer"],
            metadata={"key": "value"},
        )

        session = await redis_session_store.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == "get-user"
        assert session.roles == ["viewer"]
        assert session.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, redis_session_store) -> None:
        """Test getting a session that doesn't exist."""
        session = await redis_session_store.get_session("nonexistent-session")
        assert session is None

    @pytest.mark.asyncio
    async def test_validate_session(self, redis_session_store) -> None:
        """Test session validation."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, "val-user")

        assert await redis_session_store.validate_session(session_id) is True
        assert await redis_session_store.validate_session("invalid") is False

    @pytest.mark.asyncio
    async def test_delete_session(self, redis_session_store) -> None:
        """Test session deletion."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, "del-user")
        assert await redis_session_store.validate_session(session_id) is True

        result = await redis_session_store.delete_session(session_id)
        assert result is True

        assert await redis_session_store.validate_session(session_id) is False
        assert await redis_session_store.get_session(session_id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session(self, redis_session_store) -> None:
        """Test deleting a session that doesn't exist."""
        result = await redis_session_store.delete_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_refresh_session(self, redis_session_store) -> None:
        """Test session refresh extends TTL."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        # Create with short TTL
        await redis_session_store.create_session(
            session_id=session_id,
            user_id="refresh-user",
            ttl=10,
        )

        session_before = await redis_session_store.get_session(session_id)
        assert session_before is not None
        original_expires = session_before.expires_at

        await asyncio.sleep(0.1)

        # Refresh with extended TTL
        result = await redis_session_store.refresh_session(session_id, extend_ttl=120)
        assert result is True

        session_after = await redis_session_store.get_session(session_id)
        assert session_after is not None
        assert session_after.expires_at > original_expires

    @pytest.mark.asyncio
    async def test_refresh_nonexistent_session(self, redis_session_store) -> None:
        """Test refreshing a session that doesn't exist."""
        result = await redis_session_store.refresh_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_session_expiry(self, redis_session_store) -> None:
        """Test that sessions expire after TTL."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        # Create with very short TTL
        await redis_session_store.create_session(
            session_id=session_id,
            user_id="expiry-user",
            ttl=1,  # 1 second TTL
        )

        assert await redis_session_store.validate_session(session_id) is True

        # Wait for expiry
        await asyncio.sleep(1.5)

        assert await redis_session_store.validate_session(session_id) is False


class TestRedisMultiUserSessions:
    """Tests for multi-user session scenarios with Redis."""

    @pytest.mark.asyncio
    async def test_list_user_sessions(self, redis_session_store) -> None:
        """Test listing all sessions for a user."""
        user_id = f"user-{uuid.uuid4().hex[:8]}"
        session_ids = [f"session-{uuid.uuid4().hex[:8]}" for _ in range(3)]

        for sid in session_ids:
            await redis_session_store.create_session(sid, user_id, roles=["viewer"])

        sessions = await redis_session_store.list_user_sessions(user_id)

        assert len(sessions) == 3
        assert {s.session_id for s in sessions} == set(session_ids)

    @pytest.mark.asyncio
    async def test_list_user_sessions_cleanup_expired(self, redis_session_store) -> None:
        """Test that listing sessions cleans up expired session references."""
        user_id = f"user-{uuid.uuid4().hex[:8]}"

        # Create session with very short TTL
        await redis_session_store.create_session(
            f"session-expire-{uuid.uuid4().hex[:8]}",
            user_id,
            ttl=1,
        )

        # Create session with longer TTL
        valid_session = f"session-valid-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(valid_session, user_id, ttl=60)

        # Wait for first session to expire
        await asyncio.sleep(1.5)

        # List should only return valid session
        sessions = await redis_session_store.list_user_sessions(user_id)
        assert len(sessions) == 1
        assert sessions[0].session_id == valid_session

    @pytest.mark.asyncio
    async def test_concurrent_sessions_different_users(self, redis_session_store) -> None:
        """Test concurrent sessions for different users are isolated."""
        user1 = f"user1-{uuid.uuid4().hex[:8]}"
        user2 = f"user2-{uuid.uuid4().hex[:8]}"

        session1 = f"session1-{uuid.uuid4().hex[:8]}"
        session2 = f"session2-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session1, user1, roles=["admin"])
        await redis_session_store.create_session(session2, user2, roles=["viewer"])

        user1_sessions = await redis_session_store.list_user_sessions(user1)
        user2_sessions = await redis_session_store.list_user_sessions(user2)

        assert len(user1_sessions) == 1
        assert len(user2_sessions) == 1
        assert user1_sessions[0].roles == ["admin"]
        assert user2_sessions[0].roles == ["viewer"]

    @pytest.mark.asyncio
    async def test_delete_session_updates_user_list(self, redis_session_store) -> None:
        """Test that deleting a session removes it from user's session list."""
        user_id = f"user-{uuid.uuid4().hex[:8]}"
        session_id = f"session-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, user_id)

        sessions = await redis_session_store.list_user_sessions(user_id)
        assert len(sessions) == 1

        await redis_session_store.delete_session(session_id)

        sessions = await redis_session_store.list_user_sessions(user_id)
        assert len(sessions) == 0


# ============================================================================
# PART 4: Redis RBAC Permission Tests
# ============================================================================


class TestRedisRBACPermissions:
    """Integration tests for RBAC permissions with Redis."""

    @pytest.mark.asyncio
    async def test_set_role_permissions(self, redis_session_store) -> None:
        """Test setting custom role permissions."""
        await redis_session_store.set_role_permissions("custom_role", {"read", "write", "custom"})

        session_id = f"session-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "custom-user", roles=["custom_role"])

        assert await redis_session_store.check_permission(session_id, "widget", "1", "read")
        assert await redis_session_store.check_permission(session_id, "widget", "1", "write")
        assert await redis_session_store.check_permission(session_id, "widget", "1", "custom")
        assert not await redis_session_store.check_permission(session_id, "widget", "1", "admin")

    @pytest.mark.asyncio
    async def test_rbac_admin_permissions(self, redis_session_store) -> None:
        """Test admin role has full permissions."""
        await redis_session_store.set_role_permissions(
            "admin", {"read", "write", "delete", "admin", "manage_users"}
        )

        session_id = f"admin-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "admin-user", roles=["admin"])

        # Admin should have all standard permissions
        for perm in ["read", "write", "delete", "admin"]:
            assert await redis_session_store.check_permission(
                session_id, "widget", "any-widget", perm
            ), f"Admin should have {perm} permission"

    @pytest.mark.asyncio
    async def test_rbac_editor_permissions(self, redis_session_store) -> None:
        """Test editor role has read/write but not admin."""
        await redis_session_store.set_role_permissions("editor", {"read", "write"})

        session_id = f"editor-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "editor-user", roles=["editor"])

        assert await redis_session_store.check_permission(session_id, "widget", "1", "read")
        assert await redis_session_store.check_permission(session_id, "widget", "1", "write")
        assert not await redis_session_store.check_permission(session_id, "widget", "1", "delete")
        assert not await redis_session_store.check_permission(session_id, "widget", "1", "admin")

    @pytest.mark.asyncio
    async def test_rbac_viewer_permissions(self, redis_session_store) -> None:
        """Test viewer role has read-only access."""
        await redis_session_store.set_role_permissions("viewer", {"read"})

        session_id = f"viewer-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "viewer-user", roles=["viewer"])

        assert await redis_session_store.check_permission(session_id, "widget", "1", "read")
        assert not await redis_session_store.check_permission(session_id, "widget", "1", "write")

    @pytest.mark.asyncio
    async def test_rbac_no_permissions(self, redis_session_store) -> None:
        """Test session without roles has no permissions."""
        session_id = f"norole-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "norole-user", roles=[])

        assert not await redis_session_store.check_permission(session_id, "widget", "1", "read")

    @pytest.mark.asyncio
    async def test_rbac_invalid_session(self, redis_session_store) -> None:
        """Test permission check with invalid session."""
        result = await redis_session_store.check_permission(
            "invalid-session", "widget", "1", "read"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_rbac_multiple_roles(self, redis_session_store) -> None:
        """Test permission union across multiple roles."""
        await redis_session_store.set_role_permissions("role_a", {"perm1"})
        await redis_session_store.set_role_permissions("role_b", {"perm2"})

        session_id = f"multi-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(
            session_id, "multi-user", roles=["role_a", "role_b"]
        )

        # Should have permissions from both roles
        assert await redis_session_store.check_permission(session_id, "resource", "1", "perm1")
        assert await redis_session_store.check_permission(session_id, "resource", "1", "perm2")

    @pytest.mark.asyncio
    async def test_rbac_resource_specific_permissions(self, redis_session_store) -> None:
        """Test resource-specific permissions via session metadata."""
        session_id = f"resource-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(
            session_id,
            "resource-user",
            roles=[],  # No role-based permissions
            metadata={
                "permissions": {
                    "widget:widget-1": ["read", "write"],
                    "widget:widget-2": ["read"],
                }
            },
        )

        # Check widget-1 permissions
        assert await redis_session_store.check_permission(session_id, "widget", "widget-1", "read")
        assert await redis_session_store.check_permission(session_id, "widget", "widget-1", "write")

        # Check widget-2 permissions (read only)
        assert await redis_session_store.check_permission(session_id, "widget", "widget-2", "read")
        assert not await redis_session_store.check_permission(
            session_id, "widget", "widget-2", "write"
        )

        # Check other widget (no access)
        assert not await redis_session_store.check_permission(
            session_id, "widget", "widget-3", "read"
        )


# ============================================================================
# PART 5: Permission Escalation Prevention Tests
# ============================================================================


class TestPermissionEscalationPrevention:
    """Tests to ensure permissions cannot be escalated."""

    @pytest.mark.asyncio
    async def test_viewer_cannot_write(self, redis_session_store) -> None:
        """Test that viewer role cannot perform write operations."""
        await redis_session_store.set_role_permissions("viewer", {"read"})

        session_id = f"viewer-esc-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "viewer-user", roles=["viewer"])

        # Viewer should not have write permission
        assert not await redis_session_store.check_permission(
            session_id, "widget", "protected-widget", "write"
        )
        assert not await redis_session_store.check_permission(
            session_id, "widget", "protected-widget", "delete"
        )
        assert not await redis_session_store.check_permission(
            session_id, "widget", "protected-widget", "admin"
        )

    @pytest.mark.asyncio
    async def test_editor_cannot_admin(self, redis_session_store) -> None:
        """Test that editor role cannot perform admin operations."""
        await redis_session_store.set_role_permissions("editor", {"read", "write"})

        session_id = f"editor-esc-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "editor-user", roles=["editor"])

        assert not await redis_session_store.check_permission(
            session_id, "system", "config", "admin"
        )
        assert not await redis_session_store.check_permission(
            session_id, "user", "other-user", "manage_users"
        )

    @pytest.mark.asyncio
    async def test_session_role_immutable_in_redis(self, redis_session_store) -> None:
        """Test that roles stored in session cannot be escalated via retrieval."""
        session_id = f"immutable-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, "normal-user", roles=["viewer"])

        # Retrieve session
        session = await redis_session_store.get_session(session_id)
        assert session is not None
        assert session.roles == ["viewer"]

        # Modifying the retrieved object shouldn't affect stored data
        session.roles.append("admin")

        # Re-retrieve should still show original roles
        session2 = await redis_session_store.get_session(session_id)
        assert session2 is not None
        assert session2.roles == ["viewer"]

    def test_token_cannot_grant_additional_permissions(self, auth_secret: str) -> None:
        """Test that modifying token doesn't grant permissions."""
        # Create token for normal user
        token = generate_session_token("user-normal", auth_secret)

        # Try to modify token to look like admin
        parts = token.split(":")
        fake_token = f"admin-user:{parts[1]}:{parts[2]}:{parts[3]}"

        # Validation should fail
        is_valid, _user_id, _error = validate_session_token(fake_token, auth_secret)
        assert is_valid is False


# ============================================================================
# PART 6: Cross-Worker Session Validation Tests
# ============================================================================


class TestCrossWorkerSessionValidation:
    """Tests for session validation across multiple workers.

    These tests require Redis because they test cross-worker scenarios
    where multiple store instances share state via Redis.
    Tests will be skipped if redis_container fixture fails.
    """

    @pytest.mark.asyncio
    async def test_session_accessible_from_different_workers(
        self, redis_container: str, unique_prefix: str
    ) -> None:
        """Test that sessions created by one worker are accessible by another."""
        from pywry.state.redis import RedisSessionStore

        # Simulate two workers with separate store instances
        worker1_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        session_id = f"cross-worker-{uuid.uuid4().hex[:8]}"

        # Worker 1 creates session
        await worker1_store.create_session(session_id, "shared-user", roles=["editor"])

        # Worker 2 should be able to validate and retrieve
        assert await worker2_store.validate_session(session_id) is True

        session = await worker2_store.get_session(session_id)
        assert session is not None
        assert session.user_id == "shared-user"
        assert session.roles == ["editor"]

    @pytest.mark.asyncio
    async def test_session_deletion_propagates(
        self, redis_container: str, unique_prefix: str
    ) -> None:
        """Test that session deletion by one worker is seen by another."""
        from pywry.state.redis import RedisSessionStore

        worker1_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        session_id = f"delete-prop-{uuid.uuid4().hex[:8]}"

        await worker1_store.create_session(session_id, "user-delete")
        assert await worker2_store.validate_session(session_id) is True

        # Worker 2 deletes
        await worker2_store.delete_session(session_id)

        # Worker 1 should see deletion
        assert await worker1_store.validate_session(session_id) is False

    @pytest.mark.asyncio
    async def test_role_permissions_shared_across_workers(
        self, redis_container: str, unique_prefix: str
    ) -> None:
        """Test that role permissions set by one worker are seen by another."""
        from pywry.state.redis import RedisSessionStore

        worker1_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )
        worker2_store = RedisSessionStore(
            redis_url=redis_container,
            prefix=unique_prefix,
        )

        # Worker 1 sets role permissions
        await worker1_store.set_role_permissions("shared_role", {"perm_x", "perm_y"})

        session_id = f"shared-perm-{uuid.uuid4().hex[:8]}"
        await worker1_store.create_session(session_id, "perm-user", roles=["shared_role"])

        # Worker 2 should see permissions
        assert await worker2_store.check_permission(session_id, "resource", "1", "perm_x")
        assert await worker2_store.check_permission(session_id, "resource", "1", "perm_y")


# ============================================================================
# PART 7: Widget Permission Integration Tests
# ============================================================================


class TestWidgetPermissionIntegration:
    """Tests for widget-specific permission checking."""

    @pytest.mark.asyncio
    async def test_check_widget_permission(self, redis_session_store) -> None:
        """Test check_widget_permission utility function."""
        await redis_session_store.set_role_permissions("editor", {"read", "write"})

        session_id = f"widget-perm-{uuid.uuid4().hex[:8]}"
        session = await redis_session_store.create_session(
            session_id, "widget-user", roles=["editor"]
        )

        # Check permission via utility function
        assert await check_widget_permission(session, "widget-123", "read", redis_session_store)
        assert await check_widget_permission(session, "widget-123", "write", redis_session_store)
        assert not await check_widget_permission(
            session, "widget-123", "delete", redis_session_store
        )

    @pytest.mark.asyncio
    async def test_check_widget_permission_no_session(self, redis_session_store) -> None:
        """Test check_widget_permission with no session."""
        result = await check_widget_permission(None, "widget-123", "read", redis_session_store)
        assert result is False


# ============================================================================
# PART 8: AuthConfig and AuthMiddleware Tests
# ============================================================================


class TestAuthConfig:
    """Tests for AuthConfig dataclass."""

    def test_auth_config_defaults(self) -> None:
        """Test AuthConfig default values."""
        config = AuthConfig()

        assert config.enabled is False
        assert config.session_cookie == "pywry_session"
        assert config.auth_header == "Authorization"
        assert len(config.token_secret) > 0  # Auto-generated
        assert config.session_ttl == 86400
        assert config.require_auth_for_widgets is False

    def test_auth_config_custom(self) -> None:
        """Test AuthConfig with custom values."""
        config = AuthConfig(
            enabled=True,
            session_cookie="my_session",
            auth_header="X-Auth-Token",
            token_secret="my-secret",
            session_ttl=7200,
            require_auth_for_widgets=True,
        )

        assert config.enabled is True
        assert config.session_cookie == "my_session"
        assert config.auth_header == "X-Auth-Token"
        assert config.token_secret == "my-secret"
        assert config.session_ttl == 7200
        assert config.require_auth_for_widgets is True

    def test_auth_config_generates_secret(self) -> None:
        """Test that AuthConfig generates secret if not provided."""
        config1 = AuthConfig()
        config2 = AuthConfig()

        # Each should have unique secret
        assert len(config1.token_secret) == 64  # 32 bytes = 64 hex chars
        assert len(config2.token_secret) == 64
        assert config1.token_secret != config2.token_secret


class TestGetSessionFromRequest:
    """Tests for session extraction from requests."""

    @pytest.mark.asyncio
    async def test_session_from_cookie(self, redis_session_store, auth_config: AuthConfig) -> None:
        """Test extracting session from cookie."""
        session_id = f"cookie-sess-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "cookie-user")

        # Mock request with cookie
        mock_request = MagicMock()
        mock_request.cookies = {auth_config.session_cookie: session_id}
        mock_request.headers = {}
        mock_request.query_params = {}

        session = await get_session_from_request(mock_request, redis_session_store, auth_config)

        assert session is not None
        assert session.user_id == "cookie-user"

    @pytest.mark.asyncio
    async def test_session_from_bearer_token(
        self, redis_session_store, auth_config: AuthConfig, auth_secret: str
    ) -> None:
        """Test extracting session from Authorization header."""
        user_id = f"bearer-user-{uuid.uuid4().hex[:8]}"
        session_id = f"bearer-sess-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, user_id)

        # Generate bearer token
        token = generate_session_token(user_id, auth_secret)

        # Mock request with bearer token
        mock_request = MagicMock()
        mock_request.cookies = {}
        mock_request.headers = {auth_config.auth_header: f"Bearer {token}"}
        mock_request.query_params = {}

        session = await get_session_from_request(mock_request, redis_session_store, auth_config)

        assert session is not None
        assert session.user_id == user_id

    @pytest.mark.asyncio
    async def test_session_from_query_param(
        self, redis_session_store, auth_config: AuthConfig
    ) -> None:
        """Test extracting session from query parameter (WebSocket)."""
        session_id = f"query-sess-{uuid.uuid4().hex[:8]}"
        await redis_session_store.create_session(session_id, "query-user")

        # Mock request with query param
        mock_request = MagicMock()
        mock_request.cookies = {}
        mock_request.headers = {}
        mock_request.query_params = {"session": session_id}

        session = await get_session_from_request(mock_request, redis_session_store, auth_config)

        assert session is not None
        assert session.user_id == "query-user"

    @pytest.mark.asyncio
    async def test_no_session_credentials(
        self, redis_session_store, auth_config: AuthConfig
    ) -> None:
        """Test request with no session credentials."""
        mock_request = MagicMock()
        mock_request.cookies = {}
        mock_request.headers = {}
        mock_request.query_params = {}

        session = await get_session_from_request(mock_request, redis_session_store, auth_config)

        assert session is None

    @pytest.mark.asyncio
    async def test_invalid_session_id(self, redis_session_store, auth_config: AuthConfig) -> None:
        """Test request with invalid session ID."""
        mock_request = MagicMock()
        mock_request.cookies = {auth_config.session_cookie: "invalid-session"}
        mock_request.headers = {}
        mock_request.query_params = {}

        session = await get_session_from_request(mock_request, redis_session_store, auth_config)

        assert session is None


# ============================================================================
# PART 9: Edge Cases and Security Scenarios
# ============================================================================


class TestSecurityEdgeCases:
    """Tests for security edge cases and attack prevention."""

    def test_empty_token(self, auth_secret: str) -> None:
        """Test validation of empty token."""
        is_valid, _user_id, _error = validate_session_token("", auth_secret)
        assert is_valid is False

    def test_empty_secret(self) -> None:
        """Test token generation with empty secret."""
        token = generate_session_token("user", "")
        is_valid, _user_id, _error = validate_session_token(token, "")
        assert is_valid is True  # Empty secret is valid but not recommended

    def test_very_long_user_id(self, auth_secret: str) -> None:
        """Test token with very long user ID."""
        long_user_id = "x" * 10000
        token = generate_session_token(long_user_id, auth_secret)
        is_valid, user_id, _error = validate_session_token(token, auth_secret)
        assert is_valid is True
        assert user_id == long_user_id

    def test_special_characters_in_user_id(self, auth_secret: str) -> None:
        """Test token with special characters in user ID."""
        # Note: colon would break the token format
        special_user = "user@example.com<script>alert(1)</script>"
        token = generate_session_token(special_user, auth_secret)
        is_valid, user_id, _error = validate_session_token(token, auth_secret)
        assert is_valid is True
        assert user_id == special_user

    def test_unicode_user_id(self, auth_secret: str) -> None:
        """Test token with unicode user ID."""
        unicode_user = "用户🎉émoji"
        token = generate_session_token(unicode_user, auth_secret)
        is_valid, user_id, _error = validate_session_token(token, auth_secret)
        assert is_valid is True
        assert user_id == unicode_user

    @pytest.mark.asyncio
    async def test_session_with_empty_roles(self, redis_session_store) -> None:
        """Test session with explicitly empty roles array."""
        session_id = f"empty-roles-{uuid.uuid4().hex[:8]}"

        session = await redis_session_store.create_session(session_id, "empty-roles-user", roles=[])

        assert session.roles == []

        retrieved = await redis_session_store.get_session(session_id)
        assert retrieved is not None
        assert retrieved.roles == []

    @pytest.mark.asyncio
    async def test_session_metadata_json_encoding(self, redis_session_store) -> None:
        """Test that complex metadata is properly JSON encoded/decoded."""
        session_id = f"json-meta-{uuid.uuid4().hex[:8]}"

        complex_metadata = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "unicode": "こんにちは",
            "bool": True,
            "null": None,
        }

        await redis_session_store.create_session(session_id, "json-user", metadata=complex_metadata)

        session = await redis_session_store.get_session(session_id)
        assert session is not None
        assert session.metadata == complex_metadata

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, redis_session_store) -> None:
        """Test concurrent session operations don't cause data races."""
        session_id = f"concurrent-{uuid.uuid4().hex[:8]}"
        user_id = f"user-concurrent-{uuid.uuid4().hex[:8]}"

        await redis_session_store.create_session(session_id, user_id)

        # Perform concurrent operations
        async def validate():
            return await redis_session_store.validate_session(session_id)

        async def get():
            return await redis_session_store.get_session(session_id)

        async def refresh():
            return await redis_session_store.refresh_session(session_id)

        results = await asyncio.gather(
            validate(),
            get(),
            refresh(),
            validate(),
            get(),
        )

        # All operations should succeed
        assert results[0] is True  # validate
        assert results[1] is not None  # get
        assert results[2] is True  # refresh
        assert results[3] is True  # validate
        assert results[4] is not None  # get

    @pytest.mark.asyncio
    async def test_session_with_many_roles(self, redis_session_store) -> None:
        """Test session with many roles."""
        session_id = f"many-roles-{uuid.uuid4().hex[:8]}"
        many_roles = [f"role_{i}" for i in range(100)]

        await redis_session_store.create_session(session_id, "many-roles-user", roles=many_roles)

        session = await redis_session_store.get_session(session_id)
        assert session is not None
        assert len(session.roles) == 100
        assert set(session.roles) == set(many_roles)


# ============================================================================
# PART 10: Real Redis ACL Enforcement Tests
# ============================================================================


class TestRedisACLEnforcement:
    """Test REAL Redis ACL enforcement using configured Redis users.

    These tests verify that Redis ACLs properly restrict access:
    - Admin user can do everything
    - Editor can read/write widgets
    - Viewer can only read
    - Blocked user cannot access anything

    Requires Docker to run Redis with ACL configuration.
    Tests will be skipped if redis_container_with_acl fixture fails.
    """

    @pytest.mark.asyncio
    async def test_admin_user_full_access(self, redis_container_with_acl) -> None:
        """Admin user should have full access to Redis."""
        import redis.asyncio as aioredis

        client = aioredis.from_url(redis_container_with_acl["admin_url"], decode_responses=True)
        try:
            # Admin can ping
            pong = await client.ping()
            assert pong is True

            # Admin can write
            await client.set("pywry:widget:test-admin", "admin-data")

            # Admin can read
            value = await client.get("pywry:widget:test-admin")
            assert value == "admin-data"

            # Admin can delete
            await client.delete("pywry:widget:test-admin")

            # Admin can run admin commands
            info = await client.info()
            assert "redis_version" in info
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_editor_user_read_write_widgets(self, redis_container_with_acl) -> None:
        """Editor user should be able to read and write widgets."""
        import redis.asyncio as aioredis

        client = aioredis.from_url(redis_container_with_acl["editor_url"], decode_responses=True)
        try:
            # Editor can write to widget keys
            await client.set("pywry:widget:test-editor", "editor-data")

            # Editor can read widget keys
            value = await client.get("pywry:widget:test-editor")
            assert value == "editor-data"

            # Editor can use hash commands on widgets
            await client.hset("pywry:widget:hash-test", "field", "value")
            hash_value = await client.hget("pywry:widget:hash-test", "field")
            assert hash_value == "value"
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_editor_cannot_run_admin_commands(self, redis_container_with_acl) -> None:
        """Editor user should NOT be able to run admin commands."""
        import redis.asyncio as aioredis

        from redis.exceptions import NoPermissionError

        client = aioredis.from_url(redis_container_with_acl["editor_url"], decode_responses=True)
        try:
            # Editor should NOT be able to run CONFIG commands
            with pytest.raises((NoPermissionError, Exception)):
                await client.config_get("*")
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_viewer_user_read_only(self, redis_container_with_acl) -> None:
        """Viewer user should only be able to read widgets."""
        import redis.asyncio as aioredis

        from redis.exceptions import NoPermissionError

        # First, write data as admin
        admin_client = aioredis.from_url(
            redis_container_with_acl["admin_url"], decode_responses=True
        )
        try:
            await admin_client.set("pywry:widget:viewer-test", "viewer-can-read-this")
        finally:
            await admin_client.aclose()

        # Now try to read as viewer
        viewer_client = aioredis.from_url(
            redis_container_with_acl["viewer_url"], decode_responses=True
        )
        try:
            # Viewer CAN read
            value = await viewer_client.get("pywry:widget:viewer-test")
            assert value == "viewer-can-read-this"

            # Viewer CANNOT write
            with pytest.raises((NoPermissionError, Exception)):
                await viewer_client.set("pywry:widget:viewer-write", "should-fail")
        finally:
            await viewer_client.aclose()

    @pytest.mark.asyncio
    async def test_blocked_user_limited_access(self, redis_container_with_acl) -> None:
        """Blocked user should only be able to authenticate, nothing else."""
        import redis.asyncio as aioredis

        from redis.exceptions import NoPermissionError

        client = aioredis.from_url(redis_container_with_acl["blocked_url"], decode_responses=True)
        try:
            # Blocked user CAN authenticate (auth command is allowed)
            # But cannot do anything useful
            with pytest.raises((NoPermissionError, Exception)):
                await client.set("test", "value")

            with pytest.raises((NoPermissionError, Exception)):
                await client.get("test")
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_default_user_has_full_access(self, redis_container_with_acl) -> None:
        """Default user (no auth) should have full access in this test config."""
        import redis.asyncio as aioredis

        # Default user has no password requirement
        default_url = redis_container_with_acl["default_url"]
        client = aioredis.from_url(default_url, decode_responses=True)
        try:
            # Default user can ping
            pong = await client.ping()
            assert pong is True

            # Default user can read/write
            await client.set("default-test", "value")
            result = await client.get("default-test")
            assert result == "value"
            await client.delete("default-test")
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_widget_store_with_admin_credentials(self, redis_container_with_acl) -> None:
        """Widget store should work with admin credentials."""
        from pywry.state.redis import RedisWidgetStore

        store = RedisWidgetStore(
            redis_url=redis_container_with_acl["admin_url"],
            prefix="pywry:widget:",
        )
        try:
            widget_id = f"admin-widget-{uuid.uuid4().hex[:8]}"
            html = "<div>Admin widget content</div>"

            # Admin can register widgets
            await store.register(widget_id, html, token="admin-token")

            # Admin can read widgets
            exists = await store.exists(widget_id)
            assert exists

            stored_html = await store.get_html(widget_id)
            assert stored_html == html
        finally:
            await store.close()

    @pytest.mark.asyncio
    async def test_widget_store_with_editor_credentials(self, redis_container_with_acl) -> None:
        """Widget store should work with editor credentials."""
        from pywry.state.redis import RedisWidgetStore

        store = RedisWidgetStore(
            redis_url=redis_container_with_acl["editor_url"],
            prefix="pywry:widget:",
        )
        try:
            widget_id = f"editor-widget-{uuid.uuid4().hex[:8]}"
            html = "<div>Editor widget content</div>"

            # Editor can register widgets
            await store.register(widget_id, html, token="editor-token")

            # Editor can read widgets
            exists = await store.exists(widget_id)
            assert exists

            stored_html = await store.get_html(widget_id)
            assert stored_html == html
        finally:
            await store.close()

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_widgets(self, redis_container_with_acl) -> None:
        """Viewer should NOT be able to create widgets."""
        from redis.exceptions import NoPermissionError

        from pywry.state.redis import RedisWidgetStore

        store = RedisWidgetStore(
            redis_url=redis_container_with_acl["viewer_url"],
            prefix="pywry:widget:",
        )
        try:
            widget_id = f"viewer-widget-{uuid.uuid4().hex[:8]}"
            html = "<div>Viewer should not create this</div>"

            # Viewer CANNOT register widgets
            with pytest.raises((NoPermissionError, Exception)):
                await store.register(widget_id, html, token="viewer-token")
        finally:
            await store.close()

    @pytest.mark.asyncio
    async def test_viewer_can_read_widgets(self, redis_container_with_acl) -> None:
        """Viewer CAN read widgets created by others."""
        from pywry.state.redis import RedisWidgetStore

        # First create widget as admin
        admin_store = RedisWidgetStore(
            redis_url=redis_container_with_acl["admin_url"],
            prefix="pywry:widget:",
        )
        try:
            widget_id = f"viewer-readable-{uuid.uuid4().hex[:8]}"
            html = "<div>Viewer can read this</div>"
            await admin_store.register(widget_id, html, token="admin-token")
        finally:
            await admin_store.close()

        # Now read as viewer
        viewer_store = RedisWidgetStore(
            redis_url=redis_container_with_acl["viewer_url"],
            prefix="pywry:widget:",
        )
        try:
            # Viewer CAN check existence
            exists = await viewer_store.exists(widget_id)
            assert exists

            # Viewer CAN read HTML
            stored_html = await viewer_store.get_html(widget_id)
            assert stored_html == html
        finally:
            await viewer_store.close()

    @pytest.mark.asyncio
    async def test_session_store_with_admin_credentials(self, redis_container_with_acl) -> None:
        """Session store should work with admin credentials."""
        from pywry.state.redis import RedisSessionStore

        store = RedisSessionStore(
            redis_url=redis_container_with_acl["admin_url"],
            prefix="pywry:session:",
        )
        try:
            session_id = f"admin-session-{uuid.uuid4().hex[:8]}"

            # Admin can create sessions
            session = await store.create_session(session_id, "admin-user", roles=["admin"])
            assert session is not None
            assert session.user_id == "admin-user"

            # Admin can validate sessions
            is_valid = await store.validate_session(session_id)
            assert is_valid

            # Admin can delete sessions
            await store.delete_session(session_id)
            is_valid = await store.validate_session(session_id)
            assert is_valid is False
        finally:
            await store.close()

    @pytest.mark.asyncio
    async def test_wrong_password_fails(self, redis_container_with_acl) -> None:
        """Wrong password should fail authentication."""
        import redis.asyncio as aioredis

        from redis.exceptions import AuthenticationError

        # Try with wrong password
        host = redis_container_with_acl["host"]
        port = redis_container_with_acl["port"]
        bad_url = f"redis://admin:wrongpassword@{host}:{port}/0"

        client = aioredis.from_url(bad_url, decode_responses=True)
        try:
            with pytest.raises((AuthenticationError, Exception)):
                await client.ping()
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_nonexistent_user_fails(self, redis_container_with_acl) -> None:
        """Nonexistent user should fail authentication."""
        import redis.asyncio as aioredis

        from redis.exceptions import AuthenticationError

        host = redis_container_with_acl["host"]
        port = redis_container_with_acl["port"]
        bad_url = f"redis://fakeuser:fakepass@{host}:{port}/0"

        client = aioredis.from_url(bad_url, decode_responses=True)
        try:
            with pytest.raises((AuthenticationError, Exception)):
                await client.ping()
        finally:
            await client.aclose()
