#!/usr/bin/env python
"""Generate the shipped oecd_cache.pkl.xz baseline cache.

Run from the oecd provider root:

    python generate_cache.py

Uses **bulk** SDMX v2 endpoints to fetch everything in ~4 API calls:

  1. /structure/dataflow        — all dataflow IDs/names (~1400+)
  2. /structure/datastructure   — all DSDs (dimensions, codelist refs)
  3. /structure/codelist        — all codelists (code->label mappings)
  3b. /structure/hierarchicalcodelist — nested hierarchies (parent-child)
  4. /structure/categoryscheme  + /structure/categorisation — taxonomy

Then joins dataflows->DSDs->codelists in memory, derives parameters and
indicators for every dataflow, and writes the result to
openbb_oecd/assets/oecd_cache.pkl.xz.

This file ships with the package so users have a complete metadata map
with zero API calls at runtime.
"""

# pylint: disable=C0302,R0914
# flake8: noqa: T201

from __future__ import annotations

import json
import lzma
import pickle
import re
import time
from collections import defaultdict
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CACHE_FILE = ASSETS_DIR / "oecd_cache.pkl.xz"
BASE_URL = "https://sdmx.oecd.org/public/rest/v2"
STRUCTURE_ACCEPT = "application/vnd.sdmx.structure+json; version=1.0; charset=utf-8"
_CL_URN_RE = re.compile(r"Codelist=([^:]+):([^(]+)\(([^)]+)\)")
_DSD_URN_RE = re.compile(r"DataStructure=([^:]+):([^(]+)\(([^)]+)\)")
_CATEGORISATION_DF_RE = re.compile(r"Dataflow=([^:]+):([^(]+)\(([^)]+)\)")
_CATEGORISATION_CAT_RE = re.compile(r"OECDCS1\([^)]+\)\.(.+)")
_session = requests.Session()
_session.headers["Accept"] = STRUCTURE_ACCEPT


def _get(url: str, retries: int = 5, backoff: float = 3.0) -> dict:
    """GET *url* and return parsed JSON.  Retries on transient failures."""
    for attempt in range(retries):
        try:
            resp = _session.get(url, timeout=300)
            if resp.status_code == 429:
                wait = max(15, backoff * (attempt + 1) * 5)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            if attempt == retries - 1:
                raise
            wait = backoff * (attempt + 1)
            time.sleep(wait)
    raise requests.RequestException(f"failed after {retries} attempts: {url}")


def _extract_codelist_id(urn: str) -> str:
    """Extract the fully-qualified codelist key from a URN.

    Returns ``agency:id(version)`` so that codelists from different
    agencies (e.g. ``OECD.SDD.STES:CL_MEASURE(1.0)`` vs
    ``OECD.WISE.WDP:CL_MEASURE(1.1)``) never collide.
    """
    m = _CL_URN_RE.search(urn)
    if m:
        return f"{m.group(1)}:{m.group(2)}({m.group(3)})"
    if ":" in urn:
        return urn.rsplit(":", 1)[-1].split("(")[0]
    return urn


# ---------------------------------------------------------------------------
# Step 1 -- Fetch all dataflows
# ---------------------------------------------------------------------------


def fetch_dataflows() -> tuple[dict[str, dict], dict[str, str]]:
    """Return (dataflows dict keyed by full_id, short_id_map)."""
    raw = _get(f"{BASE_URL}/structure/dataflow")
    dataflows: dict[str, dict] = {}
    short_id_map: dict[str, str] = {}

    for df in raw.get("data", raw).get("dataflows", []):
        full_id = df.get("id", "")
        agency_id = df.get("agencyID", "")
        version = df.get("version", "")
        names = df.get("names", {})
        name = (names.get("en", "") if isinstance(names, dict) else "") or df.get(
            "name", full_id
        )
        struct_urn = df.get("structure", "")
        short_id = full_id.split("@")[-1] if "@" in full_id else full_id
        dsd_key = ""
        m = _DSD_URN_RE.search(struct_urn)

        if m:
            dsd_key = f"{m.group(1)}:{m.group(2)}({m.group(3)})"

        dataflows[full_id] = {
            "short_id": short_id,
            "agency_id": agency_id,
            "version": version,
            "name": name,
            "_dsd_key": dsd_key,
        }
        short_id_map[short_id] = full_id

    return dataflows, short_id_map


# ---------------------------------------------------------------------------
# Step 2 -- Fetch all DSDs (bulk)
# ---------------------------------------------------------------------------


