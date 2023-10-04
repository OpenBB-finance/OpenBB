"""Coverage dependency."""

from fastapi import Depends
from openbb_core.app.router import CommandMap
from openbb_core.app.service.auth_service import AuthService
from typing_extensions import Annotated


async def get_command_map(
    _: Annotated[None, Depends(AuthService().auth_hook)]
) -> CommandMap:
    """Get command map."""
    return CommandMap()
