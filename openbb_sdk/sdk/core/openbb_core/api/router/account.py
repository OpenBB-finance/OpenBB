"""OpenBB API Account Router."""
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from openbb_core.api.dependency.user import (
    UserService,
    authenticate_user,
    create_access_token,
    create_jwt_token,
    get_password_hash,
    get_user,
    get_user_service,
)
from openbb_core.api.model.token_response import TokenResponse
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.hub_service import HubService
from typing_extensions import Annotated

router = APIRouter(prefix="/account", tags=["Account"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    openbb_hub: bool = Form(True),
) -> TokenResponse:
    """Login for access token."""
    user_settings = authenticate_user(
        password=form_data.password,
        user_service=user_service,
        username=form_data.username,
    )
    if not user_settings and openbb_hub:
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


@router.put("/push")
async def push_user_settings_to_hub(
    user_settings: Annotated[UserSettings, Depends(get_user)]
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
async def pull_user_settings_from_hub(
    user_settings: Annotated[UserSettings, Depends(get_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettings:
    """Pull user settings from hub."""
    if user_settings.profile.hub_session:
        hub_service = HubService(user_settings.profile.hub_session)
        incoming = hub_service.pull()
        incoming.id = user_settings.id
        incoming_dict = incoming.dict(exclude_none=True)
        filtered_incoming = UserSettings.parse_obj(incoming_dict)
        user_service.user_settings_repository.update(filtered_incoming)
        return incoming
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not connected to hub.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/disconnect")
async def disconnect_from_hub(
    user_settings: Annotated[UserSettings, Depends(get_user)],
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
