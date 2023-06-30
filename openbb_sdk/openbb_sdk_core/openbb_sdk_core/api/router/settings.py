from typing import Annotated

from fastapi import APIRouter, Depends
from openbb_sdk_core.api.dependency.user import (
    UserService,
    get_user,
    get_user_service,
)
from openbb_sdk_core.app.model.credentials import Credentials
from openbb_sdk_core.app.model.user_settings import UserSettings

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("")
async def read_users_settings(
    user_settings: Annotated[UserSettings, Depends(get_user)],
) -> UserSettings:
    return user_settings


@router.patch("/credentials")
async def patch_user_credentials(
    credentials: Credentials,
    user_settings: Annotated[UserSettings, Depends(get_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettings:
    current = user_settings.credentials.dict()
    incoming = credentials.dict(exclude_none=True)
    current.update(incoming)
    user_settings.credentials = Credentials.parse_obj(current)
    user_service.user_settings_repository.update(user_settings)
    return user_settings
