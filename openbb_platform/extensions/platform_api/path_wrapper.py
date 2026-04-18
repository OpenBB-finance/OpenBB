"""Wrapper to handle converting path parameters to query parameter endpoints.

These helpers modify the app instance to add a new route that mirrors the path
parameter endpoints and converts them to URL query parameters.

To use, call the function before generating OpenAPI JSON spec.
It will return the widget_exclude_filter to prevent duplicate widgets
from generating for the function.

>>> widget_exclude_filter = register_path_query_wrappers(app, widget_exclude_filter)
"""

from typing import Any
from urllib.parse import urlencode

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRoute
from pydantic import Field, create_model


def _build_query_wrapper_path(route: APIRoute) -> str:
    segments = [seg for seg in route.path.strip("/").split("/") if seg]
    base_segments = []
    for segment in segments:
        if segment.startswith("{"):
            break
        base_segments.append(segment)
    if not base_segments:
        fallback = (route.name or "query").replace(" ", "_")
        return f"/{fallback}"
    return "/" + "/".join(base_segments)


def _create_path_parameter_query_wrapper(route: APIRoute):
    handler = route.get_route_handler()
    path_params = list(route.dependant.path_params)
    query_model_name = "".join(part.capitalize() for part in (route.name or "wrapper").split("_")) + "QueryParams"

    model_fields = {}
    for param in path_params:
        annotation = getattr(param, "outer_type_", None) or getattr(param, "type_", None) or str
        if annotation is Any:
            annotation = str

        field_kwargs = {}
        field_info = getattr(param, "field_info", None)
        if field_info:
            if getattr(field_info, "description", None):
                field_kwargs["description"] = field_info.description
            if getattr(field_info, "title", None):
                field_kwargs["title"] = field_info.title
            if getattr(field_info, "example", None) is not None:
                field_kwargs["example"] = field_info.example
            if getattr(field_info, "examples", None):
                field_kwargs["examples"] = field_info.examples

        default = param.default if not param.required else ...
        model_fields[param.alias] = (
            annotation,
            Field(default=default, alias=param.alias, **field_kwargs),
        )

    QueryParamsModel = create_model(query_model_name, **model_fields)

    async def wrapper(request: Request, query_params: QueryParamsModel = Depends()):
        path_values = query_params.model_dump() if hasattr(query_params, "model_dump") else query_params.dict()

        missing = [name for name in path_values if path_values[name] is None]
        if missing:
            detail = [
                {
                    "loc": ["query", name],
                    "msg": "Field required",
                    "type": "value_error.missing",
                }
                for name in missing
            ]
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

        remaining_query_items = [
            (key, value) for key, value in request.query_params.multi_items() if key not in path_values
        ]

        scope = dict(request.scope)
        scope["path_params"] = path_values
        path_template = getattr(route, "path_format", route.path)
        target_path = path_template.format(**path_values)
        scope["path"] = target_path
        scope["raw_path"] = target_path.encode("utf-8")
        scope["matched_path"] = route.path
        scope["endpoint"] = route.endpoint
        scope["route"] = route
        scope["query_string"] = (
            urlencode(remaining_query_items, doseq=True).encode("utf-8") if remaining_query_items else b""
        )

        forward_request = Request(scope, request.receive)
        return await handler(forward_request)

    endpoint = route.endpoint
    wrapper.__name__ = getattr(endpoint, "__name__", route.name or "wrapper")
    wrapper.__doc__ = getattr(endpoint, "__doc__", None)
    return wrapper


def register_path_query_wrappers(api_app, widget_exclusions=None):
    widget_exclusions = widget_exclusions or []

    existing_paths = {getattr(route, "path", None) for route in api_app.router.routes if hasattr(route, "path")}
    existing_paths = {path for path in existing_paths if path}

    for route in list(api_app.router.routes):
        if not isinstance(route, APIRoute) or not route.dependant.path_params:
            continue

        wrapper_path = _build_query_wrapper_path(route)
        candidate = wrapper_path
        suffix = 1
        while candidate in existing_paths:
            suffix += 1
            candidate = f"{wrapper_path.rstrip('/')}-{suffix}"
        existing_paths.add(candidate)

        if route.path not in widget_exclusions:
            widget_exclusions.append(route.path)

        publish_in_schema = route.include_in_schema
        route.include_in_schema = False
        methods = sorted(route.methods) if route.methods else None

        api_app.router.add_api_route(
            path=candidate,
            endpoint=_create_path_parameter_query_wrapper(route),
            methods=methods,
            name=route.name,
            response_class=route.response_class,
            status_code=route.status_code,
            tags=route.tags,
            dependencies=route.dependencies,
            summary=route.summary,
            description=route.description,
            response_model=route.response_model,
            responses=route.responses,
            deprecated=route.deprecated,
            include_in_schema=publish_in_schema,
            operation_id=route.operation_id,
        )

    return widget_exclusions
