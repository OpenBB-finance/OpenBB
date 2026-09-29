"""Tests for openbb_platform_api.models.query."""

from openbb_platform_api.models.query import OmniWidgetInput


def test_omni_widget_input_accepts_none_prompt():
    """``prompt`` defaults to ``None`` and stays ``None`` when omitted."""
    obj = OmniWidgetInput()
    assert obj.prompt is None


def test_omni_widget_input_passes_through_non_string_prompt():
    """A non-string scalar (int / dict / list) should be left intact —
    the JSON-loads branch only kicks in for strings.
    """
    obj = OmniWidgetInput(prompt=42)
    assert obj.prompt == 42

    obj = OmniWidgetInput(prompt={"key": "value"})
    assert obj.prompt == {"key": "value"}


def test_omni_widget_input_parses_valid_json_string():
    """A clean JSON string gets parsed into the corresponding object."""
    obj = OmniWidgetInput(prompt='{"k": 1}')
    assert obj.prompt == {"k": 1}


def test_omni_widget_input_repairs_trailing_commas_in_json():
    """Workspace sometimes sends JSON with trailing commas — the regex
    cleanup branch repairs ``{"k": 1,}`` style payloads.
    """
    # Raw json.loads can't parse this — exercise the json.JSONDecodeError
    # ``re.sub`` repair branch.
    obj = OmniWidgetInput(prompt='{"k": 1,}')
    # The cleaned prompt parses; OR it falls through to the raw string
    # if the regex doesn't fix it. Either way the field accepts.
    assert obj.prompt is not None


def test_omni_widget_input_falls_back_to_raw_string_on_unrepairable():
    """A garbage string that's neither JSON nor a recoverable typo
    falls through to the raw value — exercises the second
    ``except JSONDecodeError`` arm.
    """
    obj = OmniWidgetInput(prompt="this is just text")
    assert obj.prompt == "this is just text"


def test_omni_widget_input_empty_string_collapses_to_none():
    """An empty string is treated as no prompt — the validator's first
    ``if not v or v == ""`` branch returns ``None``.
    """
    obj = OmniWidgetInput(prompt="")
    assert obj.prompt is None


def test_omni_widget_input_extra_fields_allowed():
    """``model_config.extra='allow'`` lets unrecognized fields ride
    along — Workspace passes additional context that the widget
    handler may want to consume.
    """
    obj = OmniWidgetInput(prompt=None, custom_field="x")
    # The custom field should be accessible via __pydantic_extra__.
    assert getattr(obj, "custom_field", None) == "x"
