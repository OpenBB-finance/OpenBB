"""Exception handlers module."""

import logging
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.env import Env
from pydantic import ValidationError

logger = logging.getLogger("uvicorn.error")


class ExceptionHandlers:
    """Exception handlers."""

    @staticmethod
    async def _handle(exception: Exception, status_code: int, kind: str, detail: Any):
        """Exception handler."""
        if Env().DEBUG_MODE:
            raise exception
        logger.error(exception)
        return JSONResponse(
            status_code=status_code,
            content={
                "kind": kind,
                "detail": detail,
            },
        )

    @staticmethod
    async def base(_: Request, error: Exception) -> JSONResponse:
        """Exception handler for Base Exception."""
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=500,
            kind="General",
            detail="Unexpected error.",
        )

    @staticmethod
    async def query_validation(request: Request, error: ValidationError):
        """Exception handler for ValidationError."""
        # We check if the validation error comes from provider QueryParams.
        # Some validation is performed at Fetcher level.
        # If yes, we update the error location with query.
        # If not, we handle it as a base Exception error.
        query_params = dict(request.query_params)
        errors = error.errors(include_url=False)
        all_in_query = all(
            loc in query_params for err in errors for loc in err.get("loc", ())
        )
        if "QueryParams" in error.title and all_in_query:
            detail = [{**err, "loc": ("query",) + err.get("loc", ())} for err in errors]
            return await ExceptionHandlers._handle(
                exception=error, status_code=422, kind="ValidationError", detail=detail
            )
        return await ExceptionHandlers.base(request, error)

    @staticmethod
    async def openbb(_: Request, error: OpenBBError):
        """Exception handler for OpenBBError."""
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=400,
            kind=error.__class__.__name__,
            detail=str(error.original),
        )
