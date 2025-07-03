"""OpenBB Workspace Query Models."""

from typing import Any, Optional

from openbb_core.provider.abstract.data import Data
from pydantic import AliasGenerator, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_snake


class FormData(Data):
    """Submit a form via POST request."""

    model_config = ConfigDict(
        extra="allow",
        alias_generator=AliasGenerator(to_snake),
        title="Submit Form",
    )


class OmniWidgetInput(Data):
    """Input for OmniWidget."""

    model_config = ConfigDict(
        extra="allow",
        alias_generator=AliasGenerator(to_snake),
        title="OmniWidget Input Data for POST Request.",
        json_schema_extra={
            "x-widget_config": {
                "$.type": "omni",
            }
        },
    )

    prompt: Optional[Any] = Field(
        default=None,
        description="The prompt text or JSON object sent from Workspace.",
        json_schema_extra={
            "x-widget_config": {
                "type": "text",
                "value": "",
                "description": "Input prompt value for the OmniWidget.",
                "show": False,
            }
        },
    )

    @field_validator("prompt", mode="before")
    @classmethod
    def _validate_prompt(cls, v):
        """Validate and parse the prompt field."""
        # pylint: disable=import-outside-toplevel
        import json
        import re

        if not v or v == "":
            return None

        prompt = ""

        try:
            prompt = json.loads(v)
        except json.JSONDecodeError:
            # Try to fix common JSON errors like trailing commas
            try:
                # Remove trailing commas in objects and arrays
                cleaned_prompt = re.sub(r",(\s*[}\]])", r"\1", prompt)
                prompt = json.loads(cleaned_prompt)
            except json.JSONDecodeError:
                prompt = v

        return prompt if prompt != "" else None
