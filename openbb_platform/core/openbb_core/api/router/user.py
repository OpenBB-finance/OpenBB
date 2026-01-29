"""OpenBB 平台 API 账户路由器。"""

from typing import Annotated

from fastapi import APIRouter, Depends
from openbb_core.api.auth.user import authenticate_user, get_user_settings
from openbb_core.app.model.user_settings import UserSettings

router = APIRouter(prefix="/user", tags=["User"])
auth_hook = authenticate_user
user_settings_hook = get_user_settings


@router.get("/me")
async def read_user_settings(
    user_settings: Annotated[UserSettings, Depends(get_user_settings)],
):
    """读取当前用户设置。"""
    return user_settings
