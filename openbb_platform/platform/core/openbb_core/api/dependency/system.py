"""System dependency."""

from fastapi import Depends
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService
from typing_extensions import Annotated


async def get_system_service() -> SystemService:
    """Get system service."""
    return SystemService()


async def get_system_settings(
    _: Annotated[None, Depends(AuthService().auth_hook)],
    system_service: Annotated[SystemService, Depends(get_system_service)],
) -> SystemSettings:
    """Get system settings."""
    return system_service.system_settings
