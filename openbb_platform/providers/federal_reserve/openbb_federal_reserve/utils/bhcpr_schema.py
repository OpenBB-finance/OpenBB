"""Parse the BHCPR User's Guide PDF into an ordered hierarchical schema asset."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

GUIDE_URL = "https://www.federalreserve.gov/publications/files/2026-03-UGBHCPR.pdf"

_SECTION_MARKER = "Sample BHCPR and Definition of Items"
_RUNNING_HEADER = "Section 3:"
_TITLE_FIXES = {
    "Allowance and Net Credit Losses on Loans and Lease": (
        "Allowance and Net Credit Losses on Loans and Leases"
    ),
}


def _dehyphenate(text: str) -> str:
    """Join words split by a line-break hyphen (``prem- ises`` -> ``premises``)."""
    return re.sub(r"(\w)-\s+(\w)", r"\1\2", text).strip()


def _lines(page: Any) -> list[tuple[str, float, str]]:
    """Return each text line of a page as ``(kind, size, text)``, top to bottom."""
    out: list[tuple[str, float, str]] = []
    for line in page.extract_text_lines(layout=False, strip=True):
        chars = [char for char in line["chars"] if char["text"].strip()]
        if not chars:
            continue
        fontname = Counter(char["fontname"] for char in chars).most_common(1)[0][0]
        size = sum(char["size"] for char in chars) / len(chars)
        if "-Md" in fontname:
            kind = "md"
        elif "It" in fontname:
            kind = "italic"
        else:
            kind = "body"
        out.append((kind, size, line["text"].strip()))
    return out


def _item_basis(label: str, guide_basis: str | None) -> str | None:
    """Return the item's basis from the guide's own text, or ``None``."""
    if guide_basis:
        return guide_basis
    if re.search(r"\(\$?\s*000s?\)", label):
        return "Dollar Amount in Thousands"
    if re.search(r"\(X\)\s*$", label):
        return "Multiple (X)"
    if re.match(r"(?i)^number\b", label) or "number of" in label.lower():
        return "Number"
    if " / " in label:
        return label.split(" / ", 1)[1].strip()
    return None


def parse_guide_schema(content: bytes) -> list[dict[str, Any]]:
    """Parse the guide PDF into the ordered, hierarchical BHCPR schema.

    Parameters
    ----------
    content : bytes
        The raw *User's Guide for the BHCPR* PDF bytes.

    Returns
    -------
    list[dict]
        One entry per report section, ``{"section", "entries"}``. Each entry is a
        ``{"kind": "subheader"|"item", "label", "level", ...}`` in report order.
        ``level`` is the nesting depth (parents and their children). Items also
        carry ``basis`` (the guide's ratio basis or unit marker) and ``definition``
        (the book-weight prose; the ``(Percent of ...)`` basis itself when the guide
        repeats an item under a second basis without restating the prose).
    """
    import io

    import pdfplumber

    schema: list[dict[str, Any]] = []
    by_title: dict[str, dict[str, Any]] = {}
    section: dict[str, Any] | None = None
    parent: str | None = None
    subparent: str | None = None
    label: str | None = None
    level = 0
    guide_basis: str | None = None
    definition: list[str] = []
    name_open = False

    def flush() -> None:
        """Append the accumulated item to the current section, then reset."""
        nonlocal label, guide_basis, definition, name_open
        if section is not None and label:
            clean_basis = guide_basis.strip("() ").strip() if guide_basis else None
            prose = _dehyphenate(" ".join(definition)).strip()
            section["entries"].append(
                {
                    "kind": "item",
                    "label": label.strip(),
                    "level": level,
                    "basis": _item_basis(label.strip(), clean_basis),
                    "definition": prose or clean_basis or None,
                }
            )
        label, guide_basis, definition, name_open = None, None, [], False

    started = False
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            if _SECTION_MARKER in (page.extract_text() or ""):
                started = True
            if not started:
                continue
            for kind, size, text in _lines(page):
                if text.startswith(_RUNNING_HEADER):
                    continue
                if kind == "md" and size >= 11.5:
                    flush()
                    parent = subparent = None
                    title = _TITLE_FIXES.get(text, text)
                    section = by_title.get(title)
                    if section is None:
                        section = {"section": title, "entries": []}
                        by_title[title] = section
                        schema.append(section)
                elif kind == "md":
                    flush()
                    if size >= 10.5:
                        parent, subparent, depth = text, None, 0
                    else:
                        subparent, depth = text, (1 if parent else 0)
                    if section is not None:
                        section["entries"].append(
                            {"kind": "subheader", "label": text, "level": depth}
                        )
                elif kind == "italic":
                    open_basis = bool(guide_basis) and guide_basis.count(
                        "("
                    ) > guide_basis.count(")")
                    if text.startswith("(") or open_basis:
                        guide_basis = f"{guide_basis} {text}" if guide_basis else text
                    else:
                        if definition or guide_basis:
                            flush()
                        if not name_open:
                            level = (1 if parent else 0) + (1 if subparent else 0)
                        label = (
                            f"{label} {text}".strip() if label and name_open else text
                        )
                        name_open = True
                elif label is not None:
                    name_open = False
                    definition.append(text)
    flush()

    return [
        entry for entry in schema if any(e["kind"] == "item" for e in entry["entries"])
    ]


def load_schema() -> list[dict[str, Any]]:
    """Return the committed BHCPR schema asset (sections in report order)."""
    import json
    from pathlib import Path

    asset = Path(__file__).resolve().parents[1] / "assets" / "bhcpr" / "schema.json"
    return json.loads(asset.read_text(encoding="utf-8"))


def section_titles() -> list[str]:
    """Return the BHCPR section titles in report order, from the schema asset."""
    return [section["section"] for section in load_schema()]
