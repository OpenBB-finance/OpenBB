"""Unit tests for mcp_config module."""

from unittest.mock import patch

import pytest
from openbb_mcp_server.models.mcp_config import (
    ArgumentDefinitionModel,
    HTTPMethod,
    MCPConfigModel,
    PromptConfigModel,
    is_valid_mcp_config,
    validate_mcp_config,
)
from pydantic import ValidationError


def test_argument_definition_model():
    """Test ArgumentDefinitionModel."""
    # Valid data
    arg = ArgumentDefinitionModel(
        name="test_arg", type="str", description="A test arg."
    )
    assert arg.name == "test_arg"
    assert arg.type == "str"

    # Invalid names
    with pytest.raises(ValidationError):
        ArgumentDefinitionModel(name="123invalid", type="str")
    with pytest.raises(ValidationError):
        ArgumentDefinitionModel(name="invalid-name", type="str")
    with pytest.raises(ValidationError):
        ArgumentDefinitionModel(name="", type="str")

    # Invalid type
    with pytest.raises(ValidationError):
        ArgumentDefinitionModel(name="valid_name", type="invalid_type")


def test_prompt_config_model():
    """Test PromptConfigModel."""
    # Valid data
    prompt = PromptConfigModel(
        name="test_prompt",
        content="This is a {test_arg}.",
        arguments=[ArgumentDefinitionModel(name="test_arg", type="str")],
    )
    assert prompt.name == "test_prompt"
    assert len(prompt.arguments) == 1

    # Empty content
    with pytest.raises(ValidationError):
        PromptConfigModel(name="test", content=" ")

    # Unmatched braces
    with pytest.raises(ValidationError):
        PromptConfigModel(name="test", content="This is a {test_arg.")

    # Invalid name
    with pytest.raises(ValidationError):
        PromptConfigModel(name="invalid name", content="test")

    # Invalid tags
    with pytest.raises(ValidationError):
        PromptConfigModel(name="test", content="test", tags=[""])
    with pytest.raises(ValidationError):
        PromptConfigModel(name="test", content="test", tags=[123])  # type: ignore


def test_mcp_config_model():
    """Test MCPConfigModel."""
    # Valid data
    config = MCPConfigModel(
        expose=True,
        methods=["GET", "POST"],  # type: ignore
        prompts=[PromptConfigModel(name="p1", content="c1")],
    )
    assert config.expose is True
    assert config.methods == [HTTPMethod.GET, HTTPMethod.POST]

    # Invalid method
    with pytest.raises(ValidationError):
        MCPConfigModel(methods=["INVALID"])  # type: ignore

    # Duplicate prompt names
    with pytest.raises(ValidationError):
        MCPConfigModel(
            prompts=[
                PromptConfigModel(name="p1", content="c1"),
                PromptConfigModel(name="p1", content="c2"),
            ]
        )

    # Test method validation
    config = MCPConfigModel(methods=["get", "POST"])  # type: ignore
    assert config.methods == [HTTPMethod.GET, HTTPMethod.POST]

    with pytest.raises(ValidationError):
        MCPConfigModel(methods=["GET", "*"])  # type: ignore


def test_validate_mcp_config():
    """Test validate_mcp_config function."""
    valid_config_dict = {"expose": True, "methods": ["GET"]}
    config = validate_mcp_config(valid_config_dict)
    assert isinstance(config, MCPConfigModel)

    invalid_config_dict = {"methods": ["INVALID"]}
    with pytest.raises(ValidationError):
        validate_mcp_config(invalid_config_dict)

    # Non-strict mode
    with patch("openbb_mcp_server.models.mcp_config.logger.warning") as mock_warning:
        config = validate_mcp_config(invalid_config_dict, strict=False)
        assert isinstance(config, MCPConfigModel)
        assert config.methods is None
        mock_warning.assert_called_once()


def test_is_valid_mcp_config():
    """Test is_valid_mcp_config function."""
    valid_config_dict = {"expose": True, "methods": ["GET"]}
    assert is_valid_mcp_config(valid_config_dict) is True

    invalid_config_dict = {"methods": ["INVALID"]}
    assert isinstance(is_valid_mcp_config(invalid_config_dict), Exception)
