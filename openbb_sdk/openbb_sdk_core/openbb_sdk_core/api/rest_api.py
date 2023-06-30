from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openbb_sdk_core.api.dependency.system import get_system_settings
from openbb_sdk_core.api.dependency.user import get_user_service
from openbb_sdk_core.api.router.account import router as router_account
from openbb_sdk_core.api.router.commands import router as router_commands
from openbb_sdk_core.api.router.settings import router as router_settings
from openbb_sdk_core.api.router.system import router as router_system
from openbb_sdk_core.app.model.profile import Profile
from openbb_sdk_core.app.model.user_settings import UserSettings

app = FastAPI()
app.include_router(router=router_account, prefix="/api/v1")
app.include_router(router=router_settings, prefix="/api/v1")
app.include_router(router=router_system, prefix="/api/v1")
app.include_router(router=router_commands, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # react renders on this port
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def setup_default_user_settings():
    system_settings = await get_system_settings()
    user_service = await get_user_service(system_settings=system_settings)
    user_settings_repository = user_service.user_settings_repository
    default_user_settings = user_service.default_user_settings
    default_profile_list = [
        Profile(
            active=True,
            username="openbb",
            # HASH OF 'openbb'
            # cSpell:disable-next-line
            password_hash="$2b$12$c8x3TOBCbSMyhNE8FqVCz.FVydrgVtA8wH8e/CQ3V43IfU2O5fZoq",  # nosec  # noqa: S106
        ),
        Profile(
            active=True,
            username="finance",
            # HASH OF 'finance'
            # cSpell:disable-next-line
            password_hash="$2b$12$/EdKMJ3C5plpqDS/dqpdvO0wL9v/XRttg65kkIgp8XTJWWmCu7L8y",  # nosec # noqa: S106
        ),
    ]

    for default_profile in default_profile_list:
        user_settings = user_settings_repository.read_by_profile(
            filter_list=[("username", default_profile.username)]
        )
        if user_settings:
            user_settings.profile = default_profile
            user_settings.credentials = default_user_settings.credentials
            user_settings_repository.update(model=user_settings)
        else:
            default_user_settings = UserSettings(
                profile=default_profile, credentials=default_user_settings.credentials
            )
            user_settings_repository.create(model=default_user_settings)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("openbb_sdk_core.api.rest_api:app", reload=True)
