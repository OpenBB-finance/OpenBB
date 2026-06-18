"""Custom Prompt classes for FastMCP."""

from typing import Any

from fastmcp.exceptions import PromptError
from fastmcp.prompts import Prompt
from fastmcp.prompts.base import Message


class StaticPrompt(Prompt):
    """A prompt that is a static string template."""

    content: str
    argument_defaults: dict[str, Any] = {}

    async def render(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> list[Message | str]:
        """Render the prompt with arguments.

        Return type matches an element of ``Prompt.render``'s union
        (``str | list[Message | str] | PromptResult``) exactly —
        ``list`` is invariant in Python's type system, so a tighter
        ``list[Message]`` annotation would still trip the parent's
        Liskov check even though every value we produce is a
        ``Message``.
        """
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
            return [Message(rendered_content, role="user")]
        except KeyError as e:
            raise PromptError(f"Missing argument for formatting: {e}") from e
