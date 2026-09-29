"""Behavioral tests for ``openbb_core.api.router.system``.

The original test mocked ``get_system_settings`` and asserted
``response`` truthy. The handler is a pass-through, so the only
contract worth testing is *exact identity*: whatever the dependency
yields must be returned verbatim, with no copy or wrapping.
"""

import asyncio

from openbb_core.api.router.system import get_system_model
from openbb_core.app.model.system_settings import SystemSettings


def test_get_system_model_returns_injected_settings_unchanged():
    """``get_system_model`` is a pass-through over the injected ``SystemSettings``."""
    settings = SystemSettings()

    result = asyncio.run(get_system_model(settings))

    assert result is settings


def test_get_system_model_round_trips_arbitrary_subclass_attribute():
    """The handler does not strip dynamically-added attributes off the settings object."""
    settings = SystemSettings()
    # ``SystemSettings`` is a pydantic model with ``extra='ignore'`` by default,
    # but ``__dict__`` mutation works for attribute identity assertions.
    object.__setattr__(settings, "_test_marker", "behavioral-marker-7f")

    result = asyncio.run(get_system_model(settings))

    assert getattr(result, "_test_marker", None) == "behavioral-marker-7f"
