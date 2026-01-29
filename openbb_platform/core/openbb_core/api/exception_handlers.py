"""异常处理程序模块。"""

# pylint: disable=unused-argument

import logging
from collections.abc import Iterable
from typing import Any

from fastapi import Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse, Response
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.env import Env
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import ValidationError

logger = logging.getLogger("uvicorn.error")


class ExceptionHandlers:
    """异常处理程序。"""

    @staticmethod
    async def _handle(exception: Exception, status_code: int, detail: Any):
        """异常处理程序。"""
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
        """基本异常的异常处理程序。"""
        errors = error.errors if hasattr(error, "errors") else error

        if errors:
            if isinstance(errors, ValueError):
                return await ExceptionHandlers._handle(
                    exception=errors,
                    status_code=422,
                    detail=errors.args,
                )
            # 缺少必需的参数，并且 ValidationError 未处理。
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
            detail=f"意外错误 -> {error.__class__.__name__} -> {error}",
        )

    @staticmethod
    async def validation(
        request: Request, error: ValidationError | ResponseValidationError
    ):
        """ValidationError 的异常处理程序。"""
        # 一些验证是在 Fetcher 级别执行的。
        # 所以我们检查验证错误是否来自 QueryParams 类。
        # 并且它在请求查询参数中。
        # 如果是，我们使用查询更新错误位置。
        # 如果不是，我们将其作为基本异常错误处理。
        query_params = dict(request.query_params)
        if isinstance(error, ResponseValidationError):
            detail = [
                {
                    **{k: v for k, v in err.items() if k != "ctx"},
                    "loc": ("query",) + err.get("loc", ()),
                }
                for err in error.errors()
            ]
            return await ExceptionHandlers._handle(
                exception=error,
                status_code=422,
                detail=detail,
            )
        try:
            errors = (
                error.errors(include_url=False)
                if hasattr(error, "errors")
                else error.errors
            )
        except Exception:
            errors = error.errors if hasattr(error, "errors") else error
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
        """OpenBBError 的异常处理程序。"""
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=400,
            detail=str(error.original),
        )

    @staticmethod
    async def empty_data(_: Request, error: EmptyDataError):
        """EmptyDataError 的异常处理程序。"""
        return Response(status_code=204)

    @staticmethod
    async def unauthorized(_: Request, error: UnauthorizedError):
        """OpenBBError 的异常处理程序。"""
        return await ExceptionHandlers._handle(
            exception=error,
            status_code=502,
            detail=str(error.original),
        )
