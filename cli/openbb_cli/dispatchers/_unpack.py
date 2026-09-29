"""Shared response unwrapping used by both the HTTP dispatcher and codegen."""

from __future__ import annotations

import json as _json
import re as _re
from typing import Any

_BARE_ASTERISK = _re.compile(r":\s*\*\s*(?=[,}\]])")


def safe_json_loads(text: str) -> Any:
    """Parse JSON text, sanitizing common upstream quirks first."""
    try:
        return _json.loads(text)
    except ValueError:
        sanitized = _BARE_ASTERISK.sub(": null", text)
        return _json.loads(sanitized)


def unpack_response(
    payload: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Split a raw API payload into (rows, metadata)."""
    if isinstance(payload, list):
        if len(payload) == 1:
            return unpack_response(payload[0])
        rows = [r for r in payload if isinstance(r, dict)]
        if rows:
            return rows, {}
        return [{"value": r} for r in payload], {}
    if not isinstance(payload, dict):
        return [{"value": payload}], {}
    list_keys = [k for k, v in payload.items() if isinstance(v, list)]
    if len(list_keys) == 1:
        key = list_keys[0]
        items = payload[key]
        metadata = {k: v for k, v in payload.items() if k != key}
        # Only return this as an envelope if all items are dicts or the list is
        # the only thing in the payload.
        if all(isinstance(v, dict) for v in items):
            return items, metadata
        if len(payload) == 1:
            return [{"value": r} for r in items], metadata
    if len(payload) == 1:
        only_value = next(iter(payload.values()))
        if isinstance(only_value, (list, dict)):
            return unpack_response(only_value)
    return [payload], {}