def fetch_all_dsds() -> dict[str, dict]:
    """Fetch all DSDs in one call.  Returns {agency:id(ver): parsed_dsd}."""
    raw = _get(f"{BASE_URL}/structure/datastructure")
    result: dict[str, dict] = {}

    for dsd in raw.get("data", raw).get("dataStructures", []):
        dsd_id = dsd.get("id", "")
        dsd_agency = dsd.get("agencyID", "")
        dsd_version = dsd.get("version", "")
        key = f"{dsd_agency}:{dsd_id}({dsd_version})"

        dims: list[dict] = []
        components = dsd.get("dataStructureComponents", {})
        for dim in components.get("dimensionList", {}).get("dimensions", []):
            dim_id = dim.get("id", "")
            position = dim.get("position", len(dims))
            local_repr = dim.get("localRepresentation", {})
            enum_urn = local_repr.get("enumeration", "")
            cl_id = _extract_codelist_id(enum_urn) if enum_urn else ""
            names = dim.get("names", {})
            dim_name = (
                names.get("en", "") if isinstance(names, dict) else ""
            ) or dim.get("name", dim_id)
            dims.append(
                {
                    "id": dim_id,
                    "position": position,
                    "codelist_id": cl_id,
                    "name": dim_name,
                }
            )
        dims.sort(key=lambda d: d["position"])

        time_dims = components.get("dimensionList", {}).get("timeDimensions", [])
        result[key] = {
            "dimensions": dims,
            "has_time_dimension": bool(time_dims),
        }

    return result


# ---------------------------------------------------------------------------
# Step 3 -- Fetch all codelists (bulk)
# ---------------------------------------------------------------------------


def fetch_all_codelists() -> tuple[
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    list[dict],
]:
    """Fetch all codelists in one call, with hierarchical codelists.

    Uses ``?references=hierarchicalcodelist`` so the single bulk call
    returns both the flat codelists **and** any associated hierarchical
    codelists (HCLs), avoiding per-agency HCL fetches.

    Returns
    -------
    tuple
        (codelists_by_id, codelist_descriptions_by_id, codelist_parents_by_id,
         codelist_comp_rules_by_id, raw_hcls).
        Keys are fully-qualified ``agency:id(version)`` strings so that
        codelists from different agencies (e.g. multiple ``CL_MEASURE``
        variants) never collide.
        codelist_descriptions_by_id maps {cl_key: {code: description}}.
        codelist_parents_by_id maps {cl_key: {code: parent_code}} — only
        for codelists whose codes have a ``parent`` field.
        codelist_comp_rules_by_id maps {cl_key: {code: comp_rule_string}} —
        extracted from ``COMP_RULE`` annotations on codes.
        raw_hcls is the list of hierarchicalCodelist dicts from the response.
    """
    raw = _get(f"{BASE_URL}/structure/codelist?references=hierarchicalcodelist")
    by_id: dict[str, dict[str, str]] = {}
    descs_by_id: dict[str, dict[str, str]] = {}
    parents_by_id: dict[str, dict[str, str]] = {}
    comp_rules_by_id: dict[str, dict[str, str]] = {}

    for cl in raw.get("data", raw).get("codelists", []):
        bare_id = cl.get("id", "")
        agency = cl.get("agencyID", "")
        version = cl.get("version", "")
        cl_id = f"{agency}:{bare_id}({version})" if agency and version else bare_id

        codes: dict[str, str] = {}
        descs: dict[str, str] = {}
        parents: dict[str, str] = {}
        comp_rules: dict[str, str] = {}

        for code in cl.get("codes", []):
            code_id = code.get("id", "")
            names = code.get("names", {})
            label = (
                names.get("en", "") if isinstance(names, dict) else ""
            ) or code.get("name", code_id)
            codes[code_id] = label

            d = code.get("descriptions", {})
            desc = (d.get("en", "") if isinstance(d, dict) else "") or code.get(
                "description", ""
            )
            descs[code_id] = desc or label

            parent = code.get("parent")
            if parent:
                parents[code_id] = parent

            # Extract COMP_RULE annotation — defines the composition of
            # aggregate codes (e.g. "CP045+CP0722" for Energy).
            for ann in code.get("annotations", []):
                if ann.get("type") == "COMP_RULE":
                    rule = ann.get("title", "")
                    if rule:
                        comp_rules[code_id] = rule
                    break

        if cl_id:
            by_id[cl_id] = codes
            descs_by_id[cl_id] = descs
            if parents:
                parents_by_id[cl_id] = parents
            if comp_rules:
                comp_rules_by_id[cl_id] = comp_rules

    raw_hcls: list[dict] = raw.get("data", raw).get("hierarchicalCodelists", [])
    print(f"    {len(raw_hcls)} hierarchical codelists included via ?references")

    return by_id, descs_by_id, parents_by_id, comp_rules_by_id, raw_hcls


# ---------------------------------------------------------------------------
# Step 3b -- Infer orphan parents from COMP_RULE annotations
# ---------------------------------------------------------------------------


