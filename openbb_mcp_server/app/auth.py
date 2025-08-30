"""Custom authentication for the MCP server."""

from typing import Any, Optional

from fastapi import HTTPException
from fastmcp.server.auth.auth import AuthProvider
from openbb_core.api.auth.user import get_user_service
from starlette.requests import Request


class TokenAuthProvider(AuthProvider):
    """Token authentication provider."""

    def __init__(self, user_service: Any):
        """Initialize the token auth provider."""
        self.user_service = user_service

    async def authorize(self, request: Request) -> bool:
        """Authorize the request."""
        if "Authorization" not in request.headers:
            return False

        auth_header = request.headers["Authorization"]
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return False
            user = self.user_service.get_user_from_token(token)
            if not user:
                return False
            request.state.user = user
        except (ValueError, HTTPException):
            return False

        return True

    async def verify_token(self, token: str) -> Optional[dict[str, Any]]:
        """Verify the token."""
        try:
            user = self.user_service.get_user_from_token(token)
            if not user:
                return None
            return user.model_dump()
        except (ValueError, HTTPException):
            return None


def get_auth_provider() -> TokenAuthProvider:
    """Get the authentication provider."""
    user_service = get_user_service()
    return TokenAuthProvider(user_service)
