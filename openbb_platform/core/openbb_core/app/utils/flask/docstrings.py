"""Parse view-function docstrings in Google, NumPy and Sphinx styles."""

from __future__ import annotations

import re
from inspect import cleandoc

_GOOGLE_HEADER = re.compile(r"^(args|arguments|parameters)\s*:$", re.IGNORECASE)
_SECTION_HEADER = re.compile(
    r"^(returns?|raises?|yields?|examples?|notes?|attributes?"
    r"|args|arguments|parameters)\s*:?\s*$",
    re.IGNORECASE,
)
_GOOGLE_PARAM = re.compile(r"^(\w+)\s*(?:\([^)]*\))?\s*:\s*(.+)$")
_SPHINX_PARAM = re.compile(r"^:param\s+(?:[^:\s]+\s+)?(\w+)\s*:\s*(.+)$")
_DASHES = re.compile(r"^-{3,}$")


def parse_docstring(
    doc: str | None,
) -> tuple[str | None, str | None, dict[str, str]]:
    """Return ``(summary, description, params)`` parsed from ``doc``."""
    if not doc or not doc.strip():
        return None, None, {}
    lines = cleandoc(doc).split("\n")
    summary = lines[0].strip() or None
    params: dict[str, str] = {}
    params.update(_parse_sphinx(lines))
    params.update(_parse_google(lines))
    params.update(_parse_numpy(lines))
    return summary, _extract_description(lines), params


def _extract_description(lines: list[str]) -> str | None:
    """Join the body lines between the summary and the first section."""
    body: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if (
            _SECTION_HEADER.match(stripped)
            or stripped.startswith(":param")
            or _DASHES.match(stripped)
        ):
            break
        if stripped:
            body.append(stripped)
    return " ".join(body) or None


def _parse_sphinx(lines: list[str]) -> dict[str, str]:
    """Extract ``:param name: description`` entries."""
    out: dict[str, str] = {}
    for line in lines:
        match = _SPHINX_PARAM.match(line.strip())
        if match:
            out[match.group(1)] = match.group(2).strip()
    return out


def _parse_google(lines: list[str]) -> dict[str, str]:
    """Extract entries from a Google-style ``Args`` block."""
    start: int | None = None
    for index, line in enumerate(lines):
        if _GOOGLE_HEADER.match(line.strip()):
            start = index + 1
            break
    if start is None:
        return {}

    out: dict[str, str] = {}
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if _SECTION_HEADER.match(stripped):
            break
        match = _GOOGLE_PARAM.match(stripped)
        if match:
            out[match.group(1)] = match.group(2).strip()
    return out


def _parse_numpy(lines: list[str]) -> dict[str, str]:
    """Extract entries from a NumPy-style ``Parameters`` block."""
    start: int | None = None
    for index in range(len(lines) - 1):
        if lines[index].strip().lower() == "parameters" and _DASHES.match(
            lines[index + 1].strip()
        ):
            start = index + 2
            break
    if start is None:
        return {}

    out: dict[str, str] = {}
    current: str | None = None
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped or _DASHES.match(stripped):
            continue
        if _SECTION_HEADER.match(stripped):
            break
        if not line[:1].isspace():
            current = stripped.split(":")[0].strip().split()[0]
            out.setdefault(current, "")
        elif current:
            out[current] = f"{out[current]} {stripped}".strip()
    return out