def infer_orphan_parents(
    parents_by_id: dict[str, dict[str, str]],
    comp_rules_by_id: dict[str, dict[str, str]],
    codelists_by_id: dict[str, dict[str, str]],
) -> None:
    """Infer parents for orphan codes using COMP_RULE annotations.

    Mutates *parents_by_id* in place.  For each codelist that has both
    parent data and COMP_RULE annotations, this resolves orphan codes
    (codes without an explicit ``parent``) by computing the closest
    common ancestor of the COMP_RULE component codes.

    For example, if ``CP041T043`` has COMP_RULE ``CP041+CP042+CP043`` and
    all three components have ``parent=CP04``, then ``CP041T043`` is
    inferred to be a child of ``CP04``.
    """
    for cl_id, comp_rules in comp_rules_by_id.items():
        parents = parents_by_id.get(cl_id)
        if parents is None:
            # Codelist doesn't have any parent info — COMP_RULE alone
            # can't tell us the hierarchy.
            continue
        codelist_codes = codelists_by_id.get(cl_id, {})
        if not codelist_codes:
            continue

        for code, rule in comp_rules.items():
            if code in parents:
                # Already has an explicit parent.
                continue

            # Parse COMP_RULE: "CP045+CP0722" → ["CP045", "CP0722"]
            components = [c.strip() for c in rule.split("+") if c.strip()]
            if not components:
                continue

            # Find closest common ancestor of all component codes.
            ancestor = _closest_common_ancestor(components, parents)
            if ancestor and ancestor in codelist_codes:
                parents[code] = ancestor

    # Second pass: codes that are referenced as parent by other codes
    # but don't themselves have a parent → they're root nodes.  We don't
    # assign them a synthetic parent — they're genuinely top-level.


# ---------------------------------------------------------------------------
# Step 3c -- Fetch hierarchical codelists (HCLs)
# ---------------------------------------------------------------------------

_HCL_CODE_URN_RE = re.compile(r"Code=([^:]+):([^(]+)\(([^)]+)\)\.(.+)")


def _extract_hcl_parents(
    hierarchical_codes: list[dict],
    parent_id: str | None = None,
    result: dict[str, str] | None = None,
) -> dict[str, str]:
    """Recursively extract parent-child relationships from nested HCL codes."""
    if result is None:
        result = {}
    for hc in hierarchical_codes:
        code_id = hc.get("codeID", hc.get("id", ""))
        if parent_id and code_id not in result:
            result[code_id] = parent_id
        children = hc.get("hierarchicalCodes", [])
        if children:
            _extract_hcl_parents(children, code_id, result)
    return result


def parse_hierarchical_codelists(
    raw_hcls: list[dict],
    referenced_cl_ids: set[str],
) -> dict[str, dict[str, str]]:
    """Parse pre-fetched hierarchical codelists into parent-child maps.

    The HCL data is returned by the bulk codelist fetch when using
    ``?references=hierarchicalcodelist`` — no extra API calls needed.

    Parameters
    ----------
    raw_hcls
        The list of hierarchicalCodelist dicts from the bulk response.
    referenced_cl_ids
        The set of fully-qualified codelist keys (``agency:id(ver)``)
        that are actually used by dataflow dimensions.

    Returns
    -------
    dict
        ``{cl_key: {code: parent_code}}`` for each codelist that has
        HCL hierarchy data.
    """
    if not raw_hcls:
        return {}

    # Map "agency:bare_id(" prefix → actual fully-qualified key.
    _prefix_to_key: dict[str, str] = {}
    for key in referenced_cl_ids:
        m = _CL_URN_RE.search(f"Codelist={key}")
        if m:
            _prefix_to_key[f"{m.group(1)}:{m.group(2)}("] = key

    # Parse HCLs: group extracted parents by base codelist.
    result: dict[str, dict[str, str]] = {}
    for hcl in raw_hcls:
        for h in hcl.get("hierarchies", []):
            top_codes = h.get("hierarchicalCodes", [])
            if not top_codes:
                continue
            # Identify target codelist from the first code's URN.
            urn = top_codes[0].get("code", "")
            m = _HCL_CODE_URN_RE.search(urn)
            if not m:
                continue
            hcl_agency = m.group(1)
            hcl_cl = m.group(2)
            # Map to actual key via version-agnostic prefix.
            prefix = f"{hcl_agency}:{hcl_cl}("
            actual_key = _prefix_to_key.get(prefix)
            if not actual_key:
                continue
            parents = _extract_hcl_parents(top_codes)
            if parents:
                result.setdefault(actual_key, {}).update(parents)

    return result


