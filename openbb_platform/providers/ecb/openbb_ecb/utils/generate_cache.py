#!/usr/bin/env python
"""Generate the shipped ``ecb_cache.json.xz`` SDMX metadata baseline.

Run at build time by ``hatch_build.py`` (and exposed as the
``generate-ecb-cache`` console script). The ECB Data Portal serves
structural metadata as **SDMX-ML 2.1 (XML)** only — JSON is rejected with
HTTP 406 — so this script parses XML with the standard library
``xml.etree.ElementTree`` to avoid adding a non-stdlib parser to the
isolated PEP 517 build environment (whose only third-party package is
``requests``, declared in ``[build-system].requires``).

The catalog is assembled from six bulk structure calls and written
LZMA-compressed to ``openbb_ecb/assets/ecb_cache.json.xz``.
"""

from __future__ import annotations

import json
import lzma
import sys
import time
import xml.etree.ElementTree as ET  # noqa: S405 - trusted ECB build-time responses
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CACHE_FILE = ASSETS_DIR / "ecb_cache.json.xz"
BASE_URL = "https://data-api.ecb.europa.eu/service"
AGENCY = "ECB"
HCL_AGENCY = "ECB.DISS"  # presentation-table hierarchical code lists live here

_NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

_session = requests.Session()
_session.headers["Accept"] = "application/xml"
_session.headers["User-Agent"] = "openbb-ecb build hook"


def _get(url: str, retries: int = 5, backoff: float = 3.0) -> ET.Element | None:
    """GET ``url`` and return the parsed XML root, or ``None`` on 404/empty."""
    for attempt in range(retries):
        try:
            resp = _session.get(url, timeout=300)
            if resp.status_code == 429:
                time.sleep(max(15, backoff * (attempt + 1) * 5))
                continue
            if resp.status_code in (400, 404):
                return None
            resp.raise_for_status()
            return ET.fromstring(resp.content)  # noqa: S314 - trusted ECB response
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    raise requests.RequestException(f"failed after {retries} attempts: {url}")


def _en(elem: ET.Element | None, tag: str) -> str:
    """Return the English (or first) text of the ``com:`` child ``tag``."""
    if elem is None:
        return ""
    found = None
    for child in elem.findall(f"com:{tag}", _NS):
        found = child
        if child.get(_XML_LANG) == "en":
            break
    return (found.text or "").strip() if found is not None else ""


def _structures(root: ET.Element | None) -> ET.Element | None:
    """Return the ``mes:Structures`` element of a structure message."""
    if root is None:
        return None
    return root.find("mes:Structures", _NS)


def fetch_dataflows() -> dict[str, dict]:
    """Return dataflows keyed by id, each with its DSD reference."""
    print("[1/6] Fetching dataflows...", flush=True)
    structures = _structures(
        _get(f"{BASE_URL}/dataflow/{AGENCY}?detail=full&references=none")
    )
    out: dict[str, dict] = {}
    if structures is None:
        return out
    for df in structures.findall(".//str:Dataflow", _NS):
        df_id = df.get("id")
        if not df_id:
            continue
        ref = df.find("str:Structure/Ref", _NS)
        out[df_id] = {
            "id": df_id,
            "agencyID": df.get("agencyID", AGENCY),
            "version": df.get("version", ""),
            "name": _en(df, "Name"),
            "description": _en(df, "Description"),
            "dsd_id": ref.get("id") if ref is not None else None,
            "dsd_agency": ref.get("agencyID") if ref is not None else AGENCY,
            "dsd_version": ref.get("version") if ref is not None else None,
        }
    print(f"      {len(out)} dataflows", flush=True)
    return out


def _component(comp: ET.Element) -> dict:
    """Translate a Dimension/Attribute element into the cached shape."""
    concept = comp.find("str:ConceptIdentity/Ref", _NS)
    codelist = comp.find("str:LocalRepresentation/str:Enumeration/Ref", _NS)
    entry: dict = {
        "id": comp.get("id"),
        "concept_id": concept.get("id") if concept is not None else None,
        "codelist_id": codelist.get("id") if codelist is not None else None,
    }
    if comp.get("position"):
        entry["position"] = int(comp.get("position"))
    return entry


