"""Custom Prompt classes for FastMCP."""

from typing import Any

from fastmcp.exceptions import PromptError
from fastmcp.prompts import Prompt
from mcp.types import PromptMessage, TextContent


class StaticPrompt(Prompt):
    """A prompt that is a static string template."""

    content: str
    argument_defaults: dict[str, Any] = {}

    async def render(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> list[PromptMessage]:
        """Render the prompt with arguments."""
        # Start with stored defaults, then overlay caller-supplied values
        args = {**self.argument_defaults, **(arguments or {})}

        # Validate required arguments
        if self.arguments:
            required = {arg.name for arg in self.arguments if arg.required}
            provided = set(args)
            missing = required - provided
            if missing:
                raise PromptError(f"Missing required arguments: {missing}")

        try:
            rendered_content = (
                self.content.format(**args) if self.arguments or args else self.content
            )
            return [
                PromptMessage(
                    role="user", content=TextContent(type="text", text=rendered_content)
                )
            ]
        except KeyError as e:
            raise PromptError(f"Missing argument for formatting: {e}") from e
