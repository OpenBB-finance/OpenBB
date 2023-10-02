"""User dependency."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from openbb_core.app.service.user_service import UserService
from openbb_userauth.auth.utils import (
    ALGORITHM,
    SECRET_KEY,
    get_user_service,
    oauth2_scheme,
)
from typing_extensions import Annotated


async def get_user_settings(
    jwt_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Get user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt_payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_settings_id: Optional[str] = jwt_payload.get("sub")
        if user_settings_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    user_settings = user_service.user_settings_repository.read(
        filter_list=[("id", user_settings_id)]
    )
    if (
        user_settings is None
        or user_settings.profile is None
        or user_settings.profile.active is None
    ):
        raise credentials_exception
    if user_settings and user_settings.profile and not user_settings.profile.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user_settings
