"""REST API for the OpenBB Platform."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openbb_core.api.app_loader import AppLoader
from openbb_core.api.router.commands import router as router_commands
from openbb_core.api.router.coverage import router as router_coverage
from openbb_core.api.router.system import router as router_system
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.version import VERSION
from openbb_core.env import Env

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="OpenBB Platform API",
    description="This is the OpenBB Platform API.",
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
AppLoader.from_routers(
    app=app,
    routers=[AuthService().router, router_system, router_coverage, router_commands]
    if Env().DEV_MODE
    else [router_commands],
    prefix="/api/v1",
)


@app.on_event("startup")
async def startup():
    """Startup event."""
    auth = "ENABLED" if Env().API_AUTH else "DISABLED"
    banner = rf"""

                   ███╗
  █████████████████╔══█████████████████╗       OpenBB Platform {VERSION}
  ███╔══════════███║  ███╔══════════███║
  █████████████████║  █████████████████║       Authentication: {auth}
  ╚═════════════███║  ███╔═════════════╝
     ██████████████║  ██████████████╗
     ███╔═══════███║  ███╔═══════███║
     ██████████████║  ██████████████║
     ╚═════════════╝  ╚═════════════╝
Investment research for everyone, anywhere.

       https://my.openbb.co/app/sdk

"""
    logger.info(banner)


@app.exception_handler(Exception)
async def api_exception_handler(request: Request, exc: Exception):
    """Exception handler for all other exceptions."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_kind": exc.__class__.__name__,
        },
    )


@app.exception_handler(OpenBBError)
async def openbb_exception_handler(request: Request, exc: OpenBBError):
    """Exception handler for OpenBB errors."""
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