def fetch_datastructures() -> dict[str, dict]:
    """Return DSDs keyed by id (dimensions, time dimension, attributes)."""
    print("[2/6] Fetching data structures...", flush=True)
    structures = _structures(
        _get(f"{BASE_URL}/datastructure/{AGENCY}?detail=full&references=none")
    )
    out: dict[str, dict] = {}
    if structures is None:
        return out
    for dsd in structures.findall(".//str:DataStructure", _NS):
        dsd_id = dsd.get("id")
        if not dsd_id:
            continue
        dims = [
            _component(d)
            for d in dsd.findall(
                "str:DataStructureComponents/str:DimensionList/str:Dimension", _NS
            )
        ]
        dims.sort(key=lambda d: d.get("position", 999))
        time_dim = dsd.find(
            "str:DataStructureComponents/str:DimensionList/str:TimeDimension", _NS
        )
        attrs = [
            _component(a)
            for a in dsd.findall(
                "str:DataStructureComponents/str:AttributeList/str:Attribute", _NS
            )
        ]
        out[dsd_id] = {
            "id": dsd_id,
            "agencyID": dsd.get("agencyID", AGENCY),
            "version": dsd.get("version", ""),
            "dimensions": dims,
            "time_dimension": (
                {"id": time_dim.get("id")} if time_dim is not None else None
            ),
            "attributes": attrs,
        }
    print(f"      {len(out)} data structures", flush=True)
    return out


def fetch_codelists() -> dict[str, dict]:
    """Return ``{codelist_id: {code_id: label}}`` for every ECB codelist."""
    print("[3/6] Fetching codelists (~35 MB, please wait)...", flush=True)
    structures = _structures(_get(f"{BASE_URL}/codelist/{AGENCY}?detail=full"))
    out: dict[str, dict] = {}
    if structures is None:
        return out
    for cl in structures.findall(".//str:Codelist", _NS):
        cl_id = cl.get("id")
        if not cl_id:
            continue
        codes: dict[str, str] = {}
        for code in cl.findall("str:Code", _NS):
            code_id = code.get("id")
            if code_id:
                codes[code_id] = _en(code, "Name") or code_id
        out[cl_id] = codes
    total = sum(len(v) for v in out.values())
    print(f"      {len(out)} codelists, {total} codes", flush=True)
    return out


def fetch_concepts() -> dict[str, str]:
    """Return ``{concept_id: name}`` for the ECB concept scheme(s)."""
    print("[4/6] Fetching concept schemes...", flush=True)
    structures = _structures(_get(f"{BASE_URL}/conceptscheme/{AGENCY}?detail=full"))
    out: dict[str, str] = {}
    if structures is None:
        return out
    for concept in structures.findall(".//str:Concept", _NS):
        c_id = concept.get("id")
        if c_id and c_id not in out:
            out[c_id] = _en(concept, "Name") or c_id
    print(f"      {len(out)} concepts", flush=True)
    return out


def _walk_categories(parent: ET.Element, out: dict[str, dict]) -> None:
    """Flatten nested ``str:Category`` elements into ``out``."""
    for cat in parent.findall("str:Category", _NS):
        cat_id = cat.get("id")
        if cat_id:
            out[cat_id] = {
                "name": _en(cat, "Name"),
                "description": _en(cat, "Description"),
            }
        _walk_categories(cat, out)


