"""Federal Reserve BHCPR User's Guide item definitions.

The Bank Holding Company Performance Report has no interactive concept guide like
the UBPR; the Federal Reserve publishes the definition of each BHCPR item only in
the static PDF *A User's Guide for the Bank Holding Company Performance Report*.
This parses that guide's Section 3 ("Sample BHCPR and Definition of Items") — a
two-column layout in which each item is an italic heading, optionally followed by
an italic ``(Percent of …)`` basis line and then its definition in regular text —
into a ``{(section, item): definition}`` map, and resolves a parsed report line
item's section and label to that definition for the hover card.
"""

from __future__ import annotations

import re
from typing import Any

GUIDE_URL = "https://www.federalreserve.gov/publications/files/2021-12-UGBHCPR.pdf"

_COLUMN_SPLIT = 306.0
_SECTION_MARKER = "Section 3"
_SEP = "\x1e"


def _norm(text: str) -> str:
    """Normalize a label or item name for matching: alphanumerics only, lowercased."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", (text or "").lower())).strip()


def _dehyphenate(text: str) -> str:
    """Join words split by a line-break hyphen (``prem- ises`` -> ``premises``)."""
    return re.sub(r"(\w)-\s+(\w)", r"\1\2", text).strip()


def _group_lines(words: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Cluster a column's words into lines, top-to-bottom then left-to-right."""
    words = sorted(words, key=lambda w: (round(w["top"]), w["x0"]))
    lines: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    last_top: float | None = None
    for word in words:
        if last_top is None or abs(word["top"] - last_top) <= 4:
            current.append(word)
        else:
            lines.append(current)
            current = [word]
        last_top = word["top"]
    if current:
        lines.append(current)
    return [sorted(line, key=lambda w: w["x0"]) for line in lines]


def _classify(line: list[dict[str, Any]]) -> tuple[str, str]:
    """Classify one line by its fonts into a structural kind and its text.

    Item names and their ``(basis)`` line are italic; a bare item name does not
    open with ``(``. Section titles are 13pt bold; sub-category headers are 10pt
    bold. Sample-report numbers and rotated running-header text are ``skip``.
    """
    text = " ".join(word["text"] for word in line).strip()
    count = len(line)
    bold = sum("Bold" in word["fontname"] for word in line)
    italic = sum("Italic" in word["fontname"] for word in line)
    size = max(word["size"] for word in line)
    singles = sum(len(word["text"]) == 1 for word in line)
    digits = sum(char.isdigit() for char in text)
    letters = sum(char.isalpha() for char in text)
    if singles > count * 0.6 or digits > letters:
        return "skip", text
    if bold >= count * 0.6:
        return ("section" if size >= 12.5 else "subheader"), text
    if italic >= count * 0.6:
        return ("basis" if text.startswith("(") else "item"), text
    return "body", text


def _parse_pages(pages: list[Any]) -> dict[str, str]:
    """Parse the guide's definition pages into a ``{section-item: definition}`` map.

    Keys join the normalized section title and item name with a record separator.

    Reading starts at the first page carrying the ``Section 3`` running header and
    runs to the end (the header prints only on recto pages, so every page is read
    once the section has begun). Within each page the two columns are read left
    then right; body text accumulates under the most recent italic item heading and
    flushes at the next heading, sub-header, or section title.
    """
    definitions: dict[str, str] = {}
    section: str | None = None
    item: str | None = None
    buffer: list[str] = []
    started = False
    in_title = False

    def _flush() -> None:
        """Store the accumulated definition for the current section and item."""
        if section and item and buffer:
            definitions.setdefault(
                f"{_norm(section)}{_SEP}{_norm(item)}", _dehyphenate(" ".join(buffer))
            )

    for page in pages:
        text = page.extract_text() or ""
        if _SECTION_MARKER in text:
            started = True
        if not started:
            continue
        words = [
            word
            for word in page.extract_words(extra_attrs=["fontname", "size"])
            if word["text"].strip() and 42 <= word["top"] <= 758
        ]
        for x0, x1 in ((0.0, _COLUMN_SPLIT), (_COLUMN_SPLIT, page.width)):
            column = [word for word in words if x0 <= word["x0"] < x1]
            for line in _group_lines(column):
                kind, line_text = _classify(line)
                if kind == "skip" or line_text.startswith(_SECTION_MARKER):
                    continue
                if kind == "section":
                    if in_title and section:
                        section = f"{section} {line_text}".strip()
                    else:
                        _flush()
                        section, item, buffer, in_title = line_text, None, [], True
                    continue
                in_title = False
                if kind == "subheader":
                    _flush()
                    item, buffer = None, []
                elif kind == "item":
                    if item is not None and not buffer:
                        item = f"{item} {line_text}".strip()
                    else:
                        _flush()
                        item, buffer = line_text, []
                elif kind == "basis":
                    continue
                elif item:
                    buffer.append(line_text)
    _flush()
    return definitions


def _fetch_guide() -> bytes:
    """Download the BHCPR User's Guide PDF."""
    from openbb_core.provider.utils.helpers import make_request

    return make_request(GUIDE_URL).content


def fetch_bhcpr_definitions() -> dict[str, str]:
    """Return the cached ``{section-item: definition}`` map parsed from the guide."""
    import io

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, str]:
        """Download and parse the guide into the definition map."""
        import pdfplumber

        with pdfplumber.open(io.BytesIO(_fetch_guide())) as pdf:
            return _parse_pages(pdf.pages)

    return cached(
        "bhcpr_guide_definitions",
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def bhcpr_narrative(
    definitions: dict[str, str], section: str, label: str
) -> str | None:
    """Resolve a report line item's definition, preferring a same-section match.

    The item is matched by normalized label within its report section; when the
    guide names the section differently, it falls back to a unique match on the
    label alone across all sections.
    """
    key = _norm(label)
    if not key:
        return None
    scoped = f"{_norm(section)}{_SEP}{key}"
    if scoped in definitions:
        return definitions[scoped]
    matches = {
        value
        for stored, value in definitions.items()
        if stored.endswith(f"{_SEP}{key}")
    }
    return matches.pop() if len(matches) == 1 else None
