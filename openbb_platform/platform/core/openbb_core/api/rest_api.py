from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openbb_core.api.dependency.user import get_user_service
from openbb_core.api.router.account import router as router_account
from openbb_core.api.router.commands import router as router_commands
from openbb_core.api.router.coverage import router as router_coverage
from openbb_core.api.router.system import router as router_system
from openbb_core.api.router.user import router as router_user
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.profile import Profile
from openbb_core.app.model.user_settings import UserSettings

app = FastAPI(
    title="OpenBB SDK API",
    description="This is the OpenBB SDK API.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "OpenBB Team",
        "url": "https://openbb.co",
        "email": "hello@openbb.co",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/LICENSE",
    },
)
app.include_router(router=router_account, prefix="/api/v1")
app.include_router(router=router_user, prefix="/api/v1")
app.include_router(router=router_system, prefix="/api/v1")
app.include_router(router=router_coverage, prefix="/api/v1")
app.include_router(router=router_commands, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def setup_default_user_settings():
    user_service = await get_user_service()
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
                profile=default_profile,
                credentials=default_user_settings.credentials,
                preferences=default_user_settings.preferences,
                defaults=default_user_settings.defaults,
            )
            user_settings_repository.create(model=default_user_settings)


@app.exception_handler(Exception)
async def api_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_kind": exc.__class__.__name__,
        },
    )


@app.exception_handler(OpenBBError)
async def openbb_exception_handler(request: Request, exc: OpenBBError):
    openbb_error = exc.original
    status_code = 400 if "No results" in str(openbb_error) else 500
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(openbb_error),
            "error_kind": openbb_error.__class__.__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("openbb_core.api.rest_api:app", reload=True)