def merge_hcl_parents(
    codelist_parents: dict[str, dict[str, str]],
    hcl_parents: dict[str, dict[str, str]],
    codelists_by_id: dict[str, dict[str, str]],
) -> int:
    """Merge HCL-derived parents into *codelist_parents* for orphan codes.

    Only fills in parents for codes that:
    1. Don't already have a parent (from the flat codelist or COMP_RULE).
    2. Both child and parent exist in the flat codelist.

    Mutates *codelist_parents* in place.  Returns the number of parents added.
    """
    added = 0
    for cl_key, hcl_map in hcl_parents.items():
        existing = codelist_parents.get(cl_key, {})
        flat_codes = set(codelists_by_id.get(cl_key, {}))
        if not flat_codes:
            continue
        for code, parent in hcl_map.items():
            if code in existing:
                continue  # already has a parent
            if code in flat_codes and parent in flat_codes:
                if cl_key not in codelist_parents:
                    codelist_parents[cl_key] = {}
                codelist_parents[cl_key][code] = parent
                added += 1
    return added


def _closest_common_ancestor(
    codes: list[str],
    parents: dict[str, str],
) -> str | None:
    """Compute the closest common ancestor of *codes* in the parent tree.

    Returns ``None`` if no common ancestor can be determined (e.g. codes
    are from different root branches or not found in the parent map).
    """

    def _ancestors(code: str) -> list[str]:
        """Return ancestor chain from immediate parent to root."""
        chain: list[str] = []
        visited: set[str] = set()
        current = code
        while current in parents:
            p = parents[current]
            if p in visited:
                break  # cycle guard
            visited.add(p)
            chain.append(p)
            current = p
        return chain

    # Build ancestor chains for each component.
    chains: list[list[str]] = []
    for code in codes:
        if code not in parents:
            # Component doesn't have a parent — it's a root code.
            # The common ancestor must include this root.
            return None
        chain = _ancestors(code)
        if not chain:
            return None
        chains.append(chain)

    if not chains:
        return None

    # Walk the first chain from nearest ancestor outward; the closest
    # common ancestor is the first one that appears in ALL other chains.
    ancestor_sets = [set(c) for c in chains[1:]]
    for ancestor in chains[0]:
        if all(ancestor in s for s in ancestor_sets):
            return ancestor

    return None


# ---------------------------------------------------------------------------
# Step 4 -- Join: map each dataflow to its DSD
# ---------------------------------------------------------------------------


def join_dataflows_to_structures(
    dataflows: dict[str, dict],
    dsds: dict[str, dict],
) -> dict[str, dict]:
    """Build {full_id: dsd} for every dataflow that has a DSD."""
    datastructures: dict[str, dict] = {}
    unmatched = 0

    # Build a version-agnostic index so we can fall back when the version
    # embedded in a dataflow's structure URN differs from the version that
    # the bulk /structure/datastructure endpoint returned.
    # Maps "agency:dsd_id" → first matching full key "agency:dsd_id(ver)".
    _base_to_key: dict[str, str] = {}
    for k in dsds:
        base = k.rsplit("(", 1)[0]  # strip "(version)" suffix
        _base_to_key.setdefault(base, k)

    for full_id, df_meta in dataflows.items():
        dsd_key = df_meta.get("_dsd_key", "")
        dsd = dsds.get(dsd_key)

        if not dsd and dsd_key:
            # Version mismatch fallback: strip version and match by agency:id.
            base = dsd_key.rsplit("(", 1)[0]
            fallback = _base_to_key.get(base)
            if fallback:
                dsd = dsds.get(fallback)

        if not dsd:
            # Last resort: infer DSD id from the "@"-prefixed full_id
            # (e.g. "DSD_STES@DF_CLI" → dsd_id "DSD_STES") and the
            # dataflow's own agency_id / version metadata.
            agency_id = df_meta.get("agency_id", "")
            version = df_meta.get("version", "")
            if "@" in full_id and agency_id:
                dsd_prefix = full_id.split("@", 1)[0]
                # Try exact inferred key first, then version-agnostic.
                inferred_key = f"{agency_id}:{dsd_prefix}({version})"
                dsd = dsds.get(inferred_key)
                if not dsd:
                    inferred_base = f"{agency_id}:{dsd_prefix}"
                    fallback = _base_to_key.get(inferred_base)
                    if fallback:
                        dsd = dsds.get(fallback)

        if not dsd:
            unmatched += 1
            continue

        # Copy so multiple dataflows sharing a DSD don't collide.
        datastructures[full_id] = {
            "dimensions": [dict(d) for d in dsd["dimensions"]],
            "has_time_dimension": dsd.get("has_time_dimension", True),
        }

    return datastructures


# ---------------------------------------------------------------------------
# Step 6 -- Derive parameters and indicators
# ---------------------------------------------------------------------------

_INDICATOR_DIMENSION_CANDIDATES = (
    "MEASURE",
    "INDICATOR",
    "SUBJECT",
    "TRANSACTION",
    "ACTIVITY",
    "PRODUCT",
    "SERIES",
    "ITEM",
    "ACCOUNTING_ENTRY",
    "SECTOR",
)

_COUNTRY_DIMENSION_CANDIDATES = (
    "REF_AREA",
    "COUNTERPART_AREA",
    "JURISDICTION",
    "COUNTRY",
    "AREA",
)

