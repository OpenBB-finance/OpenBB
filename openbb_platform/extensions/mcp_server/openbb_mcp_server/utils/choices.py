"""Expose the valid values of tool parameters in MCP input schemas."""

import json
from typing import Any
from urllib.parse import urlsplit

_EXTRA_KEYS = ("choices", "multiple_items_allowed", "x-widget_config")
_SCHEMA_KEYWORDS = frozenset(
    {
        "items",
        "prefixItems",
        "properties",
        "patternProperties",
        "additionalProperties",
        "anyOf",
        "oneOf",
        "allOf",
        "not",
        "if",
        "then",
        "else",
        "contains",
        "$defs",
        "definitions",
    }
)
_MULTI_HINT = " (comma-separate several)"


def _branches(schema: dict) -> list[dict]:
    """Return the alternatives of a schema, or the schema itself."""
    for key in ("anyOf", "oneOf"):
        if isinstance(schema.get(key), list):
            return [branch for branch in schema[key] if isinstance(branch, dict)]
    return [schema]


def schema_values(schema: dict) -> tuple[list[Any], bool]:
    """Return the enumerated values of a schema and whether a non-null branch accepts any value.

    Parameters
    ----------
    schema : dict
        A JSON schema.

    Returns
    -------
    tuple[list[Any], bool]
        The ``enum`` / ``const`` values of the non-null branches, and whether any
        non-null branch is unconstrained.
    """
    values: list[Any] = []
    free = False
    for branch in _branches(schema):
        if branch.get("type") == "null":
            continue
        if isinstance(branch.get("enum"), list):
            values.extend(branch["enum"])
        elif "const" in branch:
            values.append(branch["const"])
        else:
            free = True
    return values, free


def _unique(values: list[Any]) -> list[Any]:
    """Return ``values`` without duplicates, keeping the first occurrence."""
    seen: list[Any] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


def _option_values(widget: dict) -> list[Any]:
    """Return the values of a widget config's static ``options``."""
    return [
        option.get("value") if isinstance(option, dict) else option
        for option in widget.get("options") or []
    ]


def _json_type(values: list[Any]) -> str | None:
    """Return the JSON type shared by ``values``, if there is one."""
    kinds = set()
    for value in values:
        if isinstance(value, bool):
            kinds.add("boolean")
        elif isinstance(value, int):
            kinds.add("integer")
        elif isinstance(value, float):
            kinds.add("number")
        elif isinstance(value, str):
            kinds.add("string")
        else:
            return None
    if kinds == {"integer", "number"}:
        return "number"
    return kinds.pop() if len(kinds) == 1 else None


def _with_enum(schema: dict, values: list[Any]) -> dict:
    """Return ``schema`` constrained to ``values``, keeping it nullable when it was."""
    nullable = any(branch.get("type") == "null" for branch in _branches(schema))
    constrained: dict[str, Any] = {"enum": values}
    if json_type := _json_type(values):
        constrained = {"type": json_type, "enum": values}
    rest = {
        key: value
        for key, value in schema.items()
        if key not in ("anyOf", "oneOf", "type", "enum", "const")
    }
    if nullable:
        return {**rest, "anyOf": [constrained, {"type": "null"}]}
    return {**rest, **constrained}


def _endpoint_path(endpoint: str) -> str:
    """Return the path of an ``optionsEndpoint`` with a leading slash."""
    return "/" + urlsplit(endpoint).path.lstrip("/")


def _format_values(values: list[Any]) -> str:
    """Return ``values`` as a comma-separated list."""
    return ", ".join(str(value) for value in values)


def _lookup_note(widget: dict, tool_names: dict[str, str]) -> str | None:
    """Return a note naming the tool that lists a parameter's valid values."""
    endpoint = widget.get("optionsEndpoint")
    if not isinstance(endpoint, str):
        return None
    tool = tool_names.get(_endpoint_path(endpoint))
    if tool is None:
        return None
    arguments = [
        f"{name}=<the {value[1:]} you pass here>"
        if isinstance(value, str) and value.startswith("$")
        else f"{name}={json.dumps(value)}"
        for name, value in (widget.get("optionsParams") or {}).items()
    ]
    call = f" with {', '.join(arguments)}" if arguments else ""
    return f"Get the valid values from the `{tool}` tool{call}."


