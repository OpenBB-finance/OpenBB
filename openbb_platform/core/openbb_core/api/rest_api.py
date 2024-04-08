"""REST API for the OpenBB Platform."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openbb_core.api.app_loader import AppLoader
from openbb_core.api.router.commands import router as router_commands
from openbb_core.api.router.coverage import router as router_coverage
from openbb_core.api.router.system import router as router_system
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService
from openbb_core.env import Env

logger = logging.getLogger("uvicorn.error")

system = SystemService().system_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup event."""
    auth = "ENABLED" if Env().API_AUTH else "DISABLED"
    banner = rf"""

                   ███╗
  █████████████████╔══█████████████████╗       OpenBB Platform v{system.version}
  ███╔══════════███║  ███╔══════════███║
  █████████████████║  █████████████████║       Authentication: {auth}
  ╚═════════════███║  ███╔═════════════╝
     ██████████████║  ██████████████╗
     ███╔═══════███║  ███╔═══════███║
     ██████████████║  ██████████████║
     ╚═════════════╝  ╚═════════════╝
Investment research for everyone, anywhere.

    https://my.openbb.co/app/platform

"""
    logger.info(banner)
    yield


app = FastAPI(
    title=system.api_settings.title,
    description=system.api_settings.description,
    version=system.api_settings.version,
    terms_of_service=system.api_settings.terms_of_service,
    contact={
        "name": system.api_settings.contact_name,
        "url": system.api_settings.contact_url,
        "email": system.api_settings.contact_email,
    },
    license_info={
        "name": system.api_settings.license_name,
        "url": system.api_settings.license_url,
    },
    servers=[
        {
            "url": s.url,
            "description": s.description,
        }
        for s in system.api_settings.servers
    ],
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=system.api_settings.cors.allow_origins,
    allow_methods=system.api_settings.cors.allow_methods,
    allow_headers=system.api_settings.cors.allow_headers,
)
app.openapi_tags = AppLoader.get_openapi_tags()
AppLoader.from_routers(
    app=app,
    routers=(
        [AuthService().router, router_system, router_coverage, router_commands]
        if Env().DEV_MODE
        else [router_commands]
    ),
    prefix=system.api_settings.prefix,
)


@app.exception_handler(Exception)
async def api_exception_handler(_: Request, exc: Exception):
    """Exception handler for all other exceptions."""
    if Env().DEBUG_MODE:
        raise exc
    logger.error(exc)
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_kind": exc.__class__.__name__,
        },
    )


@app.exception_handler(OpenBBError)
async def openbb_exception_handler(_: Request, exc: OpenBBError):
    """Exception handler for OpenBB errors."""
    if Env().DEBUG_MODE:
        raise exc
    logger.error(exc.original)
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
