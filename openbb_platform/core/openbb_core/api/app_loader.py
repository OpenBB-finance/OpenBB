"""应用程序加载器模块。"""

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import ResponseValidationError
from openbb_core.api.exception_handlers import ExceptionHandlers
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.router import RouterLoader
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import ValidationError


class AppLoader:
    """应用程序加载器。"""

    @staticmethod
    def add_routers(app: FastAPI, routers: list[APIRouter | None], prefix: str):
        """添加路由器。"""
        for router in routers:
            if router:
                app.include_router(router=router, prefix=prefix)

    @staticmethod
    def add_openapi_tags(app: FastAPI):
        """添加 OpenAPI 标签。"""
        main_router = RouterLoader.from_extensions()
        # 为主路由器中的每个路由器添加标签数据
        app.openapi_tags = [
            {
                "name": r,
                "description": main_router.get_attr(r, "description"),
            }
            for r in main_router.routers
        ]

    @staticmethod
    def add_exception_handlers(app: FastAPI):
        """添加异常处理程序。"""
        app.exception_handlers[Exception] = ExceptionHandlers.exception
        app.exception_handlers[ValidationError] = ExceptionHandlers.validation
        app.exception_handlers[ResponseValidationError] = ExceptionHandlers.validation
        app.exception_handlers[OpenBBError] = ExceptionHandlers.openbb
        app.exception_handlers[EmptyDataError] = ExceptionHandlers.empty_data
        app.exception_handlers[UnauthorizedError] = ExceptionHandlers.unauthorized
