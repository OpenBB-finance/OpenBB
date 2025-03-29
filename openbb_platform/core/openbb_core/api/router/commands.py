"""Commands: generates the command map."""

import inspect
from functools import partial, wraps
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from fastapi import APIRouter, Depends, Header
from fastapi.routing import APIRoute
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.auth_service import AuthService
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService
from openbb_core.env import Env
from pydantic import BaseModel
from typing_extensions import Annotated, ParamSpec

try:
    from openbb_charting import Charting

    CHARTING_INSTALLED = True
except ImportError:
    CHARTING_INSTALLED = False

T = TypeVar("T")
P = ParamSpec("P")

router = APIRouter(prefix="")


def build_new_annotation_map(sig: Signature) -> Dict[str, Any]:
    """Build new annotation map."""
    annotation_map = {}
    parameter_list = sig.parameters.values()

    for parameter in parameter_list:
        annotation_map[parameter.name] = parameter.annotation

    annotation_map["return"] = sig.return_annotation

    return annotation_map


def build_new_signature(path: str, func: Callable) -> Signature:
    """Build new function signature."""
    sig = signature(func)
    parameter_list = sig.parameters.values()
    return_annotation = sig.return_annotation
    new_parameter_list = []
    var_kw_pos = len(parameter_list)
    for pos, parameter in enumerate(parameter_list):
        if parameter.name == "cc" and parameter.annotation == CommandContext:
            continue

        if parameter.kind == Parameter.VAR_KEYWORD:
            # We track VAR_KEYWORD parameter to insert the any additional
            # parameters we need to add before it and avoid a SyntaxError
            var_kw_pos = pos

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
                    annotation=Annotated[
                        Optional[str], Header(include_in_schema=False)
                    ],
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
    Validate OBBject object.

    Checks against the OBBject schema and removes fields that contain the
    `exclude_from_api` extra `pydantic.Field` kwarg.
    Note that the modification to the `OBBject` object is done in-place.

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
        field = c_out.model_fields.get(key, None)
        json_schema_extra = field.json_schema_extra if field else None

        # case where 1st layer field needs to be excluded
        if (
            json_schema_extra
            and isinstance(json_schema_extra, dict)
            and json_schema_extra.get("exclude_from_api", None)
        ):
            delattr(c_out, key)

        # if it's a model with nested fields
        elif is_model(type_):
            for field_name, field in type_.model_fields.items():
                extra = getattr(field, "json_schema_extra", None)
                if (
                    extra
                    and isinstance(extra, dict)
                    and extra.get("exclude_from_api", None)
                ):
                    delattr(value, field_name)

                # if it's a yet a nested model we need to go deeper in the recursion
                elif is_model(getattr(field, "annotation", None)):
                    exclude_fields_from_api(field_name, getattr(value, field_name))

    # Let a non-OBBject object pass through without validation
    if not isinstance(c_out, OBBject):
        return c_out

    for k, v in c_out.model_copy():
        exclude_fields_from_api(k, v)

    return c_out


def build_api_wrapper(
    command_runner: CommandRunner,
    route: APIRoute,
) -> Callable:
    """Build API wrapper for a command."""
    func: Callable = route.endpoint  # type: ignore
    path: str = route.path  # type: ignore

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
    async def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> OBBject:
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

        if defaults:
            _provider = defaults.pop("provider", None)
            standard_params = getattr(
                kwargs.pop("standard_params", None), "__dict__", {}
            )
            extra_params = getattr(kwargs.pop("extra_params", None), "__dict__", {})

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

        execute = partial(command_runner.run, path, user_settings)
        output = await execute(*args, **kwargs)

        if isinstance(output, OBBject) and not no_validate:
            return validate_output(output)

        return output

    return wrapper


def add_command_map(command_runner: CommandRunner, api_router: APIRouter) -> None:
    """Add command map to the API router."""
    plugins_router = RouterLoader.from_extensions()

    for route in plugins_router.api_router.routes:
        route.endpoint = build_api_wrapper(command_runner=command_runner, route=route)  # type: ignore # noqa
    api_router.include_router(router=plugins_router.api_router)


system_settings = SystemService(logging_sub_app="api").system_settings
command_runner_instance = CommandRunner(system_settings=system_settings)
add_command_map(command_runner=command_runner_instance, api_router=router)
