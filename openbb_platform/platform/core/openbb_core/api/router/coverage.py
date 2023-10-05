from fastapi import APIRouter, Depends
from openbb_core.api.dependency.coverage import get_command_map
from openbb_core.app.router import CommandMap
from typing_extensions import Annotated

router = APIRouter(prefix="/coverage", tags=["Coverage"])


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
