"""Exception handlers module."""

# pylint: disable=unused-argument

import logging
from collections.abc import Iterable
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.env import Env
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

logger = logging.getLogger("uvicorn.error")


class ExceptionHandlers:
    """Exception handlers."""

    @staticmethod
    async def _handle(exception: Exception, status_code: int, detail: Any):
        """Exception handler."""
        if Env().DEBUG_MODE:
            raise exception
        logger.error(exception)
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": detail,
            },
        )

    @staticmethod
    async def exception(_: Request, error: Exception) -> JSONResponse:
        """Exception handler for Base Exception."""
        errors = error.errors(include_url=False) if hasattr(error, "errors") else error
        if errors:
            if isinstance(errors, ValueError):
                return await ExceptionHandlers._handle(
                    exception=errors,
                    status_code=422,
                    detail=errors.args,
                )
            # Required parameters are missing and is not handled by ValidationError.
            if isinstance(errors, Iterable):
                for err in errors:
                    if err.get("type") == "missing":
                        return await ExceptionHandlers._handle(
                            exception=error,
                            status_code=422,
                            detail={**err},
                        )
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=500,
            detail="Unexpected error.",
        )

    @staticmethod
    async def validation(request: Request, error: ValidationError):
        """Exception handler for ValidationError."""
        # Some validation is performed at Fetcher level.
        # So we check if the validation error comes from a QueryParams class.
        # And that it is in the request query params.
        # If yes, we update the error location with query.
        # If not, we handle it as a base Exception error.
        query_params = dict(request.query_params)
        errors = error.errors(include_url=False)
        all_in_query = all(
            loc in query_params for err in errors for loc in err.get("loc", ())
        )
        if "QueryParams" in error.title and all_in_query:
            detail = [
                {
                    **{k: v for k, v in err.items() if k != "ctx"},
                    "loc": ("query",) + err.get("loc", ()),
                }
                for err in errors
            ]
            return await ExceptionHandlers._handle(
                exception=error,
                status_code=422,
                detail=detail,
            )
        return await ExceptionHandlers.exception(request, error)

    @staticmethod
    async def openbb(_: Request, error: OpenBBError):
        """Exception handler for OpenBBError."""
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=400,
            detail=str(error.original),
        )

    @staticmethod
    async def empty_data(_: Request, error: EmptyDataError):
        """Exception handler for EmptyDataError."""
        return Response(status_code=204)