def fetch_categories() -> tuple[dict[str, dict], dict[str, list], dict[str, list]]:
    """Return ``(categories, dataflow->categories, category->dataflows)``."""
    print("[5/6] Fetching category scheme...", flush=True)
    categories: dict[str, dict] = {}
    structures = _structures(
        _get(f"{BASE_URL}/categoryscheme/{AGENCY}?detail=full&references=none")
    )
    if structures is not None:
        for scheme in structures.findall(".//str:CategoryScheme", _NS):
            _walk_categories(scheme, categories)

    print("[6/6] Fetching categorisations...", flush=True)
    df_to_cat: dict[str, list] = {}
    cat_to_df: dict[str, list] = {}
    structures = _structures(_get(f"{BASE_URL}/categorisation/{AGENCY}"))
    if structures is not None:
        for c in structures.findall(".//str:Categorisation", _NS):
            source = c.find("str:Source/Ref", _NS)
            target = c.find("str:Target/Ref", _NS)
            if source is None or target is None:
                continue
            if (source.get("class") or "").lower() != "dataflow":
                continue
            flow_id = source.get("id")
            cat_id = target.get("id")
            if not flow_id or not cat_id:
                continue
            df_to_cat.setdefault(flow_id, [])
            if cat_id not in df_to_cat[flow_id]:
                df_to_cat[flow_id].append(cat_id)
            cat_to_df.setdefault(cat_id, [])
            if flow_id not in cat_to_df[cat_id]:
                cat_to_df[cat_id].append(flow_id)
    print(
        f"      {len(categories)} categories, {len(df_to_cat)} dataflows categorised",
        flush=True,
    )
    return categories, df_to_cat, cat_to_df


def _parse_hierarchical_code(hcode: ET.Element) -> dict:
    """Parse a ``HierarchicalCode`` node (with its children) into the cached shape."""
    ref = hcode.find("str:Code/Ref", _NS)
    return {
        "code": ref.get("id") if ref is not None else None,
        "codelist_id": ref.get("maintainableParentID") if ref is not None else None,
        "agency": ref.get("agencyID") if ref is not None else None,
        "children": [
            _parse_hierarchical_code(child)
            for child in hcode.findall("str:HierarchicalCode", _NS)
        ],
    }


def fetch_presentation_tables() -> tuple[dict[str, dict], dict[str, str]]:
    """Return ``(presentation_tables, row_labels)`` from the ECB.DISS HCLs."""
    print("[7/7] Fetching presentation tables...", flush=True)
    structures = _structures(
        _get(f"{BASE_URL}/hierarchicalcodelist/{HCL_AGENCY}?references=all")
    )
    tables: dict[str, dict] = {}
    row_labels: dict[str, str] = {}
    if structures is None:
        return tables, row_labels
    for cl in structures.findall(".//str:Codelist", _NS):
        if cl.get("id") != "JDF_ROW_LABELS":
            continue
        for code in cl.findall("str:Code", _NS):
            code_id = code.get("id")
            if code_id:
                row_labels[code_id] = _en(code, "Name") or code_id
    for hcl in structures.findall(".//str:HierarchicalCodelist", _NS):
        hid = hcl.get("id")
        if not hid or "@HCL_" not in hid:
            continue
        hierarchy = hcl.find("str:Hierarchy", _NS)
        tree = (
            [
                _parse_hierarchical_code(hc)
                for hc in hierarchy.findall("str:HierarchicalCode", _NS)
            ]
            if hierarchy is not None
            else []
        )
        tables[hid] = {
            "id": hid,
            "name": _en(hcl, "Name"),
            "dataflow_id": hid.split("@HCL_")[-1],
            "tree": tree,
        }
    print(
        f"      {len(tables)} presentation tables, {len(row_labels)} row labels",
        flush=True,
    )
    return tables, row_labels


def fetch_content_constraints() -> dict[str, dict[str, list[str]]]:
    """Return ``{dataflow_id: {dim_id: [allowed_code, ...]}}`` from constraints.

    A dataflow's content constraint (a CubeRegion of allowed key values) is the
    source of truth for which codes are actually valid per dimension — the
    shared codelists (e.g. CL_AREA's ~900 areas) are far broader than any single
    dataflow permits.
    """
    print("[8/8] Fetching content constraints...", flush=True)
    structures = _structures(_get(f"{BASE_URL}/contentconstraint/{AGENCY}"))
    out: dict[str, dict[str, list[str]]] = {}
    if structures is None:
        return out
    for constraint in structures.findall(".//str:ContentConstraint", _NS):
        cube = constraint.find("str:CubeRegion", _NS)
        if cube is None or cube.get("include") == "false":
            continue
        flow_ids = [
            ref.get("id")
            for ref in constraint.findall(
                "str:ConstraintAttachment/str:Dataflow/Ref", _NS
            )
            if ref.get("id")
        ]
        if not flow_ids:
            continue
        dim_codes: dict[str, list[str]] = {}
        for key_value in cube.findall("com:KeyValue", _NS):
            dim_id = key_value.get("id")
            values = [v.text for v in key_value.findall("com:Value", _NS) if v.text]
            if dim_id and values:
                dim_codes[dim_id] = values
        if not dim_codes:
            continue
        for flow_id in flow_ids:
            out[flow_id] = dim_codes
    print(f"      {len(out)} dataflows with content constraints", flush=True)
    return out


