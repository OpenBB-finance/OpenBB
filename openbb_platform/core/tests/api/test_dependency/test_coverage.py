"""Behavioral tests for ``openbb_core.api.dependency.coverage``.

The original test asserted only ``assert response`` after calling
``get_command_map`` — a truthy check on a populated dict, which means
the test passed even if the function returned the wrong dict. This
rewrite verifies the dependency returns the *real* ``CommandMap`` /
``ProviderInterface`` objects with the expected attribute surfaces.
"""

import asyncio

from openbb_core.api.dependency.coverage import (
    get_command_map,
    get_provider_interface,
)
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap


def test_get_command_map_returns_real_command_map_instance():
    """The dependency yields a real ``CommandMap`` exposing the documented attrs."""
    result = asyncio.run(get_command_map(None))  # type: ignore[arg-type]
    assert isinstance(result, CommandMap)
    # All three attributes are dicts even when the registry is empty.
    assert isinstance(result.provider_coverage, dict)
    assert isinstance(result.command_coverage, dict)
    assert isinstance(result.commands_model, dict)


def test_get_provider_interface_returns_real_provider_interface_instance():
    """The dependency yields a real ``ProviderInterface`` (singleton) with the expected dicts."""
    result = asyncio.run(get_provider_interface(None))  # type: ignore[arg-type]
    assert isinstance(result, ProviderInterface)
    # ``map`` and ``return_annotations`` are the contract used by the
    # ``/coverage/command_model`` endpoint.
    assert isinstance(result.map, dict)
    assert isinstance(result.return_annotations, dict)


def test_get_provider_interface_returns_singleton():
    """``ProviderInterface`` is a singleton — repeated dependency calls share state."""
    a = asyncio.run(get_provider_interface(None))  # type: ignore[arg-type]
    b = asyncio.run(get_provider_interface(None))  # type: ignore[arg-type]
    assert a is b
