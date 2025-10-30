"""Test router.py file."""

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import pytest
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.router import (
    CommandMap,
    Router,
    RouterLoader,
    SignatureInspector,
)
from pydantic import BaseModel, ConfigDict


class MockBaseModel(BaseModel):
    """Mock BaseModel class."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


@pytest.fixture(scope="module")
def router():
    """Set up router."""
    return Router()


def test_router_init(router):
    """Test init."""
    assert router


def test_command(router):
    """Test command."""

    @router.command
    async def valid_function() -> OBBject[list[int] | None]:
        return OBBject(results=[1, 2, 3])

    assert valid_function


def test_include_router(router):
    """Test include_router."""
    some_router = Router()
    assert router.include_router(some_router) is None


@pytest.fixture(scope="module")
def router_loader():
    """Set up router_loader."""
    return RouterLoader()


def test_router_loader_init(router_loader):
    """Test init."""
    assert router_loader


def test_from_extensions(router_loader):
    """Test from_extensions."""
    assert router_loader.from_extensions()


@pytest.fixture(scope="module")
def signature_inspector():
    """Set up signature_inspector."""
    return SignatureInspector()


def test_signature_inspector_init(signature_inspector):
    """Test init."""
    assert signature_inspector


def test_complete_signature(signature_inspector):
    """Test complete_signature."""

    async def sample_function(  # type: ignore[empty-body]
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    model = "EquityHistorical"

    assert signature_inspector.complete(sample_function, model)


def test_complete_signature_error(signature_inspector):
    """Test complete_signature."""

    async def valid_function() -> OBBject[list[int] | None]:
        return OBBject(results=[1, 2, 3])

    assert signature_inspector.complete(valid_function, "invalid_model") is None


def test_validate_signature(signature_inspector):
    """Test validate_signature."""

    async def sample_function(  # type: ignore
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    expected_signature = {
        "cc": CommandContext,
        "provider_choices": ProviderChoices,
        "standard_params": StandardParams,
        "extra_params": ExtraParams,
    }

    assert (
        signature_inspector.validate_signature(sample_function, expected_signature)
        is None
    )


def test_inject_dependency(signature_inspector):
    """Test inject_dependency."""

    async def sample_function(  # type: ignore
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    assert signature_inspector.inject_dependency(sample_function, "cc", CommandContext)


def test_get_description(signature_inspector):
    """Test get_description."""

    async def some_function():
        """Mock function."""

    assert signature_inspector.get_description(some_function) == some_function.__doc__


def test_get_description_no_doc(signature_inspector):
    """Test get_description."""

    async def some_function():
        pass

    assert not signature_inspector.get_description(some_function)


@pytest.fixture(scope="module")
def command_map():
    """Set up command_map."""
    return CommandMap()


def test_command_map_init(command_map):
    """Test init."""
    assert command_map


def test_map(command_map):
    """Test map."""
    assert isinstance(command_map.map, dict)


def test_provider_coverage(command_map):
    """Test provider_coverage."""
    assert isinstance(command_map.provider_coverage, dict)


def test_command_coverage(command_map):
    """Test command_coverage."""
    assert isinstance(command_map.command_coverage, dict)


def test_get_command_map(command_map, router):
    """Test get_command_map."""
    command_map = command_map.get_command_map(router)
    assert isinstance(command_map, dict)
    assert len(command_map) > 0


def test_get_provider_coverage(command_map, router):
    """Test get_provider_coverage."""
    provider_coverage = command_map.get_provider_coverage(router)
    assert isinstance(provider_coverage, dict)


def test_get_command_coverage(command_map, router):
    """Test get_command_coverage."""
    command_coverage = command_map.get_command_coverage(router)
    assert isinstance(command_coverage, dict)


def test_get_command(command_map):
    """Test get_command."""
    command = command_map.get_command("stocks/load")
    assert command is None