# Dimensions that are NEVER indicators — they describe how data is
# measured, adjusted, or transformed, not what is being measured.
_NON_INDICATOR_DIMENSIONS = (
    "FREQ",
    "ADJUSTMENT",
    "TRANSFORMATION",
    "UNIT_MEASURE",
    "UNIT_MULT",
    "CURRENCY_DENOM",
    "CURRENCY",
    "VALUATION",
    "PRICE_BASE",
    "CONSOLIDATION",
    "MATURITY",
    "METHODOLOGY",
    "TABLE_IDENTIFIER",
    "TIME_PERIOD",
    "COUNTERPART_AREA",
    "DEBT_BREAKDOWN",
)


def derive_parameters(
    datastructures: dict[str, dict],
    codelists_by_id: dict[str, dict[str, str]],
) -> dict[str, dict[str, list[dict]]]:
    """Build {full_id: {dim_id: [{label, value}, ...]}}."""
    result: dict[str, dict[str, list[dict]]] = {}

    for full_id, dsd in datastructures.items():
        params: dict[str, list[dict]] = {}

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")
            codes = codelists_by_id.get(cl_id, {}) if cl_id else {}
            params[dim_id] = [
                {"label": label, "value": code} for code, label in sorted(codes.items())
            ]

        result[full_id] = params

    return result


def derive_indicators(
    datastructures: dict[str, dict],
    dataflow_parameters: dict[str, dict[str, list[dict]]],
    codelist_descriptions: dict[str, dict[str, str]],
    codelist_parents: dict[str, dict[str, str]] | None = None,
) -> dict[str, dict]:
    """Build {full_id: {dims: [{dim_id, codes: [...]}]}}.

    Every content dimension (not country, not freq, not metadata) gets
    its codes enumerated so each individual code is a searchable
    indicator that produces time series.
    """
    if codelist_parents is None:
        codelist_parents = {}
    _skip = (
        set(_COUNTRY_DIMENSION_CANDIDATES)
        | set(_NON_INDICATOR_DIMENSIONS)
        | {"FREQ", "TIME_PERIOD"}
    )
    result: dict[str, dict] = {}

    for full_id, dsd in datastructures.items():
        params = dataflow_parameters.get(full_id, {})
        dims_sorted = sorted(
            dsd.get("dimensions", []), key=lambda d: d.get("position", 0)
        )

        # Identify ALL content dimensions.
        content_dims: list[str] = []
        for d in dims_sorted:
            d_id = d["id"]
            if d_id not in _skip and d_id in params and params[d_id]:
                content_dims.append(d_id)

        if not content_dims:
            result[full_id] = {"dims": []}
            continue

        dim_codelist_map: dict[str, str] = {}
        for d in dsd.get("dimensions", []):
            dim_codelist_map[d["id"]] = d.get("codelist_id", "")

        dims_list: list[dict] = []
        seen_codes: set[str] = set()

        for dim_id in content_dims:
            cl_id = dim_codelist_map.get(dim_id, "")
            descriptions = codelist_descriptions.get(cl_id, {})
            parents = codelist_parents.get(cl_id, {})
            codes: list[dict] = []

            for entry in params[dim_id]:
                code = entry["value"]
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                desc = descriptions.get(code, entry["label"])
                item: dict = {"indicator": code, "label": entry["label"]}
                if desc != entry["label"]:
                    item["description"] = desc
                if code in parents:
                    item["parent"] = parents[code]
                codes.append(item)

            if codes:
                dims_list.append({"dim_id": dim_id, "codes": codes})

        result[full_id] = {"dims": dims_list}

    return result


# ---------------------------------------------------------------------------
# Step 7 -- Fetch topic taxonomy
# ---------------------------------------------------------------------------


def _parse_category_tree(
    categories: list[dict],
    prefix: str = "",
) -> tuple[list[dict], dict[str, str]]:
    """Recursively parse a category scheme into a tree and flat name map."""
    tree: list[dict] = []
    names: dict[str, str] = {}
    for cat in categories:
        cid = cat.get("id", "")
        cnames = cat.get("names", {})
        name = (cnames.get("en", "") if isinstance(cnames, dict) else "") or cat.get(
            "name", cid
        )
        path = f"{prefix}.{cid}" if prefix else cid
        names[path] = name
        children, child_names = _parse_category_tree(cat.get("categories", []), path)
        names.update(child_names)
        tree.append(
            {
                "id": cid,
                "name": name,
                "path": path,
                "children": children,
            }
        )
    return tree, names


