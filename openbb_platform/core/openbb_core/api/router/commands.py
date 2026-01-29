"""Commands：生成命令映射。"""

import inspect
from collections.abc import Callable
from functools import partial, wraps
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, TypeVar, get_args, get_origin

from fastapi import APIRouter, Depends, Header
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends as DependsParam
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic import BaseModel
from typing_extensions import ParamSpec

try:
    from openbb_charting import Charting

    CHARTING_INSTALLED = True
except ImportError:
    CHARTING_INSTALLED = False

T = TypeVar("T")
P = ParamSpec("P")
router = APIRouter(prefix="")


def build_new_annotation_map(sig: Signature) -> dict[str, Any]:
    """构建新的注释映射。"""
    annotation_map = {}
    parameter_list = sig.parameters.values()

    for parameter in parameter_list:
        annotation_map[parameter.name] = parameter.annotation

    annotation_map["return"] = sig.return_annotation

    return annotation_map


def build_new_signature(path: str, func: Callable) -> Signature:
    """构建新的函数签名。"""
    sig = signature(func)
    parameter_list = sig.parameters.values()
    return_annotation = sig.return_annotation
    new_parameter_list: list = []
    var_kw_pos = len(parameter_list)

    for pos, parameter in enumerate(parameter_list):
        if (
            parameter.name == "cc"
            and parameter.annotation == CommandContext
            or parameter.name in ["kwargs", "args", "*", "**", "**kwargs", "*args"]
        ):
            # 我们不会将 kwargs 添加到完成的 API 签名中。
            # Kwargs 将传递给每个接受它们的函数，
            # 但我们不会强制端点接受它们。
            # 我们在包装器中读取原始签名以
            # 确定 kwargs 是否可以传递给局部变量。
            continue

        # 这些是路径参数或依赖注入。
        if parameter.kind == Parameter.VAR_KEYWORD:
            # 我们跟踪 VAR_KEYWORD 参数以在我们通过它之前插入任何额外的
            # 参数，并避免 SyntaxError
            var_kw_pos = pos

        if get_origin(parameter.annotation) is Annotated:
            # 从 Annotated 获取元数据
            metadata = get_args(parameter.annotation)[1:]
            # 检查是否有任何元数据项是 Depends 实例
            if any(isinstance(m, DependsParam) for m in metadata):
                # 在 var_kw_pos 处插入，include_in_schema=False
                new_parameter_list.insert(
                    var_kw_pos,
                    Parameter(
                        parameter.name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=parameter.default,
                        annotation=parameter.annotation,
                    ),
                )
                var_kw_pos += 1
                continue

        new_parameter_list.append(
            Parameter(
                parameter.name,
                kind=parameter.kind,
                default=parameter.default,
                annotation=parameter.annotation,
            )
        )

    if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
        new_parameter_list.insert(
            var_kw_pos,
            Parameter(
                "chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=False,
                annotation=bool,
            ),
        )
        var_kw_pos += 1

    if custom_headers := SystemService().system_settings.api_settings.custom_headers:
        for name, default in custom_headers.items():
            new_parameter_list.insert(
                var_kw_pos,
                Parameter(
                    name.replace("-", "_"),
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=Annotated[str | None, Header(include_in_schema=False)],
                ),
            )
            var_kw_pos += 1

    if Env().API_AUTH:
        new_parameter_list.insert(
            var_kw_pos,
            Parameter(
                "__authenticated_user_settings",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=UserSettings(),
                annotation=Annotated[
                    UserSettings, Depends(AuthService().user_settings_hook)
                ],
            ),
        )
        var_kw_pos += 1

    return Signature(
        parameters=new_parameter_list,
        return_annotation=return_annotation,
    )


def validate_output(c_out: OBBject) -> OBBject:
    """
    验证 OBBject 对象。

    根据 OBBject 架构进行检查，并删除包含
    `exclude_from_api` 额外 `pydantic.Field` kwarg 的字段。
    请注意，对 `OBBject` 对象的修改是就地完成的。

    Parameters
    ----------
    c_out : OBBject
        OBBject object to validate.

    Returns
    -------
    Dict
        Serialized OBBject.
    """

    def is_model(type_):
        return inspect.isclass(type_) and issubclass(type_, BaseModel)

    def exclude_fields_from_api(key: str, value: Any):
        type_ = type(value)
        field = getattr(type(c_out), "model_fields", {}).get(key, None)
        json_schema_extra = field.json_schema_extra if field else None

        # 第一层字段需要被排除的情况
        if (
            json_schema_extra
            and isinstance(json_schema_extra, dict)
            and json_schema_extra.get("exclude_from_api", None)
        ):
            delattr(c_out, key)

        # 如果它是具有嵌套字段的模型
        elif is_model(type_):
            for field_name, field in type_.model_fields.items():
                extra = getattr(field, "json_schema_extra", None)
                if (
                    extra
                    and isinstance(extra, dict)
                    and extra.get("exclude_from_api", None)
                ):
                    delattr(value, field_name)

                # 如果它是一个嵌套模型，我们需要深入递归
                elif is_model(getattr(field, "annotation", None)):
                    exclude_fields_from_api(field_name, getattr(value, field_name))

    # 让非 OBBject 对象通过而不进行验证
    if not isinstance(c_out, OBBject):
        return c_out

    for k, v in c_out.model_copy():
        exclude_fields_from_api(k, v)

    return c_out


