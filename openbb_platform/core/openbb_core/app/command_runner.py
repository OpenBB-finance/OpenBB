"""命令运行器模块。"""

# pylint: disable=R0903
from collections.abc import Callable
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from datetime import datetime
from inspect import Parameter, iscoroutinefunction, signature
from sys import exc_info
from time import perf_counter_ns
from typing import TYPE_CHECKING, Any, Optional
from warnings import catch_warnings, showwarning, warn

from fastapi.encoders import jsonable_encoder
from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning, cast_warning
from openbb_core.app.model.extension import CachedAccessor
from openbb_core.app.model.metadata import Metadata
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams
from openbb_core.app.static.package_builder import PathHandler
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import maybe_coroutine, run_async, to_snake_case
from pydantic import BaseModel, ConfigDict, create_model

if TYPE_CHECKING:
    from fastapi.routing import APIRoute
    from openbb_core.app.model.system_settings import SystemSettings
    from openbb_core.app.model.user_settings import UserSettings
    from openbb_core.app.router import CommandMap


class ExecutionContext:
    """执行上下文。"""

    # 用于检查命令是否在 API 路由中指定了无验证
    _route_map = PathHandler.build_route_map()

    def __init__(
        self,
        command_map: "CommandMap",
        route: str,
        system_settings: "SystemSettings",
        user_settings: "UserSettings",
    ) -> None:
        """初始化执行上下文。"""
        self.command_map = command_map
        self.route = route
        self.system_settings = system_settings
        self.user_settings = user_settings

    @property
    def api_route(self) -> "APIRoute":
        """API 路由。"""
        return self._route_map[self.route]  # type: ignore


