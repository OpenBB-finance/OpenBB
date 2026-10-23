"""Tests for ``openbb_mcp_server.models.prompts``."""

import pytest
from fastmcp.exceptions import PromptError
from fastmcp.prompts import PromptArgument
from fastmcp.prompts.base import Message
from mcp.types import TextContent

from openbb_mcp_server.models.prompts import StaticPrompt


def _assert_user_message(rendered, text: str) -> None:
    """Assert ``rendered`` is a single user ``Message`` whose text is ``text``."""
    assert len(rendered) == 1
    msg = rendered[0]
    assert isinstance(msg, Message)
    assert msg.role == "user"
    assert isinstance(msg.content, TextContent)
    assert msg.content.text == text


class TestStaticPrompt:
    """Rendering static prompts."""

    @pytest.mark.asyncio
    async def test_static_prompt_render_success(self):
        """Test successful rendering of StaticPrompt."""
        prompt = StaticPrompt(
            name="test_prompt",
            content="Hello, {name}!",
            arguments=[PromptArgument(name="name", required=True)],
        )
        rendered = await prompt.render(arguments={"name": "World"})
        _assert_user_message(rendered, "Hello, World!")

    @pytest.mark.asyncio
    async def test_static_prompt_render_missing_required_argument(self):
        """Test rendering StaticPrompt with a missing required argument."""
        prompt = StaticPrompt(
            name="test_prompt",
            content="Hello, {name}!",
            arguments=[PromptArgument(name="name", required=True)],
        )
        with pytest.raises(PromptError, match="Missing required arguments: {'name'}"):
            await prompt.render(arguments={})

    @pytest.mark.asyncio
    async def test_static_prompt_render_missing_formatting_key(self):
        """Test rendering StaticPrompt with a missing formatting key."""
        prompt = StaticPrompt(name="test_prompt", content="Hello, {name}!")
        with pytest.raises(
            PromptError, match="Missing argument for formatting: 'name'"
        ):
            await prompt.render(arguments={"wrong_key": "World"})

    @pytest.mark.asyncio
    async def test_static_prompt_render_no_arguments(self):
        """Test rendering StaticPrompt with no arguments."""
        prompt = StaticPrompt(name="test_prompt", content="Hello, World!")
        rendered = await prompt.render()
        _assert_user_message(rendered, "Hello, World!")

    @pytest.mark.asyncio
    async def test_static_prompt_render_optional_argument(self):
        """Test rendering StaticPrompt with an optional argument."""
        prompt = StaticPrompt(
            name="test_prompt",
            content="Hello, {name}!",
            arguments=[PromptArgument(name="name", required=False)],
        )
        rendered = await prompt.render(arguments={"name": "Optional"})
        _assert_user_message(rendered, "Hello, Optional!")

    @pytest.mark.asyncio
    async def test_static_prompt_render_multiple_arguments(self):
        """Test rendering StaticPrompt with multiple arguments."""
        prompt = StaticPrompt(
            name="test_prompt",
            content="Hello, {name}! Welcome to {place}.",
            arguments=[
                PromptArgument(name="name", required=True),
                PromptArgument(name="place", required=True),
            ],
        )
        rendered = await prompt.render(arguments={"name": "User", "place": "OpenBB"})
        _assert_user_message(rendered, "Hello, User! Welcome to OpenBB.")

    @pytest.mark.asyncio
    async def test_static_prompt_render_with_none_arguments_in_prompt(self):
        """Test rendering StaticPrompt when arguments attribute is None."""
        prompt = StaticPrompt(
            name="test_prompt", content="Hello, World!", arguments=None
        )
        rendered = await prompt.render()
        _assert_user_message(rendered, "Hello, World!")

    @pytest.mark.asyncio
    async def test_static_prompt_renders_with_defaults(self):
        """StaticPrompt.render() applies argument_defaults when caller omits them."""
        prompt = StaticPrompt(
            name="greeting",
            content="Hello {name}, focus on {aspect}",
            arguments=[
                PromptArgument(name="name", required=True),
                PromptArgument(name="aspect", required=False),
            ],
            argument_defaults={"aspect": "fundamentals"},
        )

        rendered = await prompt.render(arguments={"name": "AAPL"})
        _assert_user_message(rendered, "Hello AAPL, focus on fundamentals")

    @pytest.mark.asyncio
    async def test_static_prompt_caller_overrides_defaults(self):
        """Caller-supplied values override argument_defaults."""
        prompt = StaticPrompt(
            name="greeting",
            content="Hello {name}, focus on {aspect}",
            arguments=[
                PromptArgument(name="name", required=True),
                PromptArgument(name="aspect", required=False),
            ],
            argument_defaults={"aspect": "fundamentals"},
        )

        rendered = await prompt.render(
            arguments={"name": "AAPL", "aspect": "technicals"}
        )
        _assert_user_message(rendered, "Hello AAPL, focus on technicals")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arguments", [None, {}])
    async def test_static_prompt_without_arguments_keeps_braces_verbatim(
        self, arguments
    ):
        """Content with literal braces is returned unformatted when nothing is supplied."""
        content = (
            '# Skill\n\n```python\nfetcher_dict = {"Example": ExampleFetcher}\n```'
        )
        prompt = StaticPrompt(name="test_curly", content=content, arguments=None)
        rendered = await prompt.render(arguments=arguments)
        _assert_user_message(rendered, content)
