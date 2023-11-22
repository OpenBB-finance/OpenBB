"""Test router.py file."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument


from typing import List, Optional

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
    CommandValidator,
    Router,
    RouterLoader,
    SignatureInspector,
)
from pydantic import BaseModel, ConfigDict


class MockBaseModel(BaseModel):
    """Mock BaseModel class."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


@pytest.fixture(scope="module")
def command_validator():
    """Set up command_validator."""
    return CommandValidator()


def test_command_validator_init(command_validator):
    """Test init."""
    assert command_validator


@pytest.mark.parametrize(
    "type_, expected",
    [
        (str, True),
        (int, True),
        (float, True),
        (bool, True),
        (list, True),
        (MockBaseModel, False),
    ],
)
def test_is_standard_pydantic_type(command_validator, type_, expected):
    """Test is_standard_pydantic_type."""
    # assert command_validator.is_standard_pydantic_type(str)
    assert command_validator.is_standard_pydantic_type(type_) == expected


def test_is_valid_pydantic_model_type(command_validator):
    """Test is_valid_pydantic_model_type."""
    assert command_validator.is_valid_pydantic_model_type(MockBaseModel)
    assert not command_validator.is_valid_pydantic_model_type(str)


@pytest.mark.parametrize(
    "type_, expected",
    [
        (str, True),
        (int, True),
        (float, True),
        (bool, True),
        (list, True),
        (MockBaseModel, True),
    ],
)
def test_is_serializable_value_type(command_validator, type_, expected):
    """Test is_serializable_value_type."""
    assert command_validator.is_serializable_value_type(type_) == expected


def test_is_annotated_dc(command_validator):
    """Test is_annotated_dc."""
    assert not command_validator.is_annotated_dc(str)


def test_check_reserved_param(command_validator):
    """Test check_reserved_param."""
    assert command_validator.check_reserved_param("name", str, {}, str, str) is None
    assert not command_validator.check_reserved_param("name", str, {}, str, int)


def test_check_parameters(command_validator):
    """Test check_parameters."""

    async def func():
        pass

    assert command_validator.check_parameters(func) is None
    with pytest.raises(TypeError):
        command_validator.check_parameters(MockBaseModel)


def test_check_return_error(command_validator):
    """Test check_return fail."""
    with pytest.raises(TypeError):

        async def func():
            pass

        command_validator.check_return(func)


def test_check_return(command_validator):
    """Test check_return."""

    async def valid_function() -> OBBject[Optional[List[int]]]:
        return OBBject(results=[1, 2, 3])

    assert command_validator.check_return(valid_function) is None


def test_check(command_validator):
    """Test check."""

    async def valid_function() -> OBBject[Optional[List[int]]]:
        return OBBject(results=[1, 2, 3])

    assert command_validator.check(valid_function) is None


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
    async def valid_function() -> OBBject[Optional[List[int]]]:
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

    async def sample_function(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    model = "EquityHistorical"

    assert signature_inspector.complete_signature(sample_function, model)


def test_complete_signature_error(signature_inspector):
    """Test complete_signature."""

    async def valid_function() -> OBBject[Optional[List[int]]]:
        return OBBject(results=[1, 2, 3])

    assert (
        signature_inspector.complete_signature(valid_function, "invalid_model") is None
    )


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
