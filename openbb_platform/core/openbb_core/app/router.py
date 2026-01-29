"""OpenBB 路由器。"""

import traceback
import warnings
from collections.abc import Callable
from functools import lru_cache
from inspect import isclass
from typing import (
    Annotated,
    Any,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from fastapi import APIRouter, Depends
from openbb_core.app.deprecation import DeprecationSummary, OpenBBDeprecationWarning
from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.example import filter_list
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
)
from openbb_core.env import Env
from pydantic import BaseModel
from typing_extensions import ParamSpec

P = ParamSpec("P")


class OpenBBErrorResponse(BaseModel):
    """OpenBB 错误响应。"""

    detail: str
    error_kind: str


class Router:
    """OpenBB 路由器类。"""

    @property
    def api_router(self) -> APIRouter:
        """API 路由器。"""
        return self._api_router

    @property
    def prefix(self) -> str:
        """前缀。"""
        return self._api_router.prefix

    @property
    def description(self) -> str | None:
        """描述。"""
        return self._description

    @property
    def routers(self) -> dict[str, "Router"]:
        """嵌套在路由器中的路由器，即子路由器。"""
        return self._routers

    def __init__(
        self,
        prefix: str = "",
        description: str | None = None,
    ) -> None:
        """初始化路由器。"""
        self._api_router = APIRouter(
            prefix=prefix,
            responses={404: {"description": "未找到"}},
        )
        self._description = description
        self._routers: dict[str, Router] = {}

    @overload
    def command(self, func: Callable[P, OBBject] | None) -> Callable[P, OBBject]:
        pass

    @overload
    def command(self, **kwargs) -> Callable:
        pass

    def command(
        self,
        func: Callable[P, OBBject] | None = None,
        **kwargs,
    ) -> Callable | None:
        """路由的命令装饰器。"""
        if func is None:
            return lambda f: self.command(f, **kwargs)

        api_router = self._api_router
        model = kwargs.pop("model", "")
        no_validate = kwargs.pop("no_validate", None)
        openapi_extra = kwargs.get("openapi_extra") or {}
        kwargs["openapi_extra"] = openapi_extra

        if widget_config := kwargs.pop("widget_config", None):
            openapi_extra["widget_config"] = widget_config

        if mcp_config := kwargs.pop("mcp_config", None):
            openapi_extra["mcp_config"] = mcp_config

        if no_validate is True:
            func.__annotations__["return"] = None

        if func := SignatureInspector.complete(func, model):
            kwargs["response_model_exclude_unset"] = True
            openapi_extra["model"] = model
            openapi_extra["examples"] = filter_list(
                examples=kwargs.pop("examples", []),
                providers=ProviderInterface().available_providers,
            )
            openapi_extra["no_validate"] = no_validate
            kwargs["operation_id"] = kwargs.get(
                "operation_id", SignatureInspector.get_operation_id(func)
            )
            kwargs["path"] = kwargs.get("path", f"/{func.__name__}")
            kwargs["endpoint"] = func
            kwargs["methods"] = kwargs.get("methods", ["GET"])
            kwargs["response_model"] = (
                kwargs.get(
                    "response_model",
                    func.__annotations__["return"],  # type: ignore
                )
                if not no_validate
                else func.__annotations__["return"]
            )
            kwargs["response_model_by_alias"] = kwargs.get(
                "response_model_by_alias", False
            )
            kwargs["description"] = SignatureInspector.get_description(func)
            kwargs["responses"] = kwargs.get(
                "responses",
                {
                    204: {
                        "description": "空响应",
                    },
                    400: {
                        "model": OpenBBErrorResponse,
                        "description": "未找到结果",
                    },
                    404: {"description": "未找到"},
                    500: {
                        "model": OpenBBErrorResponse,
                        "description": "内部错误",
                    },
                    502: {
                        "model": OpenBBErrorResponse,
                        "description": "未授权",
                    },
                },
            )

            # 对于自定义弃用
            if kwargs.get("deprecated", False):
                deprecation: OpenBBDeprecationWarning = kwargs.pop("deprecation")

                kwargs["summary"] = DeprecationSummary(
                    deprecation.long_message, deprecation
                )

            kwargs["openapi_extra"] = openapi_extra

            api_router.add_api_route(**kwargs)

        return func

    def include_router(
        self,
        router: "Router",
        prefix: str = "",
    ):
        """包含路由器。"""
        tags = [prefix.strip("/")] if prefix else None
        self._api_router.include_router(
            router=router.api_router,
            prefix=prefix,
            tags=tags,  # type: ignore
        )
        name = prefix if prefix else router.prefix
        self._routers[name.strip("/")] = router

    def get_attr(self, path: str, attr: str) -> Any:
        """从路径获取路由器属性。
        
        Parameters
        ----------
        path : str
            路由器或嵌套路由器的路径。
            例如："/equity" 或 "/equity/price"。
        attr : str
            要获取的属性。

        Returns
        -------
        Any
            属性值。
        """
        return self._search_attr(self, path, attr)

    @staticmethod
    def _search_attr(router: "Router", path: str, attr: str) -> Any:
        """从路径递归搜索路由器属性。"""
        path = path.strip("/")
        first = path.split("/")[0]
        if first in router.routers:
            return Router._search_attr(
                router.routers[first], "/".join(path.split("/")[1:]), attr
            )
        return getattr(router, attr, None)

    @classmethod
    def from_fastapi(cls, api_router: APIRouter) -> "Router":
        """从 FastAPI APIRouter 创建 OpenBB 路由器。"""
        description = getattr(api_router, "description", None)
        instance = cls(prefix=api_router.prefix, description=description)
        instance._api_router = api_router  # type: ignore[attr-defined]

        return instance


