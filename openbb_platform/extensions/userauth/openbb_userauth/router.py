"""OpenBB API Account Router."""
from typing import Callable

from extensions.userauth.openbb_userauth.bootstrap import setup_default_users
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from openbb_core.api.model.token_response import TokenResponse
from openbb_core.app.model.credentials import Credentials
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.hub_service import HubService
from openbb_core.env import Env
from typing_extensions import Annotated

from openbb_userauth.auth_hook import (
    get_user_settings,
)
from openbb_userauth.utils import (
    UserService,
    authenticate_user,
    create_access_token,
    create_jwt_token,
    get_password_hash,
    get_user_service,
)

router = APIRouter(prefix="/user", tags=["User"])


def get_auth_hook() -> Callable:
    """Get auth hook."""
    return get_user_settings


# Check if we want to remove this
def bootstrap() -> None:
    """Bootstrap extension."""
    setup_default_users()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Login for access token."""
    user_settings = authenticate_user(
        password=form_data.password,
        user_service=user_service,
        username=form_data.username,
    )
    if not user_settings and Env().API_HUB_CONNECTION:
        hub_service = HubService()
        hub_service.connect(email=form_data.username, password=form_data.password)
        user_settings = hub_service.pull()
        if user_settings:
            user_settings.profile.username = form_data.username
            user_settings.profile.password_hash = get_password_hash(form_data.password)
            user_service.user_settings_repository.create(user_settings)

    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        sub=user_settings.id,
    )
    jwt_token = create_jwt_token(access_token=access_token)
    return TokenResponse(access_token=jwt_token, token_type="bearer")  # noqa: S106


@router.get("/me", operation_id="read_users_settings")
async def read_users_settings(
    user_settings: Annotated[UserSettings, Depends(get_user_settings)],
) -> UserSettings:
    """Read users settings."""
    return user_settings


@router.patch("/credentials", operation_id="patch_user_credentials")
async def patch_user_credentials(
    credentials: Credentials,
    user_settings: Annotated[UserSettings, Depends(get_user_settings)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettings:
    """Patch user credentials."""
    current = user_settings.credentials.model_dump()
    incoming = credentials.model_dump(exclude_none=True)
    current.update(incoming)
    user_settings.credentials = Credentials.model_validate(current)
    user_service.user_settings_repository.update(user_settings)
    return user_settings


if Env().API_HUB_CONNECTION:

    @router.put("/push")
    def push_user_settings_to_hub(
        user_settings: Annotated[UserSettings, Depends(get_user_settings)]
    ) -> UserSettings:
        """Push user settings to hub."""
        if user_settings.profile.hub_session:
            hub_service = HubService(user_settings.profile.hub_session)
            hub_service.push(user_settings)
            return user_settings
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not connected to hub.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @router.post("/pull")
    def pull_user_settings_from_hub(
        user_settings: Annotated[UserSettings, Depends(get_user_settings)],
        user_service: Annotated[UserService, Depends(get_user_service)],
    ) -> UserSettings:
        """Pull user settings from hub."""
        if user_settings.profile.hub_session:
            hub_service = HubService(user_settings.profile.hub_session)
            incoming = hub_service.pull()
            incoming.id = user_settings.id
            incoming_dict = incoming.model_dump(exclude_none=True)
            filtered_incoming = UserSettings.model_validate(incoming_dict)
            user_service.user_settings_repository.update(filtered_incoming)
            return incoming
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not connected to hub.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @router.post("/disconnect")
    def disconnect_from_hub(
        user_settings: Annotated[UserSettings, Depends(get_user_settings)],
    ) -> bool:
        """Disconnect from hub."""
        if user_settings.profile.hub_session:
            hub_service = HubService(user_settings.profile.hub_session)
            result = hub_service.disconnect()
            user_settings.profile.hub_session = None
            return result
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not connected to hub.",
            headers={"WWW-Authenticate": "Bearer"},
        )
