"""Authentication and RBAC (Role-Based Access Control) utilities.

Provides utilities for:
- Session token generation and validation
- User authentication middleware
- Permission checking
- Role-based access patterns

This module works with the SessionStore for persistent session management.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.websockets import WebSocket

    from .base import SessionStore
    from .types import UserSession


logger = logging.getLogger(__name__)


# Default role permissions
DEFAULT_ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"read", "write", "admin", "delete", "manage_users"},
    "editor": {"read", "write"},
    "viewer": {"read"},
    "anonymous": set(),  # No permissions
}


@dataclass
class AuthConfig:
    """Authentication configuration.

    Attributes
    ----------
    enabled : bool
        Whether authentication is enabled.
    session_cookie : str
        Name of the session cookie.
    auth_header : str
        HTTP header for bearer token authentication.
    token_secret : str
        Secret key for token signing.
    session_ttl : int
        Session TTL in seconds.
    require_auth_for_widgets : bool
        Whether widgets require authentication to view.
    """

    enabled: bool = False
    session_cookie: str = "pywry_session"
    auth_header: str = "Authorization"
    token_secret: str = ""
    session_ttl: int = 86400  # 24 hours
    require_auth_for_widgets: bool = False

    def __post_init__(self) -> None:
        """Generate token secret if not provided."""
        if not self.token_secret:
            self.token_secret = secrets.token_hex(32)


def generate_session_token(
    user_id: str,
    secret: str,
    expires_at: float | None = None,
) -> str:
    """Generate a signed session token.

    Parameters
    ----------
    user_id : str
        The user ID.
    secret : str
        Secret key for signing.
    expires_at : float or None
        Expiration timestamp. If None, token doesn't expire.

    Returns
    -------
    str
        Signed session token.
    """
    # Token format: user_id:timestamp:expiry:signature
    timestamp = int(time.time())
    expiry = int(expires_at) if expires_at else 0

    payload = f"{user_id}:{timestamp}:{expiry}"
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]

    return f"{payload}:{signature}"


def validate_session_token(  # pylint: disable=no-else-return
    token: str,
    secret: str,
) -> tuple[bool, str | None, str | None]:
    """Validate a session token and extract user ID.

    Parameters
    ----------
    token : str
        The session token.
    secret : str
        Secret key for verification.

    Returns
    -------
    tuple[bool, str | None, str | None]
        (is_valid, user_id, error_message)
    """
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return (False, None, "Invalid token format")

        user_id, timestamp_str, expiry_str, signature = parts
        # Parse to validate format, use string values for signature verification
        int(timestamp_str)  # Validates format
        expiry = int(expiry_str)

        # Check expiry
        if 0 < expiry < time.time():
            return (False, None, "Token expired")

        # Verify signature using original string values
        payload = f"{user_id}:{timestamp_str}:{expiry_str}"
        expected_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()[:16]

        if not hmac.compare_digest(signature, expected_sig):
            return (False, None, "Invalid signature")
    except (ValueError, IndexError) as e:
        return (False, None, f"Token parse error: {e}")
    else:
        return (True, user_id, None)


def generate_widget_token(
    widget_id: str,
    secret: str,
    ttl: int = 300,  # 5 minutes
) -> str:
    """Generate a short-lived token for widget authentication.

    Parameters
    ----------
    widget_id : str
        The widget ID.
    secret : str
        Secret key for signing.
    ttl : int
        Token TTL in seconds.

    Returns
    -------
    str
        Signed widget token.
    """
    expires_at = time.time() + ttl
    return generate_session_token(widget_id, secret, expires_at)


def validate_widget_token(
    token: str,
    widget_id: str,
    secret: str,
) -> bool:
    """Validate a widget authentication token.

    Parameters
    ----------
    token : str
        The widget token.
    widget_id : str
        Expected widget ID.
    secret : str
        Secret key for verification.

    Returns
    -------
    bool
        True if token is valid for this widget.
    """
    is_valid, extracted_id, _ = validate_session_token(token, secret)
    return is_valid and extracted_id == widget_id


async def get_session_from_request(
    request: Request | WebSocket,
    session_store: SessionStore,
    config: AuthConfig,
) -> UserSession | None:
    """Extract and validate session from HTTP request or WebSocket.

    Parameters
    ----------
    request : Request or WebSocket
        The incoming request.
    session_store : SessionStore
        Session store for validation.
    config : AuthConfig
        Authentication configuration.

    Returns
    -------
    UserSession or None
        The valid session, or None if not authenticated.
    """
    session_id: str | None = None

    # Try cookie first
    if hasattr(request, "cookies"):
        session_id = request.cookies.get(config.session_cookie)

    # Try Authorization header
    if not session_id and hasattr(request, "headers"):
        auth_header = request.headers.get(config.auth_header, "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            is_valid, user_id, _ = validate_session_token(token, config.token_secret)
            if is_valid and user_id:
                # Token-based auth - look up session by user_id
                sessions = await session_store.list_user_sessions(user_id)
                if sessions:
                    return sessions[0]  # Return first active session
                return None

    # Try query parameter (for WebSocket)
    if not session_id and hasattr(request, "query_params"):
        session_id = request.query_params.get("session")

    if not session_id:
        return None

    # Validate session
    return await session_store.get_session(session_id)


async def check_widget_permission(
    session: UserSession | None,
    widget_id: str,
    permission: str,
    session_store: SessionStore,
) -> bool:
    """Check if a session has permission to access a widget.

    Parameters
    ----------
    session : UserSession or None
        The user session.
    widget_id : str
        The widget ID.
    permission : str
        Required permission (e.g., "read", "write").
    session_store : SessionStore
        Session store for permission checking.

    Returns
    -------
    bool
        True if access is allowed.
    """
    if session is None:
        return False

    return await session_store.check_permission(
        session.session_id,
        "widget",
        widget_id,
        permission,
    )


def get_role_permissions(role: str) -> set[str]:
    """Get permissions for a role.

    Parameters
    ----------
    role : str
        The role name.

    Returns
    -------
    set[str]
        Set of permissions for this role.
    """
    return DEFAULT_ROLE_PERMISSIONS.get(role, set())


def has_permission(session: UserSession | None, permission: str) -> bool:
    """Check if a session has a specific permission via roles.

    Parameters
    ----------
    session : UserSession or None
        The user session.
    permission : str
        The required permission.

    Returns
    -------
    bool
        True if the session has the permission.
    """
    if session is None:
        return False

    return any(permission in get_role_permissions(role) for role in session.roles)


def is_admin(session: UserSession | None) -> bool:
    """Check if a session has admin role.

    Parameters
    ----------
    session : UserSession or None
        The user session.

    Returns
    -------
    bool
        True if the session has admin role.
    """
    if session is None:
        return False
    return "admin" in session.roles


class AuthMiddleware:
    """ASGI middleware for authentication.

    Extracts session from requests and adds to request state.
    """

    def __init__(
        self,
        app: Any,
        session_store: SessionStore,
        config: AuthConfig,
    ) -> None:
        """Initialize the middleware.

        Parameters
        ----------
        app : ASGI application
            The wrapped application.
        session_store : SessionStore
            Session store for validation.
        config : AuthConfig
            Authentication configuration.
        """
        self.app = app
        self.session_store = session_store
        self.config = config

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        """Handle ASGI request."""
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Add session to scope
        scope["session"] = None

        if self.config.enabled:
            # Create a minimal request-like object for session extraction
            headers = dict(scope.get("headers", []))
            cookies = {}

            # Parse cookies from headers
            cookie_header = headers.get(b"cookie", b"").decode()
            for part in cookie_header.split(";"):
                if "=" in part:
                    key, value = part.strip().split("=", 1)
                    cookies[key] = value

            # Create request wrapper
            class _RequestWrapper:
                def __init__(
                    self,
                    hdrs: dict[bytes, bytes],
                    ckies: dict[str, str],
                    qparams: dict[str, str],
                ) -> None:
                    self._headers = hdrs
                    self._cookies = ckies
                    self._query_params = qparams

                @property
                def headers(self) -> dict[str, str]:
                    """Get HTTP headers as decoded dict."""
                    return {k.decode(): v.decode() for k, v in self._headers.items()}

                @property
                def cookies(self) -> dict[str, str]:
                    """Get cookies dict."""
                    return self._cookies

                @property
                def query_params(self) -> dict[str, str]:
                    """Get query parameters dict."""
                    return self._query_params

            # Parse query params
            query_string = scope.get("query_string", b"").decode()
            query_params = {}
            for part in query_string.split("&"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    query_params[key] = value

            wrapper = _RequestWrapper(headers, cookies, query_params)
            session = await get_session_from_request(
                wrapper,  # type: ignore[arg-type]
                self.session_store,
                self.config,
            )
            scope["session"] = session

        await self.app(scope, receive, send)