class SignatureInspector:
    """检查函数签名。"""

    @classmethod
    def complete(
        cls, func: Callable[P, OBBject], model: str
    ) -> Callable[P, OBBject] | None:
        """完成函数签名。"""
        if isclass(return_type := func.__annotations__["return"]) and not issubclass(
            return_type, OBBject
        ):
            return func

        provider_interface = ProviderInterface()

        if model:
            if model not in provider_interface.models:
                if Env().DEBUG_MODE:
                    warnings.warn(
                        message=f"\nSkipping api route '/{func.__name__}'.\n"
                        f"Model '{model}' not found.\n\n"
                        "Check available models in ProviderInterface().models",
                        category=OpenBBWarning,
                    )
                return None
            cls.validate_signature(
                func,
                {
                    "provider_choices": ProviderChoices,
                    "standard_params": StandardParams,
                    "extra_params": ExtraParams,
                },
            )

            func = cls.inject_dependency(
                func=func,
                arg="provider_choices",
                callable_=provider_interface.model_providers[model],
            )

            func = cls.inject_dependency(
                func=func,
                arg="standard_params",
                callable_=provider_interface.params[model]["standard"],
            )

            func = cls.inject_dependency(
                func=func,
                arg="extra_params",
                callable_=provider_interface.params[model]["extra"],
            )

            func = cls.inject_return_annotation(
                func=func,
                annotation=provider_interface.return_annotations[model],
            )

        else:
            func = cls.polish_return_schema(func)
            if (
                "provider_choices" in func.__annotations__
                and func.__annotations__["provider_choices"] == ProviderChoices
            ):
                func = cls.inject_dependency(
                    func=func,
                    arg="provider_choices",
                    callable_=provider_interface.provider_choices,
                )

        return func

    @staticmethod
    def polish_return_schema(func: Callable[P, OBBject]) -> Callable[P, OBBject]:
        """通过填充 `__doc__` 和 `__name__` 来完善 API 架构。"""
        return_type = func.__annotations__["return"]
        is_list = False

        if return_type == OBBject:
            results_type = get_type_hints(return_type)["results"]
            results_type_args = get_args(results_type)
            if not isinstance(results_type, type(None)):
                results_type = results_type_args[0]

            is_list = isinstance(get_origin(results_type), list)
            inner_type = (
                results_type_args[0] if is_list and results_type_args else results_type
            )
            inner_type_name = getattr(inner_type, "__name__", inner_type)

            func.__annotations__["return"].__doc__ = "OBBject"
            func.__annotations__["return"].__name__ = f"OBBject[{inner_type_name}]"

        return func

    @staticmethod
    def validate_signature(
        func: Callable[P, OBBject], expected: dict[str, type]
    ) -> None:
        """在绑定到模型之前验证函数签名。"""
        for k, v in expected.items():
            if k not in func.__annotations__:
                raise AttributeError(
                    f"Invalid signature: '{func.__name__}'. Missing '{k}' parameter."
                )

            if func.__annotations__[k] != v:
                raise TypeError(
                    f"Invalid signature: '{func.__name__}'. '{k}' parameter must be of type '{v.__name__}'."
                )

    @staticmethod
    def inject_dependency(
        func: Callable[P, OBBject], arg: str, callable_: Any
    ) -> Callable[P, OBBject]:
        """使用依赖注入注释函数。"""
        func.__annotations__[arg] = Annotated[callable_, Depends()]  # type: ignore
        return func

    @staticmethod
    def inject_return_annotation(
        func: Callable[P, OBBject], annotation: type[OBBject]
    ) -> Callable[P, OBBject]:
        """使用返回注释注释函数。"""
        func.__annotations__["return"] = annotation
        return func

    @staticmethod
    def get_description(func: Callable) -> str:
        """从文档字符串获取描述。"""
        doc = func.__doc__
        if doc:
            description = doc.split("    Parameters\n    ----------")[0]
            description = description.split("    Returns\n    -------")[0]
            description = description.split("    Examples\n    -------")[0]
            description = "\n".join([line.strip() for line in description.split("\n")])

            return description
        return ""

    @staticmethod
    def get_operation_id(func: Callable, sep: str = "_") -> str:
        """获取操作 ID。"""
        operation_id = [
            t.replace("_router", "").replace("openbb_", "")
            for t in func.__module__.split(".") + [func.__name__]
        ]
        cleaned_id = sep.join({c: "" for c in operation_id if c}.keys())
        return cleaned_id


