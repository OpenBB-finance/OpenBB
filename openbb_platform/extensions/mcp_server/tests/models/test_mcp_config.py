"""Unit tests for mcp_config module."""

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from openbb_mcp_server.models.mcp_config import (
    ArgumentDefinitionModel,
    HTTPMethod,
    MCPConfigModel,
    PromptConfigModel,
    is_valid_mcp_config,
    validate_mcp_config,
)


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


def test_prompt_config_rejects_whitespace_only_name():
    """A whitespace-only ``name`` fails the empty-string guard."""
    with pytest.raises(ValidationError, match="Prompt name cannot be empty string"):
        PromptConfigModel(name=" ", content="hello")


def test_prompt_config_rejects_non_string_tag():
    """The validator's defensive non-string guard fires when invoked directly."""
    with pytest.raises(ValueError, match="Tag must be a string"):
        PromptConfigModel.validate_tags([123])  # type: ignore[list-item]


def test_mcp_config_methods_validator_passthrough_none():
    """``methods=None`` short-circuits the validator and returns None."""
    config = MCPConfigModel(methods=None)
    assert config.methods is None


def test_mcp_config_methods_validator_accepts_single_string():
    """``methods="GET"`` is normalized to a single-entry list."""
    config = MCPConfigModel(methods="GET")  # type: ignore[arg-type]
    assert config.methods == [HTTPMethod.GET]


def test_mcp_config_methods_validator_rejects_non_list():
    """``methods={...}`` (not str/list) raises a TypeError-shaped ValueError."""
    with pytest.raises(ValidationError, match="must be a list of strings"):
        MCPConfigModel(methods={"GET"})  # type: ignore[arg-type]


def test_mcp_config_to_dict_excludes_none():
    """``to_dict()`` drops fields left at their None defaults."""
    config = MCPConfigModel(expose=True)
    out = config.to_dict()
    assert out == {"expose": True, "prompts": []}
