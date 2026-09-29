"""Standalone helper functions for OECD SDMX metadata."""

import re
from pathlib import Path
from typing import Any


def _get_user_cache_file() -> Path:
    """Resolve the user-writable cache path via OpenBB core settings."""
    try:
        from openbb_core.app.utils import get_user_cache_directory

        return Path(get_user_cache_directory()) / "oecd_cache.json.gz"
    except Exception:  # noqa: BLE001
        return Path.home() / ".openbb_platform" / "cache" / "oecd_cache.json.gz"


def _make_request(url: str, headers: dict | None = None, timeout: int = 30) -> Any:
    """Make a HTTP GET request.  Fails immediately on 429."""
    from openbb_core.provider.utils.helpers import make_request

    resp = make_request(url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    return resp


def _normalize_label(label: str) -> str:
    """Normalise a country / concept label to lower_snake_case."""
    label = re.sub(r"\s*\(.*?\)\s*", "", label)
    label = label.split(",")[0]
    label = label.strip().lower().replace("-", "_").replace(" ", "_")
    label = re.sub(r"_+", "_", label)

    return label.strip("_")


def _build_code_tree(
    codes: dict[str, str],
    parents: dict[str, str],
    descriptions: dict[str, str],
) -> list[dict]:
    """Build a tree from a flat mapping of codes -> labels using parent refs.

    Parameters
    ----------
    codes : dict[str, str]
        {code: label} for every code that should appear in the tree.
    parents : dict[str, str]
        {code: parent_code} for codes that have a parent.
    descriptions : dict[str, str]
        {code: description} for extended descriptions.

    Returns
    -------
    list[dict]
        Tree of {'code', 'label', 'description', 'children': [...]} dicts.
    """
    nodes: dict[str, dict] = {}

    for code, label in codes.items():
        nodes[code] = {
            "code": code,
            "label": label,
            "description": descriptions.get(code, label),
            "children": [],
        }

    roots: list[dict] = []

    for code in list(nodes):
        parent = parents.get(code)

        if parent and parent in nodes:
            nodes[parent]["children"].append(nodes[code])
        else:
            roots.append(nodes[code])

    def _sort(items: list[dict]):
        items.sort(key=lambda n: n["label"])

        for item in items:
            if item["children"]:
                _sort(item["children"])

    _sort(roots)

    return roots


def _parse_sdmx_json_codelists(
    raw: dict,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Extract codelists and parent hierarchies from an SDMX-JSON structure response.

    Returns
    -------
    tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]
        (codelists, codelist_parents) where:
        - codelists: {cl_id: {code: label}}
        - codelist_parents: {cl_id: {code: parent_code}}  (only codes that have a parent)
    """
    codelists: dict[str, dict[str, str]] = {}
    codelist_parents: dict[str, dict[str, str]] = {}
    raw_cls = raw.get("data", raw).get("codelists", [])

    for cl in raw_cls:
        bare_id = cl.get("id", "")
        agency = cl.get("agencyID", "")
        version = cl.get("version", "")
        cl_id = f"{agency}:{bare_id}({version})" if agency and version else bare_id
        codes: dict[str, str] = {}
        parents: dict[str, str] = {}

        for code in cl.get("codes", []):
            code_id = code.get("id", "")
            names = code.get("names", {})
            code_label = (
                names.get("en", "") if isinstance(names, dict) else ""
            ) or code.get("name", code_id)
            codes[code_id] = code_label
            parent = code.get("parent", "")

            if parent:
                parents[code_id] = parent

        if cl_id:
            codelists[cl_id] = codes

            if parents:
                codelist_parents[cl_id] = parents

    return codelists, codelist_parents


def _extract_codelist_id_from_urn(urn: str) -> str:
    """Extract the fully-qualified codelist key from an SDMX URN string.

    Parameters
    ----------
    urn : str
        SDMX URN, e.g.::

            urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD.SDD.TPS:CL_REF_AREA(3.0)
            urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_FREQ(2.1)

    Returns
    -------
    str
        The fully-qualified key, e.g.
        ``"OECD.SDD.TPS:CL_REF_AREA(3.0)"`` or ``"OECD:CL_FREQ(2.1)"``.
    """
    match = re.search(r"=([^=]+:[^(]+\([^)]+\))", urn)
    if match:
        return match.group(1)
    match2 = re.search(r":([^:(]+)\(", urn)

    if match2:
        return match2.group(1)

    if ":" in urn:
        return urn.rsplit(":", 1)[-1].split("(", maxsplit=1)[0]

    return urn


def _extract_concept_id_from_urn(urn: str) -> str:
    """Extract the concept ID from an SDMX concept identity URN.

    Parameters
    ----------
    urn : str
        SDMX concept URN, e.g.::

            urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=OECD:CS_COMMON(2.0).FREQ

    Returns
    -------
    str
        The concept ID, e.g. "FREQ".
    """
    if "." in urn:
        return urn.rsplit(".", 1)[-1]

    return urn


def _parse_search_query(query: str) -> list[list[str]]:
    """Parse a search query into OR-groups of AND-terms.

    Semicolon ; separates phrases (OR at phrase level).
    Space within a phrase is implicit AND.
    Pipe | within a term is OR at term level.

    Returns
    -------
    list[list[str]]
        [[term1, term2], [term3]] where outer list is OR,
        inner lists are AND.
    """
    if not query:
        return []

    phrases = [p.strip() for p in query.split(";") if p.strip()]
    result: list[list[str]] = []

    for phrase in phrases:
        words = re.sub(r"\s*\|\s*", "|", phrase)
        words = words.replace("+", " ")

        terms = [t.strip().lower() for t in words.split() if t.strip()]

        if terms:
            result.append(terms)

    return result


def _matches_query(text: str, phrases: list[list[str]]) -> bool:
    """Check if *text* matches any phrase (OR) where all terms match (AND).

    Within a single term, | is an OR: "gdp|gross" matches if
    *either* "gdp" or "gross" is in *text*.
    """
    if not phrases:
        return True

    return any(
        all(_term_matches(text, term) for term in and_terms) for and_terms in phrases
    )


def _term_matches(text: str, term: str) -> bool:
    """Check if *term* matches *text*, supporting | as intra-term OR."""
    alternatives = [t.strip() for t in term.split("|") if t.strip()]

    return any(alt in text for alt in alternatives)
