"""Coverage API router."""

from fastapi import APIRouter, Depends
from openbb_core.api.dependency.coverage import get_command_map, get_provider_interface
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap
from typing_extensions import Annotated

router = APIRouter(prefix="/coverage", tags=["Coverage"])


@router.get("/command_model")
async def get_commands_model_map(
    command_map: Annotated[CommandMap, Depends(get_command_map)],
    provider_interface: Annotated[ProviderInterface, Depends(get_provider_interface)],
):
    """Get the command to model mapping."""
    return {
        command: provider_interface.map[command_map.commands_model[command][0]]
        for command in command_map.commands_model
    }


@router.get("/providers")
async def get_provider_coverage(
    command_map: Annotated[CommandMap, Depends(get_command_map)]
):
    """Get provider coverage."""
    return command_map.provider_coverage


@router.get("/commands")
async def get_command_coverage(
    command_map: Annotated[CommandMap, Depends(get_command_map)]
):
    """Get command coverage."""
    return command_map.command_coverage
