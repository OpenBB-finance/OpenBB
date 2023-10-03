"""User dependency."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from typing_extensions import Annotated

from openbb_userauth.auth.utils import (
    ALGORITHM,
    SECRET_KEY,
    oauth2_scheme,
)
from openbb_userauth.user.userdb_service import UserDBService, get_userdb_service


async def get_user_settings(
    jwt_token: Annotated[str, Depends(oauth2_scheme)],
    userdb_service: Annotated[UserDBService, Depends(get_userdb_service)],
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

    user_settings = userdb_service.user_settings_repository.read(
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
