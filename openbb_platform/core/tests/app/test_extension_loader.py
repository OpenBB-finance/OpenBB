"""Tests for the ExtensionLoader class."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import APIRouter, FastAPI
from openbb_core.app.extension_loader import EntryPoint, ExtensionLoader, OpenBBGroups
from openbb_core.app.router import Router


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Fixture to run before and after each test function.

    This is necessary to reset the singleton instance of ExtensionLoader.
    """
    # Code to run before each test function
    yield  # This is where the test function runs
    # Code to run after each test function
    # pylint: disable=protected-access
    ExtensionLoader._instances = {}  # type: ignore


def test_extension_loader():
    """Smoke test for extension loader."""
    extension_loader = ExtensionLoader()
    assert extension_loader is not None


def test_extension_loader_singleton_prop():
    """Test the singleton property of extension loader."""
    extension_loader = ExtensionLoader()
    extension_loader2 = ExtensionLoader()
    assert extension_loader is extension_loader2


def test_openbb_groups():
    """Test the OpenBBGroups enum."""
    assert len(OpenBBGroups) == 3
    assert OpenBBGroups.core.value == "openbb_core_extension"
    assert OpenBBGroups.provider.value == "openbb_provider_extension"
    assert OpenBBGroups.obbject.value == "openbb_obbject_extension"


def test_obbject_entry_points():
    """Test the obbject entry points property."""
    el = ExtensionLoader()
    assert isinstance(el.obbject_entry_points, list)

    for ep in el.obbject_entry_points:
        assert ep.group == OpenBBGroups.obbject.value


def test_core_entry_points():
    """Test the core entry points property."""
    el = ExtensionLoader()
    assert isinstance(el.core_entry_points, list)
    for ep in el.core_entry_points:
        assert ep.group == OpenBBGroups.core.value


def test_provider_entry_points():
    """Test the provider entry points property."""
    el = ExtensionLoader()
    assert isinstance(el.provider_entry_points, list)
    for ep in el.provider_entry_points:
        assert ep.group == OpenBBGroups.provider.value


def test_sorted_entry_points():
    """Test the _sorted_entry_points method."""
    # pylint: disable=protected-access
    core_entry_points = ExtensionLoader._sorted_entry_points(OpenBBGroups.core.value)
    for ep in core_entry_points:
        assert ep.group == OpenBBGroups.core.value


def test_get_entry_point():
    """Test the _get_entry_point method."""
    el = ExtensionLoader()
    # pylint: disable=protected-access
    result = el._get_entry_point(el.provider_entry_points, "fmp")
    if result:
        assert result.group == OpenBBGroups.provider.value
        assert result.name == "fmp"

    # pylint: disable=protected-access
    result = el._get_entry_point(el.core_entry_points, "equity")
    if result:
        assert result.group == OpenBBGroups.core.value
        assert result.name == "equity"


def test_get_entry_point_not_found():
    """Test the _get_entry_point method when the extension is not found."""
    el = ExtensionLoader()
    # pylint: disable=protected-access
    result = el._get_entry_point(el.core_entry_points, "random_extension")
    assert result is None


@patch("openbb_core.app.extension_loader.ExtensionLoader._get_entry_point")
def test_get_obbject_entry_point(mock_get_entry_point):
    """Test the get_obbject_entry_point method."""

    mock_get_entry_point.return_value = EntryPoint(
        name="mock_extension", group=OpenBBGroups.obbject.value, value="mock"
    )

    el = ExtensionLoader()
    result = el.get_obbject_entry_point("mock_extension")
    if result:
        assert result.group == OpenBBGroups.obbject.value
        assert result.name == "mock_extension"


@patch("openbb_core.app.extension_loader.ExtensionLoader._get_entry_point")
def test_get_entry_point_core(mock_get_entry_point):
    """Test the get_core_entry_point method."""

    mock_get_entry_point.return_value = EntryPoint(
        name="mock_extension", group=OpenBBGroups.obbject.value, value="mock"
    )

    el = ExtensionLoader()
    result = el.get_core_entry_point("mock_extension")
    if result:
        assert result.group == OpenBBGroups.obbject.value
        assert result.name == "mock_extension"


@patch("openbb_core.app.extension_loader.ExtensionLoader._get_entry_point")
def test_get_entry_point_provider(mock_get_entry_point):
    """Test the get_core_entry_point method."""

    mock_get_entry_point.return_value = EntryPoint(
        name="mock_extension", group=OpenBBGroups.obbject.value, value="mock"
    )

    el = ExtensionLoader()
    result = el.get_provider_entry_point("mock_extension")
    if result:
        assert result.group == OpenBBGroups.obbject.value
        assert result.name == "mock_extension"


def test_obbject_objects():
    """Test the obbject objects property."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.extension import Extension

    el = ExtensionLoader()
    assert isinstance(el.obbject_objects, dict)

    for key, value in el.obbject_objects.items():
        assert isinstance(key, str)
        assert isinstance(value, Extension)


def test_core_objects():
    """Test the core objects property."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.router import Router

    el = ExtensionLoader()
    assert isinstance(el.core_objects, dict)

    for key, value in el.core_objects.items():
        assert isinstance(key, str)
        assert isinstance(value, Router)


def test_provider_objects():
    """Test the provider objects property."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.abstract.provider import Provider

    el = ExtensionLoader()
    assert isinstance(el.provider_objects, dict)

    for key, value in el.provider_objects.items():
        assert isinstance(key, str)
        assert isinstance(value, Provider)


@patch("openbb_core.app.extension_loader.entry_points")
def test_core_objects_with_fastapi_instance(mock_entry_points):
    """Test the core_objects property with a FastAPI instance."""
    # pylint: disable=import-outside-toplevel
    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "fastapi_extension"
    mock_ep.load.return_value = FastAPI()
    mock_entry_points.return_value = [mock_ep]

    el = ExtensionLoader()
    core_objects = el.core_objects

    assert "fastapi_extension" in core_objects
    assert isinstance(core_objects["fastapi_extension"], Router)
    mock_entry_points.assert_any_call(group="openbb_core_extension")


@patch("openbb_core.app.extension_loader.entry_points")
def test_core_objects_with_apirouter_instance(mock_entry_points):
    """Test the core_objects property with an APIRouter instance."""
    # pylint: disable=import-outside-toplevel
    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "apirouter_extension"
    mock_ep.load.return_value = APIRouter()
    mock_entry_points.return_value = [mock_ep]

    el = ExtensionLoader()
    core_objects = el.core_objects

    assert "apirouter_extension" in core_objects
    assert isinstance(core_objects["apirouter_extension"], Router)
    mock_entry_points.assert_any_call(group="openbb_core_extension")
