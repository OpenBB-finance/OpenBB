"""Tests for ``openbb_mcp_server.models.mcp_config``."""

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


class TestArgumentDefinitionModel:
    """Prompt argument definitions."""

    def test_argument_definition_model(self):
        """Test ArgumentDefinitionModel."""
        arg = ArgumentDefinitionModel(
            name="test_arg", type="str", description="A test arg."
        )
        assert arg.name == "test_arg"
        assert arg.type == "str"

        with pytest.raises(ValidationError):
            ArgumentDefinitionModel(name="123invalid", type="str")
        with pytest.raises(ValidationError):
            ArgumentDefinitionModel(name="invalid-name", type="str")
        with pytest.raises(ValidationError):
            ArgumentDefinitionModel(name="", type="str")

        with pytest.raises(ValidationError):
            ArgumentDefinitionModel(name="valid_name", type="invalid_type")


class TestPromptConfigModel:
    """Inline prompt configuration."""

    def test_prompt_config_model(self):
        """Test PromptConfigModel."""
        prompt = PromptConfigModel(
            name="test_prompt",
            content="This is a {test_arg}.",
            arguments=[ArgumentDefinitionModel(name="test_arg", type="str")],
        )
        assert prompt.name == "test_prompt"
        assert len(prompt.arguments) == 1

        with pytest.raises(ValidationError):
            PromptConfigModel(name="test", content=" ")

        with pytest.raises(ValidationError):
            PromptConfigModel(name="test", content="This is a {test_arg.")

        with pytest.raises(ValidationError):
            PromptConfigModel(name="invalid name", content="test")

        with pytest.raises(ValidationError):
            PromptConfigModel(name="test", content="test", tags=[""])
        with pytest.raises(ValidationError):
            PromptConfigModel(name="test", content="test", tags=[123])

    def test_prompt_config_accepts_explicit_none_name(self):
        """An explicit ``name=None`` is left for auto-naming."""
        assert PromptConfigModel(name=None, content="hello").name is None

    def test_prompt_config_rejects_whitespace_only_name(self):
        """A whitespace-only ``name`` fails the empty-string guard."""
        with pytest.raises(ValidationError, match="Prompt name cannot be empty string"):
            PromptConfigModel(name=" ", content="hello")


class TestMCPConfigModel:
    """Per-route MCP configuration."""

    def test_mcp_config_model(self):
        """Test MCPConfigModel."""
        config = MCPConfigModel(
            expose=True,
            methods=["GET", "POST"],
            prompts=[PromptConfigModel(name="p1", content="c1")],
        )
        assert config.expose is True
        assert config.methods == [HTTPMethod.GET, HTTPMethod.POST]

        with pytest.raises(ValidationError):
            MCPConfigModel(methods=["INVALID"])

        with pytest.raises(ValidationError):
            MCPConfigModel(
                prompts=[
                    PromptConfigModel(name="p1", content="c1"),
                    PromptConfigModel(name="p1", content="c2"),
                ]
            )

        config = MCPConfigModel(methods=["get", "POST"])
        assert config.methods == [HTTPMethod.GET, HTTPMethod.POST]

        with pytest.raises(ValidationError):
            MCPConfigModel(methods=["GET", "*"])

    def test_mcp_config_methods_are_deduplicated(self):
        """Repeated methods collapse to one entry, keeping the first position."""
        config = MCPConfigModel(methods=["GET", "post", "get"])
        assert config.methods == [HTTPMethod.GET, HTTPMethod.POST]

    def test_mcp_config_methods_validator_passthrough_none(self):
        """``methods=None`` short-circuits the validator and returns None."""
        config = MCPConfigModel(methods=None)
        assert config.methods is None

    def test_mcp_config_methods_validator_accepts_single_string(self):
        """``methods="GET"`` is normalized to a single-entry list."""
        config = MCPConfigModel(methods="GET")
        assert config.methods == [HTTPMethod.GET]

    def test_mcp_config_methods_validator_rejects_non_list(self):
        """``methods={...}`` (not str/list) raises a TypeError-shaped ValueError."""
        with pytest.raises(ValidationError, match="must be a list of strings"):
            MCPConfigModel(methods={"GET"})

    def test_mcp_config_tool_fields(self):
        """The tool-level keys are typed and validated."""
        config = MCPConfigModel(
            name="renamed",
            tags=["extra"],
            enable=False,
            describe_responses=True,
            mime_type="text/csv",
            exclude_args=["internal"],
        )
        assert config.to_dict() == {
            "name": "renamed",
            "tags": ["extra"],
            "enable": False,
            "describe_responses": True,
            "mime_type": "text/csv",
            "exclude_args": ["internal"],
            "prompts": [],
        }
        with pytest.raises(ValidationError):
            MCPConfigModel(enable="sometimes")

    def test_mcp_config_to_dict_excludes_none(self):
        """``to_dict()`` drops fields left at their None defaults."""
        config = MCPConfigModel(expose=True)
        out = config.to_dict()
        assert out == {"expose": True, "prompts": []}


class TestValidateMcpConfig:
    """Validating configuration dictionaries."""

    def test_validate_mcp_config(self, app_caplog):
        """Strict mode raises on invalid input; lenient mode logs and returns defaults."""
        valid_config_dict = {"expose": True, "methods": ["GET"]}
        config = validate_mcp_config(valid_config_dict)
        assert isinstance(config, MCPConfigModel)

        invalid_config_dict = {"methods": ["INVALID"]}
        with pytest.raises(ValidationError):
            validate_mcp_config(invalid_config_dict)

        config = validate_mcp_config(invalid_config_dict, strict=False)
        assert config == MCPConfigModel()
        assert [r.levelname for r in app_caplog.records] == ["WARNING"]

    def test_is_valid_mcp_config(self):
        """Test is_valid_mcp_config function."""
        valid_config_dict = {"expose": True, "methods": ["GET"]}
        assert is_valid_mcp_config(valid_config_dict) is True

        invalid_config_dict = {"methods": ["INVALID"]}
        assert isinstance(is_valid_mcp_config(invalid_config_dict), Exception)
