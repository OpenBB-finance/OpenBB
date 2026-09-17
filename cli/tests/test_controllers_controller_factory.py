"""Test the Controller Factory."""

from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.controllers.platform_controller_factory import (
    PlatformControllerFactory,
)


def _stub_backend(translators=None, paths=None):
    """Return a Mock that quacks like ``Backend.get_translators_for_path``."""
    backend = MagicMock()
    backend.get_translators_for_path.return_value = (
        translators or {},
        paths or {},
    )
    return backend


def test_init_with_backend():
    """The factory pre-fetches translators + paths from the backend."""
    backend = _stub_backend(
        translators={"test_router_settings": MagicMock()},
        paths={"settings": "subpath"},
    )
    factory = PlatformControllerFactory(backend=backend, router_name="test_router")
    assert factory.router_name == "test_router"
    assert factory.controller_name == "Test_routerController"
    backend.get_translators_for_path.assert_called_once_with("test_router")


def test_create_controller_classifies_menus_and_commands():
    """``create()`` produces a class with menus / commands derived from paths."""
    backend = _stub_backend(
        translators={
            "test_router_quote": MagicMock(),
            "test_router_settings_inner": MagicMock(),
        },
        paths={"settings": "subpath"},
    )
    factory = PlatformControllerFactory(backend=backend, router_name="test_router")
    ControllerClass = factory.create()
    assert "settings" in ControllerClass.CHOICES_MENUS
    assert "quote" in ControllerClass.CHOICES_COMMANDS
    assert all("settings" not in cmd for cmd in ControllerClass.CHOICES_COMMANDS)


def test_create_propagates_factory_attributes():
    """Translators + paths + backend are stashed on the dynamic class."""
    backend = _stub_backend(
        translators={"test_x": MagicMock()},
        paths={"settings": "subpath"},
    )
    factory = PlatformControllerFactory(backend=backend, router_name="test")
    ControllerClass = factory.create()
    assert ControllerClass._factory_backend is backend
    assert "test_x" in ControllerClass._factory_translators
    assert ControllerClass._factory_paths == {"settings": "subpath"}


@pytest.fixture
def mock_processor():
    """Fixture to mock ArgparseClassProcessor used by the legacy path."""
    with patch(
        "openbb_cli.argparse_translator.argparse_class_processor.ArgparseClassProcessor"
    ) as mock:
        instance = mock.return_value
        instance.paths = {"settings": "subpath"}
        instance.translators = {"test_router_settings": MagicMock()}
        yield instance


def test_init_legacy_form_uses_local_backend(mock_processor):
    """Passing ``platform_router=`` wraps a ``LocalBackend``."""
    with patch(
        "openbb_cli.backend.LocalBackend.get_translators_for_path",
        return_value=({"mockrouter_settings": MagicMock()}, {"settings": "subpath"}),
    ):
        factory = PlatformControllerFactory(platform_router=MagicMock())
    assert factory.router_name == "magicmock"
    assert factory.controller_name == "MagicmockController"


def test_init_requires_backend_or_platform_router():
    with pytest.raises(ValueError, match="backend"):
        PlatformControllerFactory()


def test_init_backend_requires_router_name():
    with pytest.raises(ValueError, match="router_name"):
        PlatformControllerFactory(backend=MagicMock())
