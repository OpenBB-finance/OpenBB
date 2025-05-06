"""REST API for the OpenBB Platform."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openbb_core.api.app_loader import AppLoader
from openbb_core.api.mcp_server import mount_mcp_server
from openbb_core.api.router.commands import router as router_commands
from openbb_core.api.router.coverage import router as router_coverage
from openbb_core.api.router.system import router as router_system
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService
from openbb_core.env import Env

logger = logging.getLogger("uvicorn.error")

system = SystemService().system_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup event."""
    auth = "ENABLED" if Env().API_AUTH else "DISABLED"
    mcp = "ENABLED" if Env().OPENBB_ENABLE_MCP else "DISABLED"
    banner = rf"""

                   ███╗
  █████████████████╔══█████████████████╗       OpenBB Platform v{system.version}
  ███╔══════════███║  ███╔══════════███║
  █████████████████║  █████████████████║       Authentication: {auth}
  ╚═════════════███║  ███╔═════════════╝       MCP: {mcp}
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
AppLoader.add_routers(
    app=app,
    routers=(
        [AuthService().router, router_system, router_coverage, router_commands]
        if Env().DEV_MODE
        else (
            [router_commands, router_coverage]
            if hasattr(router_commands, "routes") and router_commands.routes
            else [router_commands]
        )
    ),
    prefix=system.api_settings.prefix,
)
AppLoader.add_openapi_tags(app)
AppLoader.add_exception_handlers(app)

if Env().OPENBB_ENABLE_MCP:
    try:
        mount_mcp_server(app)
    except ImportError as e:
        logger.error(f"Failed to import or mount MCP server: {e}")
        logger.error("Ensure 'fastapi-mcp' is installed.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while mounting MCP server: {e}")
else:
    logger.debug("MCP Server not enabled (OPENBB_ENABLE_MCP not set to true).")


if __name__ == "__main__":
    # pylint: disable=import-outside-toplevel
    import uvicorn

    # This initializes the OpenBB environment variables so they can be read before uvicorn is run.
    Env()
    uvicorn_kwargs = system.python_settings.model_dump().get("uvicorn", {})
    uvicorn_reload = uvicorn_kwargs.pop("reload", None)

    if uvicorn_reload is None or uvicorn_reload:
        uvicorn_kwargs["reload"] = True

    uvicorn_app = uvicorn_kwargs.pop("app", "openbb_core.api.rest_api:app")

    uvicorn.run(uvicorn_app, **uvicorn_kwargs)
