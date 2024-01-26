"""Coverage API router helper functions."""

from inspect import _empty, signature
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Type

from openbb_core.app.provider_interface import ProviderInterface
from pydantic import BaseModel, Field, create_model

if TYPE_CHECKING:
    from openbb_core.app.static.app_factory import BaseApp

provider_interface = ProviderInterface()


def get_route_callable(app: "BaseApp", route: str) -> Callable:
    """Get the callable for a route."""
    # TODO: Add return typing Optional[Callable] to this function. First need to
    # figure how to do that starting from "BaseApp" and account for the possibility
    # of a route not existing. Then remove the type: ignore from the function.

    split_route = route.replace(".", "/").split("/")[1:]

    return_callable = app

    for route_path in split_route:
        return_callable = getattr(return_callable, route_path)

    return return_callable  # type: ignore


def signature_to_fields(app: "BaseApp", route: str) -> Dict[str, Tuple[Any, Field]]:  # type: ignore
    """Convert a command signature to pydantic fields."""
    return_callable = get_route_callable(app, route)
    sig = signature(return_callable)

    fields = {}
    for name, param in sig.parameters.items():
        if name not in ["kwargs", "args"]:
            type_annotation = (
                param.annotation if param.annotation is not _empty else Any
            )
            description = (
                param.annotation.__metadata__[0].description
                if hasattr(param.annotation, "__metadata__")
                else None
            )
            fields[name] = (
                type_annotation,
                Field(..., title="openbb", description=description),
            )

    return fields


def dataclass_to_fields(model_name: str) -> Dict[str, Tuple[Any, Field]]:  # type: ignore
    """Convert a dataclass to pydantic fields."""
    dataclass = provider_interface.params[model_name]["extra"]
    fields = {}
    for name, field in dataclass.__dataclass_fields__.items():
        type_annotation = field.default.annotation if field.default is not None else Any  # type: ignore
        description = field.default.description if field.default is not None else None  # type: ignore
        title = field.default.title if field.default is not None else None  # type: ignore
        fields[name] = (
            type_annotation,
            Field(..., title=title, description=description),
        )

    return fields


def create_combined_model(
    model_name: str,
    *field_sets: Dict[str, Tuple[Any, Field]],  # type: ignore
    filter_by_provider: Optional[str] = None,
) -> Type[BaseModel]:
    """Create a combined pydantic model."""
    combined_fields = {}
    for fields in field_sets:
        for name, (type_annotation, field) in fields.items():
            if (
                filter_by_provider is None
                or "openbb" in field.title  # type: ignore
                or (filter_by_provider in field.title)  # type: ignore
            ):
                combined_fields[name] = (type_annotation, field)

    model = create_model(model_name, **combined_fields)  # type: ignore

    # # Clean up the metadata
    for field in model.model_fields.values():
        if hasattr(field, "metadata"):
            field.metadata = None  # type: ignore

    return model


def get_route_schema_map(
    app: "BaseApp",
    command_model_map: Dict[str, str],
    filter_by_provider: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Get the route schema map."""
    route_schema_map = {}
    for route, model in command_model_map.items():
        input_model = create_combined_model(
            route,
            signature_to_fields(app, route),
            dataclass_to_fields(model),
            filter_by_provider=filter_by_provider,
        )
        output_model = provider_interface.return_schema[model]
        return_callable = get_route_callable(app, route)

        route_schema_map[route] = {
            "input": input_model,
            "output": output_model,
            "callable": return_callable,
        }

    return route_schema_map