class CommandMap:
    """将路由与命令匹配。"""

    def __init__(
        self, router: Router | None = None, coverage_sep: str | None = None
    ) -> None:
        """初始化 CommandMap。"""
        self._router = router or RouterLoader.from_extensions()
        self._map = self.get_command_map(router=self._router)
        self._provider_coverage: dict[str, list[str]] = {}
        self._command_coverage: dict[str, list[str]] = {}
        self._commands_model: dict[str, str] = {}
        self._coverage_sep = coverage_sep

    @property
    def map(self) -> dict[str, Callable]:
        """获取命令映射。"""
        return self._map

    @property
    def provider_coverage(self) -> dict[str, list[str]]:
        """获取提供者覆盖范围。"""
        if not self._provider_coverage:
            self._provider_coverage = self.get_provider_coverage(
                router=self._router, sep=self._coverage_sep
            )
        return self._provider_coverage

    @property
    def command_coverage(self) -> dict[str, list[str]]:
        """获取命令覆盖范围。"""
        if not self._command_coverage:
            self._command_coverage = self.get_command_coverage(
                router=self._router, sep=self._coverage_sep
            )
        return self._command_coverage

    @property
    def commands_model(self) -> dict[str, str]:
        """获取命令模型。"""
        if not self._commands_model:
            self._commands_model = self.get_commands_model(
                router=self._router, sep=self._coverage_sep
            )
        return self._commands_model

    @staticmethod
    def get_command_map(
        router: Router,
    ) -> dict[str, Callable]:
        """获取命令映射。"""
        api_router = router.api_router
        command_map = {route.path: route.endpoint for route in api_router.routes}  # type: ignore
        return command_map

    @staticmethod
    def get_provider_coverage(
        router: Router, sep: str | None = None
    ) -> dict[str, list[str]]:
        """获取提供者覆盖范围。"""
        api_router = router.api_router

        mapping = ProviderInterface().map

        coverage_map: dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra", None)
            if openapi_extra:
                model = openapi_extra.get("model", None)
                if model:
                    providers = list(mapping[model].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")
                    for provider in providers:
                        if provider not in coverage_map:
                            coverage_map[provider] = []
                        if hasattr(route, "path"):
                            rp = (
                                route.path  # type: ignore
                                if sep is None
                                else route.path.replace("/", sep)  # type: ignore
                            )
                            coverage_map[provider].append(rp)

        return coverage_map

    @staticmethod
    def get_command_coverage(
        router: Router, sep: str | None = None
    ) -> dict[str, list[str]]:
        """获取命令覆盖范围。"""
        api_router = router.api_router

        mapping = ProviderInterface().map

        coverage_map: dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                model = openapi_extra.get("model", None)
                if model:
                    providers = list(mapping[model].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")

                    if hasattr(route, "path"):
                        rp = route.path if sep is None else route.path.replace("/", sep)  # type: ignore
                        if route.path not in coverage_map:  # type: ignore
                            coverage_map[rp] = []
                        coverage_map[rp] = providers
        return coverage_map

    @staticmethod
    def get_commands_model(router: Router, sep: str | None = None) -> dict[str, str]:
        """获取命令模型。"""
        api_router = router.api_router

        coverage_map: dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                model = openapi_extra.get("model", None)
                if model and hasattr(route, "path"):
                    rp = route.path if sep is None else route.path.replace("/", sep)  # type: ignore
                    if route.path not in coverage_map:  # type: ignore
                        coverage_map[rp] = []
                    coverage_map[rp] = model
        return coverage_map

    def get_command(self, route: str) -> Callable | None:
        """从路由获取命令。"""
        return self._map.get(route, None)


class LoadingError(Exception):
    """加载扩展出错。"""


class RouterLoader:
    """路由器加载器。"""

    @staticmethod
    @lru_cache
    def from_extensions() -> Router:
        """从扩展加载路由。"""
        router = Router()

        for name, entry in ExtensionLoader().core_objects.items():  # type: ignore[attr-defined]
            try:
                router.include_router(router=entry, prefix=f"/{name}")
            except Exception as e:
                msg = f"加载扩展出错：{name}\n"
                if Env().DEBUG_MODE:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise LoadingError(msg + f"\033[91m{e}\033[0m") from e
                warnings.warn(
                    message=msg,
                    category=OpenBBWarning,
                )

        return router