class ParametersBuilder:
    """为函数构建参数。"""

    @staticmethod
    def get_polished_parameter_list(func: Callable) -> list[Parameter]:
        """以列表形式获取签名参数值。"""
        sig = signature(func)
        parameter_list = list(sig.parameters.values())

        return parameter_list

    @staticmethod
    def get_polished_func(func: Callable) -> Callable:
        """从函数签名和注释中删除 __authenticated_user_settings。"""
        func = deepcopy(func)
        sig = signature(func)
        parameter_map = dict(sig.parameters)

        if "__authenticated_user_settings" in parameter_map:
            parameter_map.pop("__authenticated_user_settings")

        parameter_list = list(parameter_map.values())
        new_signature = signature(func).replace(parameters=parameter_list)

        func.__signature__ = new_signature  # type: ignore
        func.__annotations__ = parameter_map

        return func

    @classmethod
    def merge_args_and_kwargs(
        cls,
        func: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """将 args 和 kwargs 合并为单个字典。"""
        args = deepcopy(args)
        kwargs_copy = deepcopy(kwargs)
        parameter_list = cls.get_polished_parameter_list(func=func)
        parameter_map = {}

        for index, parameter in enumerate(parameter_list):
            if index < len(args):
                parameter_map[parameter.name] = args[index]
            elif parameter.name in kwargs:
                parameter_map[parameter.name] = kwargs[parameter.name]
            elif parameter.default is not parameter.empty:
                parameter_map[parameter.name] = parameter.default
            else:
                parameter_map[parameter.name] = None

        if "kwargs" in parameter_map:
            merged_kwargs = parameter_map.get("kwargs") or {}
            if not isinstance(merged_kwargs, dict):
                merged_kwargs = dict(merged_kwargs)

            for key, value in kwargs_copy.items():
                if key in {"filter_query", "kwargs"} or key in parameter_map:
                    continue
                merged_kwargs[key] = value

            parameter_map.update(merged_kwargs)
            parameter_map.pop("kwargs", None)

        return parameter_map

    @staticmethod
    def update_command_context(
        func: Callable,
        kwargs: dict[str, Any],
        system_settings: "SystemSettings",
        user_settings: "UserSettings",
    ) -> dict[str, Any]:
        """使用可用的用户和系统设置更新命令上下文。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.command_context import CommandContext

        argcount = func.__code__.co_argcount
        if "cc" in func.__code__.co_varnames[:argcount]:
            kwargs["cc"] = CommandContext(
                user_settings=user_settings,
                system_settings=system_settings,
            )

        return kwargs

    @staticmethod
    def _warn_kwargs(
        extra_params: dict[str, Any],
        model: type[BaseModel],
    ) -> None:
        """如果收到 kwargs 并被验证模型忽略，则发出警告。"""
        # 我们只检查 extra_params 注释，因为被忽略的字段
        # 将始终存在
        annotation = getattr(
            model.model_fields.get("extra_params", None), "annotation", None
        )
        if is_dataclass(annotation) and any(
            t is ExtraParams for t in getattr(annotation, "__bases__", [])
        ):
            valid = asdict(annotation())  # type: ignore
            for p in extra_params:
                if "chart_params" in p:
                    continue
                if p not in valid:
                    warn(
                        message=f"未找到参数 '{p}'。",
                        category=OpenBBWarning,
                    )

    @staticmethod
    def _as_dict(obj: Any) -> dict[str, Any]:
        """安全地将对象转换为字典。"""
        try:
            if isinstance(obj, dict):
                return obj
            return asdict(obj) if is_dataclass(obj) else dict(obj)  # type: ignore
        except Exception:
            return {}

    @staticmethod
    def validate_kwargs(
        func: Callable,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """验证 kwargs，如果可能，强制转换为正确的类型。"""
        sig = signature(func)
        fields: dict[str, tuple[Any, Any]] = {}
        for name, param in sig.parameters.items():
            if param.kind is Parameter.VAR_KEYWORD:
                continue
            annotation = (
                Any if param.annotation is Parameter.empty else param.annotation
            )
            default = ... if param.default is Parameter.empty else param.default
            fields[name] = (annotation, default)
        # 我们允许模型返回包含 'cc: CommandContext' 的额外字段
        config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
        # pylint: disable=C0103
        ValidationModel = create_model(func.__name__, __config__=config, **fields)  # type: ignore
        # Validate and coerce
        model = ValidationModel(**kwargs)
        ParametersBuilder._warn_kwargs(
            ParametersBuilder._as_dict(kwargs.get("extra_params", {})),
            ValidationModel,
        )
        return dict(model)

    # pylint: disable=R0913
    @classmethod
    def build(
        cls,
        args: tuple[Any, ...],
        execution_context: ExecutionContext,
        func: Callable,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """为函数构建参数。"""
        func = cls.get_polished_func(func=func)
        system_settings = execution_context.system_settings
        user_settings = execution_context.user_settings
        kwargs = cls.merge_args_and_kwargs(
            func=func,
            args=args,
            kwargs=kwargs,
        )
        kwargs = cls.update_command_context(
            func=func,
            kwargs=kwargs,
            system_settings=system_settings,
            user_settings=user_settings,
        )
        kwargs = cls.validate_kwargs(
            func=func,
            kwargs=kwargs,
        )
        return kwargs


# pylint: disable=too-few-public-methods
class StaticCommandRunner:
    """静态命令运行器。"""

    @classmethod
    async def _command(
        cls,
        func: Callable,
        kwargs: dict[str, Any],
        show_warnings: bool = True,  # pylint: disable=unused-argument   # type: ignore
    ) -> OBBject:
        """运行命令并返回输出。"""
        obbject = await maybe_coroutine(func, **kwargs)
        if isinstance(obbject, OBBject):
            obbject.provider = getattr(
                kwargs.get("provider_choices"),
                "provider",
                getattr(obbject, "provider", None),
            )
        return obbject

    @classmethod
    def _chart(
        cls,
        obbject: OBBject,
        **kwargs,
    ) -> None:
        """从命令输出创建图表。"""
        try:
            if "charting" not in obbject.accessors:
                raise OpenBBError(
                    "未安装 OpenBB Charting。请安装 `openbb-charting`。"
                )
            # 在这里，我们将弹出 chart_params kwargs 并将它们扁平化到 kwargs 中。
            chart_params = {}
            extra_params = getattr(obbject, "_extra_params", {})

            if extra_params and "chart_params" in extra_params:
                chart_params = extra_params.get("chart_params", {})

            if kwargs.get("chart_params"):
                chart_params.update(kwargs.pop("chart_params", {}))
            # 验证 kwargs 没有被嵌套为 kwargs，这样我们就不会丢失任何图表参数。
            if (
                "kwargs" in kwargs
                and "chart_params" in kwargs["kwargs"]
                and kwargs["kwargs"].get("chart_params")
            ):
                chart_params.update(kwargs.pop("kwargs", {}).get("chart_params", {}))

            if chart_params:
                kwargs.update(chart_params)

            obbject.charting.show(render=False, **kwargs)  # type: ignore[attr-defined]
        except Exception as e:  # pylint: disable=broad-exception-caught
            if Env().DEBUG_MODE:
                raise OpenBBError(e) from e
            warn(str(e), OpenBBWarning)

    @classmethod
    def _extract_params(cls, kwargs, key) -> dict:
        """从 kwargs 中提取参数模型并转换为字典。"""
        params = kwargs.get(key, {})
        if hasattr(params, "__dict__"):
            return params.__dict__
        return params

    # pylint: disable=R0913, R0914
    @classmethod
    async def _execute_func(  # pylint: disable=too-many-positional-arguments
        cls,
        route: str,
        args: tuple[Any, ...],
        execution_context: ExecutionContext,
        func: Callable,
        kwargs: dict[str, Any],
    ) -> OBBject:
        """执行函数并返回输出。"""
        user_settings = execution_context.user_settings
        system_settings = execution_context.system_settings
        raised_warnings: list = []
        custom_headers: dict[str, Any] | None = None

        try:
            with catch_warnings(record=True) as warning_list:
                # 如果我们在 Jupyter 上，我们需要在这里弹出，因为我们将失去 "chart"
                # 在 ParametersBuilder.build 之后。这需要以一种方式修复，以便图表
                # 添加到函数签名中，并在 jupyter 和 api 之间共享
                # 我们可以在路由装饰器中检查给定函数是否在
                # 图表扩展中具有图表，然后我们在那里添加它。这样我们可以移除
                # commands.py 和 package_builder 中的图表参数，它将是
                # 添加到路由装饰器中的函数签名中
                # 如果未使用 ProviderInterface，我们需要传递
                # kwargs 字典的副本，在它被验证之前，否则我们会丢失这些项目。
                kwargs_copy = deepcopy(kwargs)
                chart = kwargs.pop("chart", False)
                kwargs_copy = deepcopy(kwargs)
                kwargs = ParametersBuilder.build(
                    args=args,
                    execution_context=execution_context,
                    func=func,
                    kwargs=kwargs,
                )
                kwargs = kwargs if kwargs is not None else {}
                # 如果 **kwargs 在函数签名中，我们需要确保传递
                # 所有 kwargs 到该函数，以便进行依赖项注入
                # 并且 kwargs 实际上在该函数内作为局部变量可用。
                if "kwargs" in kwargs_copy:
                    for k, v in kwargs_copy["kwargs"].items():
                        if k not in kwargs:
                            kwargs[k] = v
                # 如果我们在 api 上，我们需要在这里移除 "chart"，因为参数是在
                # commands.py 上添加的，并且函数签名不期望 "chart"
                kwargs.pop("chart", None)
                # 我们也弹出自定义标头
                model_headers = system_settings.api_settings.custom_headers or {}
                custom_headers = {
                    name: kwargs.pop(name.replace("-", "_"), default)
                    for name, default in model_headers.items() or {}
                } or None

                obbject = await cls._command(func, kwargs)
                # 输出可能来自带有 'no_validate=True' 的路由器命令
                # 它可能与 OBBject 类型不同。
                # 在这种情况下，我们要避免访问这些属性。
                if isinstance(obbject, OBBject):
                    # 本节准备传递给图表服务的 obbject。
                    obbject._route = route  # pylint: disable=protected-access
                    std_params = cls._extract_params(kwargs, "standard_params") or (
                        kwargs if "data" in kwargs else {}
                    )
                    extra_params = cls._extract_params(kwargs, "extra_params") or kwargs
                    obbject._standard_params = (  # pylint: disable=protected-access
                        std_params
                    )
                    obbject._extra_params = (  # pylint: disable=protected-access
                        extra_params
                    )
                    if chart and obbject.results:
                        if "extra_params" not in kwargs_copy:
                            kwargs_copy["extra_params"] = {}
                        # 恢复任何传递的被 ParametersBuilder 删除的 kwargs
                        for k in kwargs_copy.copy():
                            if k == "chart":
                                kwargs_copy.pop("chart", None)
                                continue
                            if (
                                not extra_params or k not in extra_params
                            ) and k != "extra_params":
                                kwargs_copy["extra_params"][k] = kwargs_copy.pop(
                                    k, None
                                )

                        cls._chart(obbject, **kwargs_copy)

                raised_warnings = warning_list if warning_list else []
        finally:
            if raised_warnings:
                if isinstance(obbject, OBBject):
                    obbject.warnings = []
                for w in raised_warnings:
                    if isinstance(obbject, OBBject):
                        obbject.warnings.append(cast_warning(w))  # type: ignore
                    if user_settings.preferences.show_warnings:
                        showwarning(
                            message=w.message,
                            category=w.category,
                            filename=w.filename,
                            lineno=w.lineno,
                            file=w.file,
                            line=w.line,
                        )

            if system_settings.logging_suppress is False:
                # pylint: disable=import-outside-toplevel
                from openbb_core.app.logs.logging_service import LoggingService

                ls = LoggingService(system_settings, user_settings)
                ls.log(
                    user_settings=user_settings,
                    system_settings=system_settings,
                    route=route,
                    func=func,
                    kwargs=kwargs,
                    exec_info=exc_info(),
                    custom_headers=custom_headers,
                )

        return obbject

    # pylint: disable=W0718
    @classmethod
    async def run(
        cls,
        execution_context: ExecutionContext,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """运行命令并返回 OBBject 作为输出。"""
        timestamp = datetime.now()
        start_ns = perf_counter_ns()

        command_map = execution_context.command_map
        route = execution_context.route

        if func := command_map.get_command(route=route):
            obbject = await cls._execute_func(
                route=route,
                args=args,  # type: ignore
                execution_context=execution_context,
                func=func,
                kwargs=kwargs,
            )
        else:
            raise AttributeError(f"无效命令 : route={route}")

        duration = perf_counter_ns() - start_ns

        if execution_context.user_settings.preferences.metadata and isinstance(
            obbject, OBBject
        ):
            try:
                obbject.extra["metadata"] = Metadata(
                    arguments=kwargs,
                    duration=duration,
                    route=route,
                    timestamp=timestamp,
                )
            except Exception as e:
                if Env().DEBUG_MODE:
                    raise OpenBBError(e) from e
                warn(str(e), OpenBBWarning)

            # 删除嵌入在 kwargs 中的依赖注入对象
            deps = execution_context.api_route.dependencies
            dependency_param_names: set[str] = set()
            if deps:
                for dep in deps:
                    dep_name = getattr(dep.dependency, "__name__", "")
                    dep_name = to_snake_case(dep_name).replace("get_", "")
                    dependency_param_names.add(dep_name)

                for dep_key in dependency_param_names:
                    _ = obbject._extra_params.pop(  # type:ignore  # pylint: disable=W0212
                        dep_key, None
                    )

            meta = getattr(obbject.extra.get("metadata"), "arguments", {})

            # 非提供者端点需要添加执行信息，因为它可能已被丢弃。
            if meta and (
                not meta.get("provider_choices", {})
                and not meta.get("standard_params", {})
                and not meta.get("extra_params", {})
            ):
                for k, v in kwargs.items():
                    if k == "kwargs":
                        for key, value in kwargs["kwargs"].items():
                            if key not in dependency_param_names and value:
                                obbject.extra["metadata"].arguments["extra_params"][
                                    key
                                ] = value
                        continue
                    if k not in dependency_param_names and v:
                        obbject.extra["metadata"].arguments["standard_params"][k] = v

        if isinstance(obbject, OBBject):
            try:
                cls._trigger_command_output_callbacks(route, obbject)
            except Exception as e:
                if Env().DEBUG_MODE:
                    raise OpenBBError(e) from e
                warn(str(e), OpenBBWarning)
            # 我们需要删除已添加到
            # 表示依赖注入的 kwargs 的回调函数
            metadata = obbject.extra.get("metadata")
            if metadata:
                arguments = obbject.extra["metadata"].arguments

                for section in ("standard_params", "extra_params", "provider_choices"):
                    params = arguments.get(section)

                    if not isinstance(params, dict):
                        continue

                    for key, value in params.copy().items():
                        if callable(value) or not value:
                            del obbject.extra["metadata"].arguments[section][key]
                            continue
                        try:
                            jsonable_encoder(value)
                        except (TypeError, ValueError):
                            del obbject.extra["metadata"].arguments[section][key]
                            continue

        return obbject

    @classmethod
    def _trigger_command_output_callbacks(cls, route: str, obbject: OBBject) -> None:
        """触发扩展的命令输出回调。"""
        loader = ExtensionLoader()
        callbacks = loader.on_command_output_callbacks
        if not callbacks:
            return

        # 对于注册所有路由或特定路由的每个扩展，
        # 我们在 OBBject 上调用其访问器。
        # 我们检查访问器是否不可变，以决定是否传递
        # OBBject 的副本或原始副本。
        # 如果任何扩展改变了 OBBject，我们将 _extension_modified 属性设置为 True，
        # 以便我们可以将此信息传递给界面。
        # 如果任何扩展指示仅应返回结果，
        # 我们还将 _results_only 属性设置为 True。
        results_only = False
        executed_keys: set[str] = set()
        ordered_extensions: list = []
        all_on_command_output_exts: list = []

        def _extension_key(ext) -> str:
            if key := getattr(ext, "identifier", None):
                return str(key)
            if path := getattr(ext, "import_path", None):
                return f"{path}:{getattr(ext, 'name', id(ext))}"
            return str(getattr(ext, "name", id(ext)))

        def _clone_for_immutable(source: OBBject) -> OBBject | None:
            try:
                new_source = source.model_copy()
                new_source = OBBject.model_validate(source.model_dump())
                return source.model_validate(new_source)
            except Exception as e:
                warn(
                    "跳过不可变回调，因为 OBBject "
                    f"无法复制。{e}",
                    OpenBBWarning,
                )
                return None

        for ext_list in callbacks.values():
            all_on_command_output_exts.extend(ext_list)

        for ext in callbacks.get("*", []):
            key = _extension_key(ext)
            if key not in executed_keys:
                executed_keys.add(key)
                ordered_extensions.append(ext)

        for ext in callbacks.get(route, []):
            key = _extension_key(ext)
            if key not in executed_keys:
                executed_keys.add(key)
                ordered_extensions.append(ext)

        try:
            for ext in ordered_extensions:
                if ext.results_only is True:
                    results_only = True

                if ext.command_output_paths and route not in ext.command_output_paths:
                    continue

                accessors: set = getattr(type(obbject), "accessors", set())
                if ext.name not in accessors:
                    continue

                descriptor = type(obbject).__dict__.get(ext.name)
                if not isinstance(descriptor, CachedAccessor):
                    continue

                factory = descriptor._accessor  # type: ignore  # pylint: disable=W0212

                target = _clone_for_immutable(obbject) if ext.immutable else obbject

                if target is None:
                    continue

                if iscoroutinefunction(factory):
                    run_async(factory, target)
                else:
                    result = factory(target)
                    if callable(result):
                        result()

                if ext.immutable is False:
                    object.__setattr__(obbject, "_extension_modified", True)

            if results_only is True:
                object.__setattr__(obbject, "_results_only", True)
                object.__setattr__(obbject, "_extension_modified", True)

        except Exception as e:
            raise OpenBBError(e) from e

        for ext in all_on_command_output_exts:
            if ext.name in type(obbject).__dict__:
                object.__setattr__(
                    obbject,
                    ext.name,
                    "访问器在函数执行之外不可调用。",
                )


class CommandRunner:
    """命令运行器。"""

    def __init__(
        self,
        command_map: Optional["CommandMap"] = None,
        system_settings: Optional["SystemSettings"] = None,
        user_settings: Optional["UserSettings"] = None,
    ) -> None:
        """初始化命令运行器。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.router import CommandMap
        from openbb_core.app.service.system_service import SystemService
        from openbb_core.app.service.user_service import UserService

        self._command_map = command_map or CommandMap()
        self._system_settings = system_settings or SystemService().system_settings
        self._user_settings = user_settings or UserService.read_from_file()

    def init_logging_service(self) -> None:
        """初始化日志服务。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.logs.logging_service import LoggingService

        _ = LoggingService(
            system_settings=self._system_settings, user_settings=self._user_settings
        )

    @property
    def command_map(self) -> "CommandMap":
        """命令映射。"""
        return self._command_map

    @property
    def system_settings(self) -> "SystemSettings":
        """系统设置。"""
        return self._system_settings

    @property
    def user_settings(self) -> "UserSettings":
        """用户设置。"""
        return self._user_settings

    @user_settings.setter
    def user_settings(self, user_settings: "UserSettings") -> None:
        self._user_settings = user_settings

    # pylint: disable=W1113
    async def run(
        self,
        route: str,
        user_settings: Optional["UserSettings"] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """运行命令并返回 OBBject 作为输出。"""
        # pylint: disable=import-outside-toplevel

        self._user_settings = user_settings or self._user_settings

        execution_context = ExecutionContext(
            command_map=self._command_map,
            route=route,
            system_settings=self._system_settings,
            user_settings=self._user_settings,
        )

        return await StaticCommandRunner.run(execution_context, *args, **kwargs)

    # pylint: disable=W1113
    def sync_run(
        self,
        route: str,
        user_settings: Optional["UserSettings"] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """运行命令并返回 OBBject 作为输出。"""
        return run_async(self.run, route, user_settings, *args, **kwargs)
