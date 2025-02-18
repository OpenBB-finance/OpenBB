"""Coverage API router."""

import json

from fastapi import APIRouter, Depends
from openbb_core.api.dependency.coverage import get_command_map, get_provider_interface
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap
from typing_extensions import Annotated

router = APIRouter(prefix="/coverage", tags=["Coverage"])


@router.get("/command_model", openapi_extra={"widget_config": {"exclude": True}})
async def get_commands_model_map(
    command_map: Annotated[CommandMap, Depends(get_command_map)],
    provider_interface: Annotated[ProviderInterface, Depends(get_provider_interface)],
):
    """Get the command to provider model mapping."""

    commands_map: dict = {}

    for command in command_map.commands_model:
        model = command_map.commands_model[command]
        pi_command = provider_interface.map[model]
        schema = provider_interface.return_annotations[model]
        providers = list(pi_command)
        new_command: dict = {}
        new_command["response_schema_name"] = schema.__name__ if schema else None
        for provider in providers:
            new_command[provider] = {
                "QueryParams": {"docstring": "", "fields": {}},
                "Data": {"docstring": "", "fields": {}},
            }
            p = pi_command[provider]
            query = p.get("QueryParams", {})
            query_fields = query.get("fields", {})
            data = p.get("Data", {})
            data_fields = data.get("fields", {})

            for field, field_info in query_fields.items():
                attributes = (
                    field_info._attributes_set  # pylint: disable=protected-access
                )
                if attributes.get("annotation"):
                    _annotation = str(attributes.get("annotation"))
                    attributes["annotation"] = _annotation

                new_command[provider]["QueryParams"]["fields"][field] = attributes

            new_command[provider]["QueryParams"]["docstring"] = query.get("docstring")

            for field, field_info in data_fields.items():
                attributes = (
                    field_info._attributes_set  # pylint: disable=protected-access
                )
                if attributes.get("annotation"):
                    _annotation = str(attributes.get("annotation"))
                    attributes["annotation"] = _annotation
                new_command[provider]["Data"]["fields"][field] = attributes

            new_command[provider]["Data"]["docstring"] = data.get("docstring")

            if openbb_info := new_command.get("openbb", {}):
                for key in list(new_command):
                    if key == "response_schema_name":
                        continue

                    if obb_params := openbb_info.get("QueryParams", {}).get(
                        "fields", {}
                    ):
                        old_fields = new_command[key]["QueryParams"].get("fields", {})
                        new_command[key]["QueryParams"]["fields"] = {
                            **obb_params,
                            **old_fields,
                        }
                    if obb_data := openbb_info.get("Data", {}).get("fields", {}):
                        old_fields = new_command[key]["Data"].get("fields", {})
                        new_command[key]["Data"]["fields"] = {**obb_data, **old_fields}
        _ = new_command.pop("openbb")
        commands_map[command] = new_command

    def serializer(obj):
        """Serialize the object."""
        if isinstance(obj, type):
            return str(obj)
        return obj

    return json.loads(json.dumps(commands_map, default=serializer, indent=4))


@router.get("/providers", openapi_extra={"widget_config": {"exclude": True}})
async def get_provider_coverage(
    command_map: Annotated[CommandMap, Depends(get_command_map)]
):
    """Get command coverage by provider."""
    return command_map.provider_coverage


@router.get("/commands", openapi_extra={"widget_config": {"exclude": True}})
async def get_command_coverage(
    command_map: Annotated[CommandMap, Depends(get_command_map)]
):
    """Get provider coverage by command."""
    return command_map.command_coverage
