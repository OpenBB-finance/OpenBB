from functools import partial, wraps
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, Callable, Dict, Tuple, TypeVar

from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from openbb_core.api.dependency.user import get_user
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.system_service import SystemService
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")

router = APIRouter(prefix="")


def build_new_annotation_map(sig: Signature) -> Dict[str, Any]:
    annotation_map = {}
    parameter_list = sig.parameters.values()

    for parameter in parameter_list:
        annotation_map[parameter.name] = parameter.annotation

    annotation_map["return"] = sig.return_annotation

    return annotation_map


def build_new_signature(func):
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

    new_parameter_list.append(
        Parameter(
            "chart",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            default=False,
            annotation=bool,
        )
    )

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


def build_api_wrapper(
    command_runner: CommandRunner,
    route: APIRoute,
) -> Callable:
    func: Callable = route.endpoint  # type: ignore
    path: str = route.path  # type: ignore

    new_signature = build_new_signature(func=func)
    new_annotations_map = build_new_annotation_map(sig=new_signature)

    func.__signature__ = new_signature  # type: ignore
    func.__annotations__ = new_annotations_map

    @wraps(wrapped=func)
    def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]):
        user_settings: UserSettings = UserSettings.parse_obj(
            kwargs.pop(
                "__authenticated_user_settings",
                SystemService.read_default_system_settings(),
            )
        )
        execute = partial(command_runner.run_once, user_settings, path)
        journal_entry = execute(*args, **kwargs)

        return journal_entry.output

    return wrapper


def add_command_map(command_runner: CommandRunner, api_router: APIRouter) -> None:
    plugins_router = RouterLoader.from_extensions()

    for route in plugins_router.api_router.routes:
        route.endpoint = build_api_wrapper(command_runner=command_runner, route=route)  # type: ignore # noqa

    api_router.include_router(router=plugins_router.api_router)


system_settings = SystemService.read_default_system_settings()
command_runner_instance = CommandRunner(system_settings=system_settings)
add_command_map(command_runner=command_runner_instance, api_router=router)
