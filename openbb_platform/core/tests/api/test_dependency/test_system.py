"""Behavioral tests for ``openbb_core.api.dependency.system``.

The original test built a mock ``SystemService``, stuffed a ``SystemSettings()``
into ``return_value.system_settings`` and asserted truthiness. That's the
mock talking to itself. This rewrite asserts the dependency returns the
*actual* settings object owned by the service singleton.
"""

import asyncio

from openbb_core.api.dependency.system import (
    SystemSettings,
    get_system_service,
    get_system_settings,
)
from openbb_core.app.service.system_service import SystemService


def test_get_system_service_returns_real_singleton():
    """``get_system_service`` produces a real ``SystemService`` instance."""
    service = asyncio.run(get_system_service())
    assert isinstance(service, SystemService)
    assert isinstance(service.system_settings, SystemSettings)


def test_get_system_settings_returns_settings_owned_by_service():
    """The dependency must return the *exact* object exposed by ``SystemService.system_settings``."""
    service = SystemService()
    result = asyncio.run(get_system_settings(None, service))  # type: ignore[arg-type]

    # Identity, not just equality — the API must not copy or wrap the settings.
    assert result is service.system_settings
    assert isinstance(result, SystemSettings)
    # Sanity: the settings expose the contract used by ``rest_api.py`` to
    # build the FastAPI app.
    assert hasattr(result, "version")
    assert hasattr(result, "api_settings")