def _serieskeysonly_records(dataflow_id: str, key: str) -> list[dict]:
    """Return ``[{dim_id: code}]`` for every existing series under ``key``."""
    url = f"{BASE_URL}/data/{dataflow_id}/{key}?detail=serieskeysonly&format=jsondata"
    try:
        resp = requests.get(
            url,
            headers={"Accept": "application/json", "User-Agent": "openbb-ecb build"},
            timeout=240,
        )
    except requests.RequestException:
        return []
    if resp.status_code != 200:
        return []
    try:
        message = resp.json()
    except ValueError:
        return []
    datasets = message.get("dataSets") or []
    if not datasets:
        return []
    series_dims = message.get("structure", {}).get("dimensions", {}).get("series", [])
    records: list[dict] = []
    for series_key in datasets[0].get("series", {}):
        record: dict = {}
        for pos, raw_idx in enumerate(series_key.split(":")):
            if pos >= len(series_dims):
                break
            values = series_dims[pos].get("values", [])
            idx = int(raw_idx)
            if 0 <= idx < len(values):
                record[series_dims[pos].get("id")] = values[idx].get("id")
        records.append(record)
    return records


def _context_score(combo: tuple, ctx_dims: list[str]) -> int:
    """Score a context slice — prefer euro-area, monthly, unadjusted defaults."""
    score = 0
    for dim, value in zip(ctx_dims, combo):
        if value is None:
            continue
        if dim.endswith("AREA") and value in ("U2", "I8", "I9", "EA"):
            score += 10
        if dim == "FREQ":
            score += {"M": 5, "Q": 3, "A": 1}.get(value, 0)
        if dim == "ADJUSTMENT" and value in ("N", "NSA"):
            score += 1
    return score