def fetch_taxonomy(
    dataflows: dict[str, dict],
) -> tuple[list[dict], dict[str, str], dict[str, list[str]], dict[str, list[str]]]:
    """Return (taxonomy_tree, category_names, df_to_categories, category_to_dfs)."""

    cs_raw = _get(f"{BASE_URL}/structure/categoryscheme/OECD/OECDCS1")
    schemes = cs_raw.get("data", cs_raw).get("categorySchemes", [])
    if not schemes:
        return [], {}, {}, {}

    tree, category_names = _parse_category_tree(schemes[0].get("categories", []))

    cat_raw = _get(f"{BASE_URL}/structure/categorisation")
    raw_cats = cat_raw.get("data", cat_raw).get("categorisations", [])

    seen: dict[tuple[str, str], str] = {}
    for entry in raw_cats:
        src = entry.get("source", "")
        tgt = entry.get("target", "")
        m_df = _CATEGORISATION_DF_RE.search(src)
        m_cat = _CATEGORISATION_CAT_RE.search(tgt)
        if not m_df or not m_cat:
            continue
        agency = m_df.group(1)
        dsd_df = m_df.group(2)
        version = m_df.group(3)
        cat_path = m_cat.group(1)
        full_ext = f"{agency}:{dsd_df}"
        key = (full_ext, cat_path)
        if version >= seen.get(key, ""):
            seen[key] = version

    df_to_cats: dict[str, list[str]] = defaultdict(list)
    cat_to_dfs: dict[str, list[str]] = defaultdict(list)
    for (ext_id, cat_path), _ in seen.items():
        dsd_df = ext_id.split(":", 1)[-1] if ":" in ext_id else ext_id
        if dsd_df not in dataflows:
            continue
        if cat_path not in df_to_cats[dsd_df]:
            df_to_cats[dsd_df].append(cat_path)
        if dsd_df not in cat_to_dfs[cat_path]:
            cat_to_dfs[cat_path].append(dsd_df)

    return tree, category_names, dict(df_to_cats), dict(cat_to_dfs)


# ---------------------------------------------------------------------------
# Step 8 -- Fetch content constraints (batch)
# ---------------------------------------------------------------------------

_CC_DF_URN_RE = re.compile(r"Dataflow=([^:]+):([^(]+)\(([^)]+)\)")


def fetch_all_constraints(
    dataflows: dict[str, dict],
) -> dict[str, dict[str, list[str]]]:
    """Fetch all content constraints for agencies that own dataflows.

    Uses the bulk ``/structure/contentconstraint/{agency}`` endpoint so
    that we need only one API call per agency instead of one per dataflow.

    Returns
    -------
    dict
        ``{dataflow_full_id: {dim_id: [value, ...]}}``
    """
    # Collect distinct agencies that own at least one dataflow.
    agencies: set[str] = set()
    for df_meta in dataflows.values():
        aid = df_meta.get("agency_id", "")
        if aid:
            agencies.add(aid)

    result: dict[str, dict[str, list[str]]] = {}
    agencies_sorted = sorted(agencies)

    for i, agency in enumerate(agencies_sorted, 1):
        url = f"{BASE_URL}/structure/contentconstraint/{agency}"
        raw = None
        for attempt in range(6):
            try:
                resp = _session.get(url, timeout=120)
                if resp.status_code == 404:
                    break
                if resp.status_code == 429:
                    wait = 20 * (attempt + 1)
                    print(
                        f"    [{i}/{len(agencies_sorted)}] {agency}: 429 — waiting {wait}s"
                    )
                    time.sleep(wait)
                    continue
                if resp.status_code != 200:
                    break
                raw = resp.json()
                # Pace after successful response to stay under rate limit.
                time.sleep(3)
                break
            except Exception:  # noqa: S112, BLE001
                if attempt < 5:
                    time.sleep(3 * (attempt + 1))
        if raw is None:
            continue
        print(f"    [{i}/{len(agencies_sorted)}] {agency}")

        for cc in raw.get("data", raw).get("contentConstraints", []):
            # Identify the attached dataflow.
            attachment = cc.get("constraintAttachment", {})
            df_urns = attachment.get("dataflows", [])
            if not df_urns:
                continue
            m = _CC_DF_URN_RE.search(df_urns[0])
            if not m:
                continue
            df_full_id = m.group(2)  # e.g. "DSD_NAMAIN10@DF_TABLE1"
            if df_full_id not in dataflows:
                continue

            # Parse cube regions.
            for region in cc.get("cubeRegions", []):
                dim_constraints: dict[str, list[str]] = {}
                for kv in region.get("keyValues", []):
                    dim_id = kv.get("id", "")
                    vals = kv.get("values", [])
                    if dim_id and vals:
                        dim_constraints[dim_id] = sorted(vals)
                if dim_constraints:
                    existing = result.get(df_full_id, {})
                    for dim_id, vals in dim_constraints.items():
                        prev = set(existing.get(dim_id, []))
                        existing[dim_id] = sorted(prev | set(vals))
                    result[df_full_id] = existing

    return result


# ---------------------------------------------------------------------------
# Step 9 -- Build table map (TABLE_IDENTIFIER → metadata)
# ---------------------------------------------------------------------------


