import inspect
from functools import partial, wraps
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Dict, Tuple, TypeVar

from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from openbb_core.api.dependency.user import get_user
from openbb_core.app.charting_service import ChartingService
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService
from openbb_core.env import Env
from pydantic import BaseModel
from typing_extensions import Annotated, ParamSpec

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

    for parameter in parameter_list:
        if parameter.name == "cc" and parameter.annotation == CommandContext:
            continue

        new_parameter_list.append(
            Parameter(
                parameter.name,
                kind=parameter.kind,
                default=parameter.default,
                annotation=parameter.annotation,
            )
        )

    if (
        path.replace("/", "_")[1:]
        in ChartingService.get_implemented_charting_functions()
    ):
        new_parameter_list.append(
            Parameter(
                "chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=False,
                annotation=bool,
            )
        )

    if Env().API_AUTH:
        new_parameter_list.append(
            Parameter(
                "__authenticated_user_settings",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=UserSettings(),
                annotation=Annotated[UserSettings, Depends(get_user)],
            )
        )

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
    OBBject
        Validated OBBject object.
    """

    def is_model(type_):
        return inspect.isclass(type_) and issubclass(type_, BaseModel)

    def exclude_fields_from_api(key: str, value: Any):
        type_ = type(value)

        # case where 1st layer field needs to be excluded
        if key in c_out.__fields__ and c_out.__fields__[key].field_info.extra.get(
            "exclude_from_api", None
        ):
            delattr(c_out, key)

        # if it's a model with nested fields
        elif is_model(type_):
            for field in type_.__fields__.values():
                if field.field_info.extra.get("exclude_from_api", None):
                    delattr(value, field.name)

                # if it's a yet a nested model we need to go deeper in the recursion
                elif is_model(field.type_):
                    exclude_fields_from_api(field.name, getattr(value, field.name))

    for k, v in c_out:
        exclude_fields_from_api(k, v)

    return c_out


def build_api_wrapper(
    command_runner: CommandRunner,
    route: APIRoute,
) -> Callable:
    """Build API wrapper for a command."""
    func: Callable = route.endpoint  # type: ignore
    path: str = route.path  # type: ignore

    new_signature = build_new_signature(path=path, func=func)
    new_annotations_map = build_new_annotation_map(sig=new_signature)

    func.__signature__ = new_signature  # type: ignore
    func.__annotations__ = new_annotations_map

    @wraps(wrapped=func)
    def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]):
        user_settings: UserSettings = UserSettings.parse_obj(
            kwargs.pop(
                "__authenticated_user_settings",
                UserService.read_default_user_settings(),
            )
        )
        execute = partial(command_runner.run, path, user_settings)
        output: OBBject = execute(*args, **kwargs)

        return validate_output(output)

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
