from copy import deepcopy

from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.service.system_service import SystemService

__system_service = SystemService()


async def get_system_settings() -> SystemSettings:
    global __system_service  # noqa: PLW0602  # pylint: disable=global-variable-not-assigned
    return deepcopy(__system_service.system_settings)


def get_system_settings_sync() -> SystemSettings:
    global __system_service  # noqa: PLW0602  # pylint: disable=global-variable-not-assigned
    return __system_service.system_settings


async def get_system_service() -> SystemService:
    global __system_service  # noqa: PLW0602  # pylint: disable=global-variable-not-assigned
    return __system_service
