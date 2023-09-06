"""System dependency."""

from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.service.system_service import SystemService


async def get_system_settings() -> SystemSettings:
    """Get system settings."""
    return SystemService().system_settings
