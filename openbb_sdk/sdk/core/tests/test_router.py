"""Test router.py file."""
# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.router import (
    CommandMap,
    CommandValidator,
    Router,
    RouterLoader,
    SignatureInspector,
)
from pydantic import BaseModel


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
        (BaseModel, False),
    ],
)
def test_is_standard_pydantic_type(command_validator, type_, expected):
    """Test is_standard_pydantic_type."""
    # assert command_validator.is_standard_pydantic_type(str)
    assert command_validator.is_standard_pydantic_type(type_) == expected


def test_is_valid_pydantic_model_type(command_validator):
    """Test is_valid_pydantic_model_type."""
    assert command_validator.is_valid_pydantic_model_type(BaseModel)
    assert not command_validator.is_valid_pydantic_model_type(str)


@pytest.mark.parametrize(
    "type_, expected",
    [
        (str, True),
        (int, True),
        (float, True),
        (bool, True),
        (list, True),
        (BaseModel, True),
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

    def func():
        pass

    assert command_validator.check_parameters(func) is None
    assert not command_validator.check_parameters(BaseModel)


def test_check_return_error(command_validator):
    """Test check_return fail."""
    with pytest.raises(TypeError):

        def func():
            pass

        command_validator.check_return(func)


def test_check_return(command_validator):
    """Test check_return."""

    def valid_function() -> CommandOutput[int]:
        return CommandOutput(results=[1, 2, 3])

    assert command_validator.check_return(valid_function) is None


def test_check(command_validator):
    """Test check."""

    def valid_function() -> CommandOutput[int]:
        return CommandOutput(results=[1, 2, 3])

    assert command_validator.check(valid_function) is None


@pytest.fixture(scope="module")
def router():
    """Set up router."""
    return Router()


def test_router_init(router):
    """Test init."""
    assert router


@pytest.fixture(scope="module")
def router_loader():
    """Set up router_loader."""
    return RouterLoader()


def test_router_loader_init(router_loader):
    """Test init."""
    assert router_loader


@pytest.fixture(scope="module")
def signature_inspector():
    """Set up signature_inspector."""
    return SignatureInspector()


def test_signature_inspector_init(signature_inspector):
    """Test init."""
    assert signature_inspector


@pytest.fixture(scope="module")
def command_map():
    """Set up command_map."""
    return CommandMap()


def test_command_map_init(command_map):
    """Test init."""
    assert command_map
