"""Bearer-token authentication for the MCP server."""

import base64
import secrets

from fastmcp.server.auth import AuthProvider, TokenVerifier
from fastmcp.server.auth.auth import AccessToken


class TokenAuthProvider(TokenVerifier):
    """Accept Bearer tokens that carry ``base64(username:password)`` for fixed credentials.

    Parameters
    ----------
    credentials : tuple[str, str]
        The accepted ``(username, password)`` pair.
    """

    def __init__(self, credentials: tuple[str, str]) -> None:
        super().__init__()
        self._username = credentials[0].encode("utf-8")
        self._password = credentials[1].encode("utf-8")

    async def verify_token(self, token: str) -> AccessToken | None:
        """Return an access token when the Bearer token carries the configured credentials."""
        try:
            decoded = base64.b64decode(token, validate=True)
        except ValueError:
            return None
        username, separator, password = decoded.partition(b":")
        if not separator:
            return None
        is_user_valid = secrets.compare_digest(username, self._username)
        is_pass_valid = secrets.compare_digest(password, self._password)
        if not (is_user_valid and is_pass_valid):
            return None
        return AccessToken(
            token=token,
            client_id=username.decode("utf-8", errors="replace"),
            scopes=[],
            expires_at=None,
        )


def get_auth_provider(
    auth: AuthProvider | tuple[str, str] | list[str] | None,
) -> AuthProvider | None:
    """Return the auth provider for the ``auth`` argument of ``create_mcp_server``.

    Parameters
    ----------
    auth : AuthProvider | tuple[str, str] | list[str] | None
        A FastMCP auth provider, a ``(username, password)`` pair, or None for no authentication.

    Returns
    -------
    AuthProvider | None
        The provider that guards the server, or None when no authentication is configured.

    Raises
    ------
    TypeError
        If ``auth`` is neither an auth provider nor a pair of non-empty strings.
    """
    if auth is None:
        return None
    if isinstance(auth, AuthProvider):
        return auth
    if (
        isinstance(auth, (tuple, list))
        and len(auth) == 2
        and all(isinstance(part, str) and part for part in auth)
    ):
        return TokenAuthProvider((auth[0], auth[1]))
    raise TypeError(
        "auth must be a fastmcp AuthProvider or a (username, password) pair of non-empty strings."
    )
