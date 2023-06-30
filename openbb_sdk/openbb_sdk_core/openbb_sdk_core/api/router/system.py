from typing import Annotated

from fastapi import APIRouter, Depends
from openbb_sdk_core.api.dependency.system import get_system_settings
from openbb_sdk_core.app.model.system_settings import SystemSettings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("")
async def get_system_model(
    system_settings: Annotated[SystemSettings, Depends(get_system_settings)],
) -> SystemSettings:
    return system_settings
