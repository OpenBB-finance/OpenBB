"""OpenBB API Account Router."""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic
from openbb_core.api.dependency.user import get_user_settings
from openbb_core.app.model.user_settings import UserSettings
from typing_extensions import Annotated

security = HTTPBasic()

router = APIRouter(prefix="/user", tags=["User"])
auth_hook = get_user_settings


@router.get("/me")
async def read_user_settings(
    user_settings: Annotated[UserSettings, Depends(get_user_settings)]
) -> UserSettings:
    """Read current user settings."""
    return user_settings
