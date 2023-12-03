"""OpenBB API Account Router."""

from fastapi import APIRouter, Depends
from openbb_core.api.auth.user import authenticate_user, get_user_settings
from openbb_core.app.model.user_settings import UserSettings
from typing_extensions import Annotated

router = APIRouter(prefix="/user", tags=["User"])
auth_hook = authenticate_user
user_settings_hook = get_user_settings


@router.get("/me")
async def read_user_settings(
    user_settings: Annotated[UserSettings, Depends(get_user_settings)]
):
    """Read current user settings."""
    return user_settings
