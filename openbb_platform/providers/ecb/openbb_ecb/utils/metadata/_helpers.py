"""Stateless helpers for the ECB metadata layer."""

from __future__ import annotations

import re

from openbb_ecb.utils.metadata._constants import NS, XML_LANG


def parse_search_query(query: str) -> list[list[str]]:
    """Parse a search string into an OR-of-AND term matrix."""
    query = (query or "").strip().lower()
    if not query:
        return []
    or_groups: list[list[str]] = []
    for or_part in query.split("|"):
        terms: list[str] = []
        for match in re.finditer(r'"([^"]+)"|(\S+)', or_part):
            phrase, word = match.group(1), match.group(2)
            if phrase:
                terms.append(phrase.strip())
            elif word and word != "+":
                terms.extend(t for t in word.split("+") if t)
        if terms:
            or_groups.append(terms)
    return or_groups


def matches_query(haystack: str, parsed_query: list[list[str]]) -> bool:
    """Return True if ``haystack`` satisfies the parsed OR-of-AND query."""
    if not parsed_query:
        return True
    hay = haystack.lower()
    return any(all(term in hay for term in group) for group in parsed_query)


def en_text(elem, tag: str) -> str:
    """Return the English text of a ``com:`` child of ``elem``."""
    if elem is None:
        return ""
    found = None
    for child in elem.findall(f"com:{tag}", NS):
        found = child
        if child.get(XML_LANG) == "en":
            break
    return (found.text or "").strip() if found is not None else ""