def _derive_table_context(table: dict, dsd_dims: list[dict]) -> tuple[dict, dict]:
    """Return ``(valid_context, default_context)`` from a table's real series.

    Classifies each hierarchy dimension by how many leaf rows pin it:
      * *row* dims (every leaf) define the rows;
      * *partial* dims (some leaves) need an aggregate for the rows that don't
        pin them (e.g. a balance-sheet item with no maturity breakdown takes the
        total maturity).
    The non-hierarchy *context* dims are the user-selectable slice; their valid
    values and a best default come from the slices that cover the most rows
    (which drops incidental single-row series — e.g. spot FX under an HCI table).
    The default also pins each partial dim to the value covering the most rows.
    """
    dims_order = [d.get("id") for d in dsd_dims]
    codelist_to_dim = {
        d.get("codelist_id"): d.get("id") for d in dsd_dims if d.get("codelist_id")
    }
    hierarchy: dict[str, set] = {}
    leaves: list[dict] = []

    def walk(nodes: list[dict], path: dict) -> None:
        for node in nodes:
            local = dict(path)
            dim = codelist_to_dim.get(node.get("codelist_id"))
            code = node.get("code")
            if dim and code:
                hierarchy.setdefault(dim, set()).add(code)
                local[dim] = code
            children = node.get("children", [])
            if not children and local:
                leaves.append(local)
            walk(children, local)

    walk(table.get("tree", []), {})
    if not hierarchy or not leaves:
        return {}, {}
    leaf_fixes: dict[str, int] = {}
    for leaf in leaves:
        for fixed in leaf:
            leaf_fixes[fixed] = leaf_fixes.get(fixed, 0) + 1
    row_dims = {d for d in hierarchy if leaf_fixes.get(d) == len(leaves)}
    ctx_dims = [d for d in dims_order if d not in hierarchy]
    # Fetch the series for the row items with the partial/context dimensions left
    # open, so a partial dim's aggregate value (e.g. the total maturity that the
    # un-broken-down rows use, which is not among the hierarchy's maturity codes)
    # is included. Fall back to the full hierarchy when there is no row dim.
    fetch_dims = row_dims or set(hierarchy)
    key = ".".join(
        "+".join(sorted(hierarchy[d])) if d in fetch_dims else "" for d in dims_order
    )
    records = _serieskeysonly_records(table["dataflow_id"], key)
    if not records:
        return {}, {}
    series_set = {tuple(r.get(d) for d in dims_order) for r in records}

    def _filled(candidate: dict) -> int:
        """How many leaf rows resolve to a real series under this full slice."""
        return sum(
            tuple(leaf.get(d, candidate.get(d)) for d in dims_order) in series_set
            for leaf in leaves
        )

    non_row = [d for d in dims_order if d not in row_dims]
    pools = {
        d: sorted({r.get(d) for r in records if r.get(d) is not None}) for d in non_row
    }
    # Seed from the single existing series that already fills the most rows, then
    # coordinate-ascend each non-row dimension independently — the optimal slice
    # combines values (e.g. the *total* maturity for un-broken-down rows) that may
    # not co-occur in any single series.
    seed = max(
        records,
        key=lambda r: (
            _filled(r),
            _context_score(tuple(r.get(d) for d in ctx_dims), ctx_dims),
        ),
    )
    candidate = {d: seed.get(d) for d in dims_order}
    for _ in range(3):  # three coordinate-ascent passes converge in practice
        for d in non_row:
            best_value, best_value_rank = candidate.get(d), (-1, -1)
            for value in pools[d]:
                candidate[d] = value
                rank = (_filled(candidate), _context_score((value,), (d,)))
                if rank > best_value_rank:
                    best_value_rank, best_value = rank, value
            candidate[d] = best_value
    best_fill = _filled(candidate)
    default = {
        d: candidate[d]
        for d in dims_order
        if d not in row_dims and candidate.get(d) is not None
    }
    # Valid slice values = the values a user can swap into each context dimension
    # and still get data (filling a meaningful share of rows).
    threshold = max(1, best_fill // 3)
    valid: dict[str, list] = {}
    for d in ctx_dims:
        valid[d] = [
            value for value in pools[d] if _filled({**candidate, d: value}) >= threshold
        ]
    return valid, default


def fetch_jdf_constraints(presentation_tables: dict) -> dict[str, dict[str, list[str]]]:
    """Return ``{table_id: {dim_id: [values]}}`` from the per-table content
    constraints (agency ``ECB.DISS``).

    Each presentation table has its own content constraint whose ``DataKeySet``
    enumerates the exact series the table publishes — so the values pinned per
    dimension are the *authoritative* slice (e.g. the PSS measure: ``NT`` number
    vs ``VT`` value vs ``NP`` share), which a data-fill heuristic cannot tell
    apart for tables that share a row hierarchy.
    """
    print("[9/10] Fetching JDF table constraints...", flush=True)
    core_to_table = {
        tid.split("@", 1)[0][len("HCL_") :]: tid
        for tid in presentation_tables
        if tid.split("@", 1)[0].startswith("HCL_")
    }
    structures = _structures(_get(f"{BASE_URL}/contentconstraint/{HCL_AGENCY}"))
    out: dict[str, dict[str, set]] = {}
    if structures is not None:
        for cc in structures.findall(".//str:ContentConstraint", _NS):
            ref = cc.find(".//str:ConstraintAttachment/str:Dataflow/Ref", _NS)
            table_id = core_to_table.get(ref.get("id")) if ref is not None else None
            if not table_id:
                continue
            dims = out.setdefault(table_id, {})
            for kv in cc.iter():
                if kv.tag.endswith("}KeyValue") and kv.get("id"):
                    for value in kv:
                        if value.tag.endswith("}Value") and value.text:
                            dims.setdefault(kv.get("id"), set()).add(value.text)
    result = {t: {d: sorted(v) for d, v in dims.items()} for t, dims in out.items()}
    print(f"      {len(result)} tables with a content constraint", flush=True)
    return result


def _tree_dims(table: dict, dsd_dims: list[dict]) -> set[str]:
    """Return the DSD dimensions that appear in a table's row hierarchy."""
    codelist_to_dim = {
        d.get("codelist_id"): d.get("id") for d in dsd_dims if d.get("codelist_id")
    }
    found: set[str] = set()

    def walk(nodes: list[dict]) -> None:
        for node in nodes:
            dim = codelist_to_dim.get(node.get("codelist_id"))
            if dim:
                found.add(dim)
            walk(node.get("children", []))

    walk(table.get("tree", []))
    return found


def fetch_table_contexts(
    presentation_tables: dict, dataflows: dict, datastructures: dict
) -> int:
    """Derive and attach ``valid_context``/``default_context`` to each table.

    The fill heuristic resolves the row/aggregate dimensions; the per-table
    content constraint then overrides the non-row (context) dimensions with the
    exact values the table pins — the authoritative source of truth.
    """
    constraints = fetch_jdf_constraints(presentation_tables)
    print("[10/10] Deriving presentation-table contexts...", flush=True)
    derived = 0
    for table in presentation_tables.values():
        dataflow = dataflows.get(table.get("dataflow_id"))
        if not dataflow:
            continue
        dsd = datastructures.get(dataflow.get("dsd_id"))
        if not dsd:
            continue
        dsd_dims = dsd.get("dimensions", [])
        valid, default = _derive_table_context(table, dsd_dims)
        if not valid:
            continue
        constraint = constraints.get(table.get("id"))
        if constraint:
            tree_dims = _tree_dims(table, dsd_dims)
            for dim, values in constraint.items():
                if dim in tree_dims or not values:
                    continue
                valid[dim] = values
                if default.get(dim) not in values:
                    default[dim] = values[0]
        table["valid_context"] = valid
        table["default_context"] = default
        derived += 1
    print(f"      {derived} tables with derived context", flush=True)
    return derived


def main() -> None:
    """Generate ``ecb_cache.json.xz`` and write it to ``ASSETS_DIR``."""
    t0 = time.time()
    print("Generating ECB SDMX 2.1 cache...", flush=True)

    dataflows = fetch_dataflows()
    datastructures = fetch_datastructures()
    codelists = fetch_codelists()
    concepts = fetch_concepts()
    categories, df_to_cat, cat_to_df = fetch_categories()
    presentation_tables, row_labels = fetch_presentation_tables()
    dataflow_constraints = fetch_content_constraints()
    fetch_table_contexts(presentation_tables, dataflows, datastructures)

    blob = {
        "dataflows": dataflows,
        "datastructures": datastructures,
        "codelists": codelists,
        "concepts": concepts,
        "categories": categories,
        "dataflow_categories": df_to_cat,
        "category_dataflows": cat_to_df,
        "presentation_tables": presentation_tables,
        "row_labels": row_labels,
        "dataflow_constraints": dataflow_constraints,
        "dataflow_parameters": {},
    }

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print("Compressing and writing cache...", flush=True)
    payload = json.dumps(blob, separators=(",", ":")).encode("utf-8")
    with lzma.open(CACHE_FILE, "wb", format=lzma.FORMAT_XZ, preset=6) as fh:
        fh.write(payload)

    size_mb = CACHE_FILE.stat().st_size / (1024 * 1024)
    print(
        f"Wrote {CACHE_FILE} "
        f"({size_mb:.1f} MB compressed, {len(payload) / (1024 * 1024):.1f} MB JSON) "
        f"in {time.time() - t0:.0f}s — "
        f"{len(dataflows)} dataflows, {len(datastructures)} DSDs, "
        f"{len(codelists)} codelists, {len(concepts)} concepts, "
        f"{len(categories)} categories, "
        f"{len(presentation_tables)} presentation tables, "
        f"{len(dataflow_constraints)} constrained dataflows.",
        flush=True,
    )


if __name__ == "__main__":
    sys.exit(main())