def build_table_map(
    datastructures: dict[str, dict],
    dataflow_constraints: dict[str, dict[str, list[str]]],
    codelists_by_id: dict[str, dict[str, str]],
    codelist_descriptions: dict[str, dict[str, str]],
) -> dict[str, dict]:
    """Build a table map: ``{table_id: {name, description, dataflows}}``.

    A "table" is an OECD National Accounts TABLE_IDENTIFIER code.  The map
    connects each table ID to its human-readable name and the list of
    dataflows that serve data for that table.

    For composite/grouping codes whose names reference other table IDs
    (e.g. ``"Tables 0101, 0102 and 0103"``), dataflows are propagated
    from the referenced sub-tables so that the composite code also has a
    non-empty dataflow list.

    Returns
    -------
    dict
        ``{table_id: {"name": str, "description": str, "dataflows": [full_id, ...]}}``
    """
    # 1. Identify which codelists are used as TABLE_IDENTIFIER.
    table_codelist_ids: set[str] = set()
    for dsd in datastructures.values():
        for dim in dsd.get("dimensions", []):
            if dim.get("id") == "TABLE_IDENTIFIER":
                cl_id = dim.get("codelist_id", "")
                if cl_id:
                    table_codelist_ids.add(cl_id)

    # 2. Collect all table IDs with names/descriptions from those codelists.
    table_map: dict[str, dict] = {}
    for cl_id in table_codelist_ids:
        codes = codelists_by_id.get(cl_id, {})
        descs = codelist_descriptions.get(cl_id, {})
        for code, label in codes.items():
            if code not in table_map:
                desc = descs.get(code, label)
                table_map[code] = {
                    "name": label,
                    "description": desc if desc != label else "",
                    "dataflows": [],
                }

    # 3. Map table IDs to dataflows using constraints.
    for df_full_id, constraints in dataflow_constraints.items():
        table_ids = constraints.get("TABLE_IDENTIFIER", [])
        for tid in table_ids:
            if tid in table_map and df_full_id not in table_map[tid]["dataflows"]:
                table_map[tid]["dataflows"].append(df_full_id)

    # 4. Propagate dataflows to composite / grouping codes.
    #    Parse names like "Tables 0101, 0102 and 0103" to find sub-table IDs,
    #    then inherit their dataflows.
    _SUBTABLE_RE = re.compile(r"\b(\d{4})\b")
    for tid, entry in table_map.items():
        if entry["dataflows"]:
            continue  # already directly mapped
        name = entry["name"]
        # Look for 4-digit codes in the name that reference other table IDs.
        matches = _SUBTABLE_RE.findall(name)
        sub_ids = [f"T{m}" for m in matches if f"T{m}" in table_map and f"T{m}" != tid]
        if sub_ids:
            inherited: set[str] = set()
            for sub_id in sub_ids:
                inherited.update(table_map[sub_id]["dataflows"])
            if inherited:
                entry["dataflows"] = sorted(inherited)
                entry["sub_tables"] = sub_ids

    # Sort dataflow lists for deterministic output.
    for entry in table_map.values():
        entry["dataflows"].sort()

    return table_map


