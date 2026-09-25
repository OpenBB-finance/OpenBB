"""Shared fixtures for tests under ``tests/app/static``.

These fixtures build a *real* ``Router`` with a real command bound to a
real (fake) provider/model and replace the global
``RouterLoader.from_extensions`` and ``ProviderInterface`` singletons so
that any code path that walks "the extensions" sees the synthetic
extension we set up here. This lets tests against ``Coverage``,
``BaseApp``, ``CommandMap``, and the static package builder exercise the
real production code paths without depending on the developer having
real OpenBB extensions installed.
"""

import pytest

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
)
from openbb_core.app.router import Router, RouterLoader
from openbb_core.provider.registry_map import RegistryMap


def _reset_provider_interface() -> None:
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]


@pytest.fixture
def isolated_provider_interface(fake_registry):
    """Replace the ``ProviderInterface`` singleton with one over the fake registry."""
    _reset_provider_interface()
    pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    yield pi
    _reset_provider_interface()


@pytest.fixture
def isolated_multi_provider_interface(multi_provider_registry):
    """Replace the singleton with a ``ProviderInterface`` over both fake providers."""
    _reset_provider_interface()
    pi = ProviderInterface(registry_map=RegistryMap(registry=multi_provider_registry))
    yield pi
    _reset_provider_interface()


def _make_fake_command():
    """Return a fresh async fake command compatible with ``Router.command(model=...)``.

    Defined per call because ``Router.command`` mutates ``__annotations__``.
    """

    async def fake_command(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:  # type: ignore[empty-body]
        """Fake command for static-package tests."""

    return fake_command


@pytest.fixture
def install_router(monkeypatch):
    """Factory that installs a built ``Router`` as the global ``RouterLoader.from_extensions`` result."""

    def _install(child: Router, prefix: str = "/test") -> Router:
        parent = Router()
        parent.include_router(router=child, prefix=prefix)
        RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
        monkeypatch.setattr(
            "openbb_core.app.router.RouterLoader.from_extensions",
            lambda: parent,
        )
        return parent

    return _install


@pytest.fixture
def fake_router(isolated_provider_interface, fake_model_name, install_router) -> Router:
    """A ``Router`` with one fake command using the primary fake provider."""
    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    return install_router(child, prefix="/test")


@pytest.fixture
def multi_provider_router(
    isolated_multi_provider_interface, fake_model_name, install_router
) -> Router:
    """A ``Router`` whose single command is backed by both fake providers."""
    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    return install_router(child, prefix="/test")
