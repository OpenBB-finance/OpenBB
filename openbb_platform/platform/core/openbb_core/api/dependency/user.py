from fastapi import Depends
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.user_service import UserService
from typing_extensions import Annotated


async def get_user_service() -> UserService:
    """Get user service."""
    return UserService()


async def get_user_settings(
    _: Annotated[None, Depends(AuthService().auth_hook)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettings:
    """Get user settings."""
    return user_service.default_user_settings
