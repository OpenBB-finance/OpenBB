"""FFIEC concept metadata: full names, narratives, and value units.

Joins the CDR XBRL taxonomy (each concept's data type - ``Monetary`` marks the
dollar values the FFIEC reports in thousands) with the MDRM data dictionary (the
official item name and definition), keyed by concept code.
"""

from __future__ import annotations

from typing import Any

_SMALL_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "per",
    "the",
    "to",
    "vs",
    "with",
}
_ACRONYMS = {
    "TE",
    "YTD",
    "QTD",
    "FTE",
    "US",
    "USD",
    "ROA",
    "ROE",
    "ROAA",
    "ROAE",
    "CD",
    "ATM",
    "ACH",
    "HTM",
    "AFS",
    "IRA",
    "TDR",
    "OREO",
    "HELOC",
    "ALLL",
    "CECL",
    "FHLB",
    "GNMA",
    "FNMA",
    "FHLMC",
    "SBA",
    "MBS",
    "CMBS",
    "ABS",
    "REIT",
    "LIP",
    "OBS",
    "PD",
    "GAAP",
    "FDIC",
    "OCC",
    "PG",
}


_GUIDE_RESIDUAL_ABBREVIATIONS = (
    (r"\bLn&Ls\b", "Loans & Leases"),
    (r"\bQtr Ann\b", "Quarter Annualized"),
    (r"\bQtr\b", "Quarter"),
)


def clean_name(raw: str | None) -> str | None:
    """Title-case an FFIEC item name (MDRM or guide Description) into a readable label.

    Drops only the section-redundant Average-Assets basis (``as a percent of
    Average Assets``, ``/PERCENT OF AVERAGE ASSETS``) the report's section already
    conveys — a meaningful denominator the ratio is named for (``% of Tier 1
    Capital``) is kept in full — the ``(***)`` footnote marker, and the Call Report
    schedule cross-reference tail (``(Included in Rc-C …)``) on Call-sourced item
    names, title-cases (keeping known acronyms upper and small words lower), then
    expands the few abbreviations the guide Description itself leaves on the
    quarterly-annualized concepts (``Ln&Ls``, ``Qtr``).
    """
    import re

    if not raw:
        return None
    text = re.sub(r"\s+", " ", raw).strip()
    # Drop only the section-redundant Average-Assets basis (``as a percent of
    # Average Assets``, ``% of Avg Assets``, ``/PERCENT OF AVERAGE ASSETS``),
    # consuming the leading connective so no dangling ``as a`` remains. A
    # meaningful denominator the ratio is named for (``% of Tier 1 Capital``,
    # ``of Average Earning Assets``, ``of Average Total Loans``) is its identity,
    # not section context, and is kept in full.
    text = re.sub(
        r"\s*(?:/\s*)?(?:as\s+)?(?:a\s+)?(?:percent|%)\s+of\s+(?:average|avg)\.?"
        r"(?:\s+total)?\s+assets\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*\(\$\d*s?\)", "", text)
    text = re.sub(r"\s*\(included in .*$", "", text, flags=re.IGNORECASE)
    # Drop the trailing parent-line cross-reference footnote (``(5408)``).
    text = re.sub(r"\s*\(\d+\)\s*$", "", text)
    text = re.sub(r"\s*\(\*+\)", "", text).strip().rstrip(".").strip()
    seen_first = [False]

    def _case(match: re.Match[str]) -> str:
        """Case one word: acronym upper, small word lower, otherwise capitalized."""
        word = match.group(0)
        is_first = not seen_first[0]
        seen_first[0] = True
        if word.upper() in _ACRONYMS:
            return word.upper()
        if not is_first and word.lower() in _SMALL_WORDS:
            return word.lower()
        return word[:1].upper() + word[1:].lower()

    titled = re.sub(r"[A-Za-z0-9]+", _case, text)
    for pattern, full in _GUIDE_RESIDUAL_ABBREVIATIONS:
        titled = re.sub(pattern, full, titled, flags=re.IGNORECASE)
    return titled or None


def _narrative(text: str | None) -> str | None:
    """Drop the FFIEC ``Pseudo MDRM`` placeholder definitions, else pass through."""
    if not text or "pseudo mdrm" in text.lower():
        return None
    return text


def indented_name(label: str | None, name: str | None) -> str | None:
    """Reapply ``label``'s report-indentation prefix (``>`` + spaces) to ``name``."""
    import re

    if not name:
        return label
    match = re.match(r">[\s ]*", label or "")
    return (match.group(0) if match else "") + name


def concept_index(
    product: str = "ubpr_ratio_single", form_type: str | None = None
) -> dict[str, dict[str, Any]]:
    """Return ``{CODE: {"name", "narrative", "monetary", "is_text"}}`` per concept.

    ``monetary`` marks dollar concepts (the FFIEC reports these in thousands);
    ``is_text`` marks free-text concepts (the ``TEXTxxxx`` itemization captions
    that carry no numeric value); ``name`` is the readable MDRM item name and
    ``narrative`` its definition.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, dict[str, Any]]:
        """Join the product taxonomy types with the MDRM name and definition maps."""
        from openbb_federal_reserve.utils.cdr import fetch_taxonomy, parse_taxonomy
        from openbb_federal_reserve.utils.mdrm import (
            fetch_mdrm_definitions,
            fetch_mdrm_dictionary,
        )

        types = {
            concept["mdrm"]: concept["data_type"]
            for concept in parse_taxonomy(fetch_taxonomy(product, form_type))
        }
        names = fetch_mdrm_dictionary()
        definitions = fetch_mdrm_definitions()
        return {
            code: {
                "name": clean_name(names.get(code)),
                "narrative": _narrative(definitions.get(code)),
                "monetary": data_type == "Monetary",
                "is_text": data_type == "Text",
            }
            for code, data_type in types.items()
        }

    return cached(
        ("concept_index", product, form_type or ""),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
