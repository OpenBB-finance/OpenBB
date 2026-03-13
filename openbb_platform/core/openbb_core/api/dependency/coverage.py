"""Coverage dependency."""

from typing import Annotated

from fastapi import Depends
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap
from openbb_core.app.service.auth_service import AuthService


async def get_command_map(
    _: Annotated[None, Depends(AuthService().auth_hook)],
) -> CommandMap:
    """Get command map."""
    return CommandMap()


async def get_provider_interface(
    _: Annotated[None, Depends(AuthService().auth_hook)],
) -> ProviderInterface:
    """Get provider interface."""
    return ProviderInterface()