def build_api_wrapper(
    command_runner: CommandRunner,
    route: APIRoute,
) -> Callable:
    """为命令构建 API 包装器。"""
    func: Callable = route.endpoint  # type: ignore
    path: str = route.path  # type: ignore
    original_signature = signature(func)
    has_var_kwargs = any(
        param.kind == Parameter.VAR_KEYWORD
        for param in original_signature.parameters.values()
    )
    no_validate = (
        openapi_extra.get("no_validate")
        if (openapi_extra := getattr(route, "openapi_extra", None))
        else None
    )
    new_signature = build_new_signature(path=path, func=func)
    new_annotations_map = build_new_annotation_map(sig=new_signature)
    func.__signature__ = new_signature  # type: ignore
    func.__annotations__ = new_annotations_map

    if no_validate is True:
        route.response_model = None

    @wraps(wrapped=func)
    async def wrapper(  # pylint: disable=R0914,R0912  # noqa: PLR0912
        *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> OBBject | JSONResponse:
        user_settings: UserSettings = UserSettings.model_validate(
            kwargs.pop(
                "__authenticated_user_settings",
                UserService.read_from_file(),
            )
        )
        p = path.strip("/").replace("/", ".")
        defaults = (
            getattr(user_settings.defaults, "__dict__", {})
            .get("commands", {})
            .get(p, {})
        )
        standard_params = getattr(kwargs.pop("standard_params", None), "__dict__", {})
        extra_params = getattr(kwargs.pop("extra_params", None), "__dict__", {})

        if defaults:
            _ = defaults.pop("provider", None)

            if "chart" in defaults:
                kwargs["chart"] = defaults.pop("chart", False)

            if "chart_params" in defaults:
                extra_params["chart_params"] = defaults.pop("chart_params", {})

            for k, v in defaults.items():
                if k in standard_params and standard_params[k] is None:
                    standard_params[k] = v
                elif (k in standard_params and standard_params[k] is not None) or (
                    k in extra_params and extra_params[k] is not None
                ):
                    continue
                elif k not in extra_params or (
                    k in extra_params and extra_params[k] is None
                ):
                    extra_params[k] = v

        kwargs["standard_params"] = standard_params
        kwargs["extra_params"] = extra_params

        # 我们需要插入那些已在
        # 路由器级别添加的对象，这些对象可能不是
        # 函数签名的一部分。
        dependencies = route.dependencies or []
        dep_names: list = []
        # 仅当端点接受未定义参数时
        # 才注入依赖项。
        if has_var_kwargs and "kwargs" not in kwargs:
            kwargs["kwargs"] = {}

        for dep in dependencies:
            dep_callable = dep.dependency

            if not dep_callable:
                continue

            dep_name = getattr(dep_callable, "__name__", "") or ""
            dep_name = to_snake_case(dep_name).replace("get_", "")

            if has_var_kwargs and dep_name not in kwargs:
                kwargs["kwargs"][dep_name] = dep_callable()

            dep_names.append(dep_name)

        execute = partial(command_runner.run, path, user_settings)

        output = await execute(*args, **kwargs)

        if isinstance(output, OBBject):
            # 这是我们检查 `on_command_output` 扩展的地方
            mutated_output = getattr(output, "_extension_modified", False)
            results_only = getattr(output, "_results_only", False)
            try:
                if results_only is True:
                    content = output.model_dump(
                        exclude_unset=True, exclude_none=True
                    ).get("results", [])

                    return JSONResponse(
                        content=jsonable_encoder(content), status_code=200
                    )

                if (mutated_output and isinstance(output, OBBject)) or (
                    isinstance(output, OBBject) and no_validate
                ):
                    output.results = output.model_dump(
                        exclude_unset=True, exclude_none=True
                    ).get("results")

                    return JSONResponse(
                        content=jsonable_encoder(output), status_code=200
                    )
            except Exception as exc:  # pylint: disable=W0703
                raise OpenBBError(
                    f"Error serializing output for an extension-modified endpoint {path}: {exc}",
                ) from exc

            if not no_validate:
                return validate_output(output)

        return output

    return wrapper


def add_command_map(command_runner: CommandRunner, api_router: APIRouter) -> None:
    """将命令映射添加到 API 路由器。"""
    plugins_router = RouterLoader.from_extensions()

    for route in plugins_router.api_router.routes:
        route.endpoint = build_api_wrapper(command_runner=command_runner, route=route)  # type: ignore # noqa
    api_router.include_router(router=plugins_router.api_router)


system_settings = SystemService(logging_sub_app="api").system_settings
command_runner_instance = CommandRunner(system_settings=system_settings)
add_command_map(command_runner=command_runner_instance, api_router=router)
