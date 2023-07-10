from typing import Dict, List

from fastapi import APIRouter
from openbb_sdk_core.app.router import CommandMap

router = APIRouter(prefix="/coverage", tags=["Coverage"])


@router.get("/providers")
async def get_provider_coverage() -> Dict[str, List[str]]:
    return CommandMap().provider_coverage


@router.get("/commands")
async def get_command_coverage() -> Dict[str, List[str]]:
    return CommandMap().command_coverage