def main() -> None:
    """Generate the shipped oecd_cache.pkl.xz file."""
    t0 = time.time()
    print("Generating OECD cache... this will take a few minutes...")

    # 1. Dataflows
    dataflows, short_id_map = fetch_dataflows()

    # 2. All DSDs
    dsds = fetch_all_dsds()

    # 3. All codelists (includes hierarchical codelists via ?references)
    (
        codelists_by_id,
        codelist_descriptions,
        codelist_parents,
        codelist_comp_rules,
        raw_hcls,
    ) = fetch_all_codelists()

    # 4. Join: map every dataflow to its DSD
    datastructures = join_dataflows_to_structures(dataflows, dsds)

    # 4b. Remap dimension codelist_id to match actual keys in the cache.
    # DSDs may reference v1.0 but the bulk codelist fetch returned v1.2.
    # Build a prefix→actual_key lookup and update dimensions in place.
    _cl_prefix_map: dict[str, str] = {}  # "OECD.SDD.STES:CL_MEASURE(" → actual key

    for key in codelists_by_id:
        m = _CL_URN_RE.search(f"Codelist={key}")  # reuse existing regex
        if m:
            prefix = f"{m.group(1)}:{m.group(2)}("
            _cl_prefix_map[prefix] = key

    remapped = 0

    for dsd in datastructures.values():
        for dim in dsd.get("dimensions", []):
            cl_id = dim.get("codelist_id", "")
            if cl_id and cl_id not in codelists_by_id:
                # Try prefix match (same agency:id, different version).
                m = _CL_URN_RE.search(f"Codelist={cl_id}")
                if m:
                    prefix = f"{m.group(1)}:{m.group(2)}("
                    actual = _cl_prefix_map.get(prefix)
                    if actual:
                        dim["codelist_id"] = actual
                        remapped += 1

    # 5. Filter codelists to only those referenced by dimensions
    referenced_cl_ids: set[str] = set()

    for dsd in datastructures.values():
        for dim in dsd.get("dimensions", []):
            cl_id = dim.get("codelist_id", "")
            if cl_id:
                referenced_cl_ids.add(cl_id)

    codelists_by_id = {
        k: v for k, v in codelists_by_id.items() if k in referenced_cl_ids
    }
    codelist_parents = {
        k: v for k, v in codelist_parents.items() if k in referenced_cl_ids
    }
    codelist_comp_rules = {
        k: v for k, v in codelist_comp_rules.items() if k in referenced_cl_ids
    }

    # 5b. Infer orphan parents using COMP_RULE annotations.
    infer_orphan_parents(codelist_parents, codelist_comp_rules, codelists_by_id)

    # 5c. Parse hierarchical codelists (already fetched with codelists).
    print("  Parsing hierarchical codelists...")
    hcl_parents = parse_hierarchical_codelists(raw_hcls, referenced_cl_ids)
    print(f"    HCL hierarchies for {len(hcl_parents)} codelists")
    n_hcl = merge_hcl_parents(codelist_parents, hcl_parents, codelists_by_id)
    print(f"    HCL parents merged: {n_hcl}")

    # Only keep descriptions that differ from the label (saves ~90% of space).
    codelist_descriptions_trimmed: dict[str, dict[str, str]] = {}

    for cl_id in referenced_cl_ids:
        descs = codelist_descriptions.get(cl_id, {})
        labels = codelists_by_id.get(cl_id, {})
        differing = {
            code: desc for code, desc in descs.items() if desc != labels.get(code, "")
        }

        if differing:
            codelist_descriptions_trimmed[cl_id] = differing

    codelist_descriptions = codelist_descriptions_trimmed

    # 6a. Derive parameters
    print("  Deriving parameters...")
    dataflow_parameters = derive_parameters(datastructures, codelists_by_id)

    # 6b. Derive indicators
    print("  Deriving indicators...")
    dataflow_indicators = derive_indicators(
        datastructures,
        dataflow_parameters,
        codelist_descriptions,
        codelist_parents,
    )

    # 7. Taxonomy
    print("  Fetching taxonomy...")
    taxonomy_tree, category_names, df_to_categories, category_to_dfs = fetch_taxonomy(
        dataflows
    )

    # 8. Content constraints (batch fetch per agency).
    print("  Fetching content constraints...")
    dataflow_constraints = fetch_all_constraints(dataflows)

    # 9. Table map: TABLE_IDENTIFIER → {name, description, dataflows}.
    print("  Building table map...")
    table_map = build_table_map(
        datastructures,
        dataflow_constraints,
        codelists_by_id,
        codelist_descriptions,
    )

    # 10. Strip temporary keys from dataflows before persisting.
    for df in dataflows.values():
        df.pop("_dsd_key", None)
        df.pop("_dsd_key", None)

    # 11. Write cache
    print("  Compressing and writing cache...")
    # Note: dataflow_parameters is NOT persisted — it's 18+ MB because it
    # duplicates codelist codes across every dataflow.  It's trivially
    # derivable at runtime from datastructures + codelists (just look up the
    # codelist for each dimension).  dataflow_indicators IS persisted because
    # it's the non-trivial derived data that search_indicators() needs.
    blob = {
        "dataflows": dataflows,
        "datastructures": datastructures,
        "codelists": codelists_by_id,
        "codelist_parents": codelist_parents,
        "codelist_descriptions": codelist_descriptions,
        "codelist_comp_rules": codelist_comp_rules,
        "dataflow_constraints": dataflow_constraints,
        "dataflow_indicators": dataflow_indicators,
        "table_map": table_map,
        "short_id_map": short_id_map,
        "taxonomy_tree": taxonomy_tree,
        "df_to_categories": df_to_categories,
        "category_to_dfs": category_to_dfs,
        "category_names": category_names,
    }

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    with lzma.open(CACHE_FILE, "wb", format=lzma.FORMAT_XZ, preset=6) as fh:
        pickle.dump(blob, fh, protocol=pickle.HIGHEST_PROTOCOL)

    size_mb = CACHE_FILE.stat().st_size / (1024 * 1024)
    elapsed = time.time() - t0
    n_indicators = sum(
        sum(len(d.get("codes", [])) for d in v.get("dims", []))
        for v in dataflow_indicators.values()
    )
    n_tables = len(table_map)
    n_constraints = len(dataflow_constraints)
    print(
        f"Wrote {CACHE_FILE} ({size_mb:.1f} MB, "
        f"{len(dataflows)} dataflows, {n_indicators} indicators, "
        f"{n_constraints} constrained dataflows, {n_tables} table IDs) "
        f"in {elapsed:.0f}s"
    )


if __name__ == "__main__":
    main()
