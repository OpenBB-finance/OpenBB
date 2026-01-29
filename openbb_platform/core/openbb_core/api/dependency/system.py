"""系统依赖项。"""

from typing import Annotated

from fastapi import Depends
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService


async def get_system_service() -> SystemService:
    """获取系统服务。"""
    return SystemService()


async def get_system_settings(
    _: Annotated[None, Depends(AuthService().auth_hook)],
    system_service: Annotated[SystemService, Depends(get_system_service)],
) -> SystemSettings:
    """获取系统设置。"""
    return system_service.system_settings