def _expose(
    schema: dict, tool_providers: list[str], tool_names: dict[str, str]
) -> dict:
    """Return one parameter schema with its choices exposed."""
    general: list[Any] = []
    by_provider: dict[str, list[Any]] = {}
    lookups: list[tuple[str | None, dict]] = []
    multi = False
    extra_keys: list[str] = []

    if isinstance(schema.get("choices"), list):
        general.extend(schema["choices"])
        extra_keys.append("choices")
    widget = schema.get("x-widget_config")
    if isinstance(widget, dict):
        extra_keys.append("x-widget_config")
        general.extend(_option_values(widget))
        multi = multi or bool(widget.get("multiSelect"))
        lookups.append((None, widget))

    for key, value in schema.items():
        if key in extra_keys or key in _SCHEMA_KEYWORDS or not isinstance(value, dict):
            continue
        if not any(extra in value for extra in _EXTRA_KEYS):
            continue
        extra_keys.append(key)
        choices = list(value.get("choices") or [])
        provider_widget = value.get("x-widget_config")
        if isinstance(provider_widget, dict):
            choices.extend(_option_values(provider_widget))
            lookups.append((key, provider_widget))
        if choices:
            by_provider[key] = _unique(choices)
        multi = multi or bool(value.get("multiple_items_allowed"))

    exposed = {key: value for key, value in schema.items() if key not in extra_keys}
    notes: list[str] = []
    hint = _MULTI_HINT if multi else ""

    if general or by_provider:
        title = [part.strip() for part in str(schema.get("title", "")).split(",")]
        param_providers = (
            title
            if tool_providers and set(title) <= set(tool_providers)
            else tool_providers or list(by_provider)
        )
        covered = bool(general) or set(param_providers) <= set(by_provider)
        values = _unique(
            general
            + [value for provider in by_provider for value in by_provider[provider]]
        )
        distinct = _unique(list(by_provider.values()))
        if covered and not multi:
            current, free = schema_values(exposed)
            if free or not current:
                exposed = _with_enum(exposed, values)
            if len(distinct) > 1:
                notes.append(
                    "Valid values by provider: "
                    + "; ".join(
                        f"{provider}: {_format_values(choices)}"
                        for provider, choices in by_provider.items()
                    )
                    + "."
                )
        else:
            if general:
                notes.append(f"Valid values{hint}: {_format_values(_unique(general))}.")
            notes.extend(
                f"Valid values for provider {provider}{hint}: {_format_values(choices)}."
                for provider, choices in by_provider.items()
            )

    for owner, lookup_widget in lookups:
        if note := _lookup_note(lookup_widget, tool_names):
            notes.append(f"For provider {owner}: {note}" if owner else note)

    if notes:
        exposed["description"] = " ".join(
            [exposed["description"], *notes] if exposed.get("description") else notes
        )
    return exposed


def expose_choices(parameters: dict, tool_names: dict[str, str]) -> dict:
    """Return a tool input schema with every parameter's valid values stated as ``enum`` or in its description.

    Parameters
    ----------
    parameters : dict
        The tool's input schema.
    tool_names : dict[str, str]
        Route path to tool name, for resolving ``optionsEndpoint`` references.

    Returns
    -------
    dict
        The input schema with choices exposed.
    """
    properties = parameters.get("properties")
    if not isinstance(properties, dict):
        return parameters
    provider_values, _ = schema_values(properties.get("provider") or {})
    tool_providers = [str(value) for value in provider_values]
    return {
        **parameters,
        "properties": {
            name: _expose(schema, tool_providers, tool_names)
            if isinstance(schema, dict)
            else schema
            for name, schema in properties.items()
        },
    }
