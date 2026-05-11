"""Shared response unwrapping used by both the HTTP dispatcher and codegen.

The same envelope-stripping logic the generated extension applies at runtime
also runs against the spec-mode HTTP backend's responses, so what the user
sees in the REPL matches what an installed extension would surface — single-
key envelope wrappers stripped, single-element lists unpacked, sibling
scalar metadata split off from the row array.
"""

from __future__ import annotations

import json as _json
import re as _re
from typing import Any

# ``": *"`` — a bare asterisk is a common upstream sentinel for "data
# suppressed" (NY Fed's ``dailyAvgVolInMillions`` returns this when the
# value is masked). It's invalid JSON, so ``json.loads`` aborts on the
# first occurrence and the rest of an otherwise-good payload is lost.
_BARE_ASTERISK = _re.compile(r":\s*\*\s*(?=[,}\]])")


def safe_json_loads(text: str) -> Any:
    """Parse JSON text, sanitizing common upstream quirks first.

    Currently fixes bare-``*`` sentinels by substituting ``null``. Strict
    parse runs first so well-formed payloads pay no regex cost; the rewrite
    only happens when the strict parse fails. The sanitized text is then
    re-parsed and any remaining error surfaces as the caller's ``ValueError``.
    """
    try:
        return _json.loads(text)
    except ValueError:
        sanitized = _BARE_ASTERISK.sub(": null", text)
        return _json.loads(sanitized)


def unpack_response(
    payload: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Split a raw API payload into (rows, metadata).

    Single-element list and single-key envelope wrappers are stripped so the
    caller never has to handle them. When the payload is a dict mixing one
    array field with scalar metadata fields, the array becomes ``rows`` and
    everything else becomes ``metadata``. Arrays of scalars (strings,
    numbers) wrap each element as ``{"value": x}`` so downstream typed-row
    construction has something to instantiate. Nested objects inside a row
    are kept intact — the generated ``Data`` class describes them with
    proper nested-model classes, so Pydantic recursively validates them
    when the caller does ``Data(**row)``.
    """
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
        rows = [r for r in items if isinstance(r, dict)]
        if not rows and items:
            rows = [{"value": r} for r in items]
        metadata = {k: v for k, v in payload.items() if k != key}
        return rows, metadata
    if len(payload) == 1:
        only_value = next(iter(payload.values()))
        if isinstance(only_value, (list, dict)):
            return unpack_response(only_value)
    return [payload], {}
