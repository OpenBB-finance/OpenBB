"""Generate the shipped ``ecb_cache.json.xz`` SDMX metadata baseline."""

from __future__ import annotations

import json
import lzma
import re
import sys
import time
import xml.etree.ElementTree as ET  # noqa: S405
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CACHE_FILE = ASSETS_DIR / "ecb_cache.json.xz"
BASE_URL = "https://data-api.ecb.europa.eu/service"
AGENCY = "ECB"
AGENCIES = ("ECB", "ESTAT", "EUROSTAT", "IMF")
HCL_AGENCY = "ECB.DISS"
ROW_LABEL_CODELIST = "JDF_ROW_LABELS"

PORTAL_URL = "https://data.ecb.europa.eu"
PUBLICATION_CATEGORIES = (
    "macroeconomic-and-sectoral-statistics",
    "money-credit-and-banking",
    "financial-markets-and-interest-rates-0",
    "balance-payments-and-other-external-statistics",
    "ecbeurosystem-policy-and-exchange-rates",
    "payments-statistics",
    "supervisory-banking-statistics",
    "non-bank-financial-corporations",
)
_TABLE_ID_RE = re.compile(r"/data/publications/([A-Za-z0-9_]+)")
_SUBNODE_RE = re.compile(r"/publications/[a-z0-9\-]+/\d+")
_DRUPAL_RE = re.compile(
    r'data-drupal-selector="drupal-settings-json"[^>]*>(.*?)</script>', re.S
)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
_BREADCRUMB_RE = re.compile(r"breadcrumb.*?</(?:nav|ol|ul)>", re.S)
_ANCHOR_RE = re.compile(r"<a[^>]*>(.*?)</a>", re.S)

_DSETINFO_RE = re.compile(
    r'dataset__field-m-dsetinfo-([a-z\-]+)"(.*?)'
    r"(?=dataset__field-m-dsetinfo-|group-data-information-footer|</footer>|\Z)",
    re.S,
)
_FIELD_LABEL_RE = re.compile(r"field__label[^>]*>(.*?)</div>", re.S)
_KEEP_TAG_RE = re.compile(r"</?(?:p|a|ul|ol|li|br|strong|b|em)\b[^>]*>", re.I)
_STRIP_BLOCK_RE = re.compile(r"<(script|button|svg|style)\b.*?</\1>", re.S | re.I)
_ATTR_RE = re.compile(r'\s+(?!href)[a-zA-Z\-]+="[^"]*"')
_DOWNLOAD_RE = re.compile(r'href="/data/datasets/([a-z0-9]+)/download"')
_DATASET_REF_RE = re.compile(r'/data/datasets/([a-z0-9]+)(?:/|")')
_CONCEPT_REF_RE = re.compile(r"/data/concepts/([a-z0-9\-]+)")

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
            return ET.fromstring(resp.content)  # noqa: S314
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    raise requests.RequestException(f"failed after {retries} attempts: {url}")


def _en(elem: ET.Element | None, tag: str) -> str:
    """Return the English text of the ``com:`` child ``tag``."""
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


def _agency_structures(resource: str, query: str) -> list[tuple[str, ET.Element]]:
    """Fetch a structure resource from every hosted agency."""
    result: list[tuple[str, ET.Element]] = []
    for agency in AGENCIES:
        structures = _structures(_get(f"{BASE_URL}/{resource}/{agency}?{query}"))
        if structures is not None:
            result.append((agency, structures))
    return result


def fetch_dataflows() -> dict[str, dict]:
    """Return dataflows keyed by id, each with its DSD reference."""
    print("[1/6] Fetching dataflows...", flush=True)
    out: dict[str, dict] = {}
    for agency, structures in _agency_structures(
        "dataflow", "detail=full&references=none"
    ):
        for df in structures.findall(".//str:Dataflow", _NS):
            df_id = df.get("id")
            if not df_id or df_id in out:
                continue
            ref = df.find("str:Structure/Ref", _NS)
            out[df_id] = {
                "id": df_id,
                "agencyID": df.get("agencyID", agency),
                "version": df.get("version", ""),
                "name": _en(df, "Name"),
                "description": _en(df, "Description"),
                "dsd_id": ref.get("id") if ref is not None else None,
                "dsd_agency": ref.get("agencyID") if ref is not None else agency,
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
    position = comp.get("position")
    if position:
        entry["position"] = int(position)
    return entry


def fetch_datastructures() -> dict[str, dict]:
    """Return DSDs keyed by id."""
    print("[2/6] Fetching data structures...", flush=True)
    out: dict[str, dict] = {}
    for agency, structures in _agency_structures(
        "datastructure", "detail=full&references=none"
    ):
        for dsd in structures.findall(".//str:DataStructure", _NS):
            dsd_id = dsd.get("id")
            if not dsd_id or dsd_id in out:
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
                "agencyID": dsd.get("agencyID", agency),
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
    out: dict[str, dict] = {}
    for _agency, structures in _agency_structures("codelist", "detail=full"):
        for cl in structures.findall(".//str:Codelist", _NS):
            cl_id = cl.get("id")
            if not cl_id:
                continue
            codes: dict[str, str] = {}
            for code in cl.findall("str:Code", _NS):
                code_id = code.get("id")
                if code_id:
                    codes[code_id] = _en(code, "Name") or code_id
            out[cl_id] = {**codes, **out.get(cl_id, {})}
    total = sum(len(v) for v in out.values())
    print(f"      {len(out)} codelists, {total} codes", flush=True)
    return out


def fetch_concepts() -> dict[str, str]:
    """Return ``{concept_id: name}`` for the ECB concept schemes."""
    print("[4/6] Fetching concept schemes...", flush=True)
    out: dict[str, str] = {}
    for _agency, structures in _agency_structures("conceptscheme", "detail=full"):
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


def _get_text(url: str, retries: int = 6, backoff: float = 2.0) -> str:
    """GET ``url`` and return the decoded body, or ``""`` on a non-200/error."""
    for attempt in range(retries):
        try:
            resp = _session.get(url, headers={"Accept": "text/html"}, timeout=120)
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(max(5, backoff * (attempt + 1)))
                continue
            if resp.status_code != 200:
                return ""
            return resp.text
        except requests.RequestException:
            if attempt == retries - 1:
                return ""
            time.sleep(backoff * (attempt + 1))
    return ""


def _clean_html(fragment: str) -> str:
    """Strip tags and collapse whitespace from an HTML fragment."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def _crawl_publication_tree() -> set[str]:
    """Return every ``/data/publications`` table id under the category trees."""
    seen: set[str] = set()
    frontier = [f"/publications/{c}" for c in PUBLICATION_CATEGORIES]
    table_ids: set[str] = set()
    with ThreadPoolExecutor(max_workers=6) as pool:
        while frontier:
            batch = [p for p in frontier if p not in seen]
            seen.update(batch)
            next_frontier: set[str] = set()
            for html in pool.map(lambda p: _get_text(PORTAL_URL + p), batch):
                if not html:
                    continue
                table_ids.update(_TABLE_ID_RE.findall(html))
                next_frontier.update(
                    sub for sub in _SUBNODE_RE.findall(html) if sub not in seen
                )
            frontier = sorted(next_frontier)
    return table_ids


def _parse_publication_table(table_id: str) -> dict | None:
    """Return the cached record for one ``/data/publications/<ID>`` table, or None."""
    html = _get_text(f"{PORTAL_URL}/data/publications/{table_id}")
    if not html:
        return None
    settings_match = _DRUPAL_RE.search(html)
    if not settings_match:
        return None
    try:
        settings = json.loads(settings_match.group(1))
    except ValueError:
        return None
    series_keys = (settings.get("async_series_obs") or {}).get("series_keys") or {}
    rows: list[dict] = []
    seen_keys: set[str] = set()
    for obj in series_keys.values():
        serieskey = obj.get("serieskey") if isinstance(obj, dict) else None
        if not serieskey or serieskey in seen_keys:
            continue
        seen_keys.add(serieskey)
        flow, _, key = serieskey.partition(".")
        if flow and key:
            rows.append({"flow": flow, "key": key})
    if not rows:
        return None
    title_match = _TITLE_RE.search(html)
    title = (
        _clean_html(title_match.group(1)).split(" | ")[0].strip()
        if title_match
        else table_id
    )
    crumbs: list[str] = []
    crumb_match = _BREADCRUMB_RE.search(html)
    if crumb_match:
        crumbs = [
            c
            for c in (_clean_html(a) for a in _ANCHOR_RE.findall(crumb_match.group(0)))
            if c
        ]
    meaningful = [c for c in crumbs if c not in ("Home", "Publications", "Browse data")]
    return {
        "id": table_id,
        "title": title,
        "category": meaningful[0] if meaningful else "",
        "subcategory": meaningful[-1] if len(meaningful) > 1 else "",
        "breadcrumb": crumbs,
        "rows": rows,
        "source": "publications",
    }


def fetch_presentation_tables() -> dict[str, dict]:
    """Return the ECB data-portal presentation tables keyed by id."""
    print("[7/7] Crawling ECB data-portal publication tables...", flush=True)
    table_ids = _crawl_publication_tree()
    print(f"      {len(table_ids)} candidate tables discovered", flush=True)
    tables: dict[str, dict] = {}
    pending = sorted(table_ids)
    for _ in range(3):
        if not pending:
            break
        with ThreadPoolExecutor(max_workers=6) as pool:
            for record in pool.map(_parse_publication_table, pending):
                if record:
                    tables[record["id"]] = record
        pending = [tid for tid in pending if tid not in tables]
    total_rows = sum(len(t["rows"]) for t in tables.values())
    print(
        f"      {len(tables)} publication tables, {total_rows} series rows",
        flush=True,
    )
    return tables


def _table_has_data(table: dict) -> bool:
    """Return whether any of a publication table's series carries a value."""
    import csv
    from io import StringIO

    by_flow: dict[str, list[str]] = {}
    for row in table.get("rows") or []:
        by_flow.setdefault(row["flow"], []).append(row["key"])
    for flow, keys in by_flow.items():
        for start in range(0, len(keys), 25):
            batch = keys[start : start + 25]
            positions: list[set] = []
            for key in batch:
                for pos, part in enumerate(key.split(".")):
                    if pos >= len(positions):
                        positions.append(set())
                    positions[pos].add(part)
            or_key = ".".join("+".join(sorted(p)) for p in positions)
            url = (
                f"{BASE_URL}/data/{flow}/{or_key}"
                "?format=csvdata&detail=dataonly&lastNObservations=1"
            )
            try:
                resp = _session.get(url, headers={"Accept": "text/csv"}, timeout=120)
            except requests.RequestException:
                return True
            if resp.status_code == 429 or resp.status_code >= 500:
                return True
            if resp.status_code != 200:
                continue
            wanted = {f"{flow}.{key}" for key in batch}
            for record in csv.DictReader(StringIO(resp.text)):
                value = (record.get("OBS_VALUE") or "").strip()
                if record.get("KEY") in wanted and value:
                    return True
    return False


def prune_dead_tables(tables: dict) -> None:
    """Drop publication tables whose series return no data."""
    print("      pruning dead publication tables...", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        alive = dict(zip(tables, pool.map(_table_has_data, tables.values())))
    for tid in [t for t, ok in alive.items() if not ok]:
        del tables[tid]
        print(f"      dropped dead {tid}", flush=True)


def _parse_hierarchical_code(hcode: ET.Element) -> dict:
    """Parse a ``HierarchicalCode`` node into the cached tree shape."""
    ref = hcode.find("str:Code/Ref", _NS)
    return {
        "code": ref.get("id") if ref is not None else None,
        "codelist_id": ref.get("maintainableParentID") if ref is not None else None,
        "children": [
            _parse_hierarchical_code(child)
            for child in hcode.findall("str:HierarchicalCode", _NS)
        ],
    }


def fetch_jdf_tables() -> tuple[dict[str, dict], dict[str, str]]:
    """Return ``(jdf_tables, row_labels)`` from the ECB.DISS hierarchical code lists."""
    print("[JDF] Fetching hierarchical presentation tables...", flush=True)
    structures = _structures(
        _get(f"{BASE_URL}/hierarchicalcodelist/{HCL_AGENCY}?references=all")
    )
    tables: dict[str, dict] = {}
    row_labels: dict[str, str] = {}
    if structures is None:
        return tables, row_labels
    for cl in structures.findall(".//str:Codelist", _NS):
        if cl.get("id") != ROW_LABEL_CODELIST:
            continue
        for code in cl.findall("str:Code", _NS):
            code_id = code.get("id")
            if code_id:
                row_labels[code_id] = _en(code, "Name") or code_id
    for hcl in structures.findall(".//str:HierarchicalCodelist", _NS):
        hid = hcl.get("id")
        if not hid or "@HCL_" not in hid or not hid.startswith("HCL_JDF_"):
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
            "source": "jdf",
        }
    print(f"      {len(tables)} JDF tables, {len(row_labels)} row labels", flush=True)
    return tables, row_labels


def _serieskeysonly_records(dataflow_id: str, key: str) -> list[dict]:
    """Return ``[{dim_id: code}]`` for every existing series under ``key``."""
    url = f"{BASE_URL}/data/{dataflow_id}/{key}?detail=serieskeysonly&format=jsondata"
    try:
        resp = _session.get(url, headers={"Accept": "application/json"}, timeout=240)
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
    """Score a context slice preferring euro-area, monthly, unadjusted values."""
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


def _table_series(
    table: dict,
    dims_order: list[str],
    hierarchy: dict[str, set],
    fetch_dims: set,
    allowed: dict | None,
) -> list[dict]:
    """Return the existing series records for a table's hierarchy codes."""
    key = ".".join(
        "+".join(sorted(hierarchy[d])) if d in fetch_dims else "" for d in dims_order
    )
    records = _serieskeysonly_records(table["dataflow_id"], key)
    if allowed:
        constrained = [
            r
            for r in records
            if all(
                r.get(dim) is None or r.get(dim) in values
                for dim, values in allowed.items()
            )
        ]
        records = constrained or records
    return records


def _resolve_leaf_keys(
    table: dict, dsd_dims: list[dict], records: list[dict], candidate: dict
) -> list:
    """Resolve each hierarchy node to the series key best matching the context."""
    dims_order = [dim_id for d in dsd_dims if (dim_id := d.get("id"))]
    codelist_to_dim = {
        d.get("codelist_id"): d.get("id") for d in dsd_dims if d.get("codelist_id")
    }
    keys: list = []

    def walk(nodes: list[dict], path: dict) -> None:
        for node in nodes:
            local = dict(path)
            dim = codelist_to_dim.get(node.get("codelist_id"))
            code = node.get("code")
            if dim and code:
                local[dim] = code
            best, best_rank = None, (-1, -1)
            for record in records if local else []:
                if any(record.get(d) != c for d, c in local.items()):
                    continue
                agreement = sum(
                    1
                    for d in dims_order
                    if candidate.get(d) is not None
                    and record.get(d) == candidate.get(d)
                )
                rank = (
                    agreement,
                    _context_score(
                        tuple(record.get(d) for d in dims_order), dims_order
                    ),
                )
                if rank > best_rank:
                    best_rank, best = rank, record
            keys.append(
                ".".join(best.get(d) or "" for d in dims_order) if best else None
            )
            walk(node.get("children", []), local)

    walk(table.get("tree", []), {})
    return keys


def _derive_table_context(
    table: dict, dsd_dims: list[dict], allowed: dict | None = None
) -> tuple[dict, dict, set, list]:
    """Return ``(valid_context, default_context, row_dims, records)``."""
    dims_order = [dim_id for d in dsd_dims if (dim_id := d.get("id"))]
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
        return {}, {}, set(), []
    leaf_fixes: dict[str, int] = {}
    for leaf in leaves:
        for fixed in leaf:
            leaf_fixes[fixed] = leaf_fixes.get(fixed, 0) + 1
    row_dims = {d for d in hierarchy if leaf_fixes.get(d) == len(leaves)}
    ctx_dims = [d for d in dims_order if d not in hierarchy]
    fetch_dims = row_dims or set(hierarchy)
    records = _table_series(table, dims_order, hierarchy, fetch_dims, allowed)
    if not records:
        return {}, {}, row_dims, []
    series_set = {tuple(r.get(d) for d in dims_order) for r in records}

    def _filled(candidate: dict) -> int:
        return sum(
            tuple(leaf.get(d, candidate.get(d)) for d in dims_order) in series_set
            for leaf in leaves
        )

    non_row = [d for d in dims_order if d not in row_dims]
    pools = {
        d: sorted({r.get(d) for r in records if r.get(d) is not None}) for d in non_row
    }
    seed = max(
        records,
        key=lambda r: (
            _filled(r),
            _context_score(tuple(r.get(d) for d in ctx_dims), ctx_dims),
        ),
    )
    candidate = {d: seed.get(d) for d in dims_order}
    for _ in range(3):
        for d in non_row:
            best_value, best_value_rank = candidate.get(d), (-1, -1)
            for value in pools[d]:
                candidate[d] = value
                rank = (_filled(candidate), _context_score((value,), [d]))
                if rank > best_value_rank:
                    best_value_rank, best_value = rank, value
            candidate[d] = best_value
    best_fill = _filled(candidate)
    default = {
        d: candidate[d]
        for d in dims_order
        if d not in row_dims and candidate.get(d) is not None
    }
    threshold = max(1, best_fill // 3)
    valid: dict[str, list] = {}
    for d in ctx_dims:
        valid[d] = [
            value for value in pools[d] if _filled({**candidate, d: value}) >= threshold
        ]
    return valid, default, row_dims, records


def fetch_jdf_constraints(jdf_tables: dict) -> dict[str, dict[str, list[str]]]:
    """Return ``{table_id: {dim_id: [values]}}`` from ECB.DISS content constraints."""
    core_to_table = {
        tid.split("@", 1)[0][len("HCL_") :]: tid
        for tid in jdf_tables
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
                kv_id = kv.get("id")
                if kv.tag.endswith("}KeyValue") and kv_id:
                    for value in kv:
                        if value.tag.endswith("}Value") and value.text:
                            dims.setdefault(kv_id, set()).add(value.text)
    return {t: {d: sorted(v) for d, v in dims.items()} for t, dims in out.items()}


def _tree_dims(table: dict, dsd_dims: list[dict]) -> set[str]:
    """Return the DSD dimensions appearing in a table's row hierarchy."""
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


def _core_key(table_id: str) -> str:
    """Return the table id core with single-letter segments removed."""
    core = table_id.split("@", 1)[0]
    return "_".join(part for part in core.split("_") if len(part) > 1)


def _drop_superseded(jdf_tables: dict, constraints: dict) -> None:
    """Drop unconstrained JDF tables duplicating a constrained table's core."""
    constrained_cores = {_core_key(tid) for tid in jdf_tables if tid in constraints}
    for tid in [t for t in jdf_tables if t not in constraints]:
        if _core_key(tid) in constrained_cores:
            del jdf_tables[tid]
            print(f"      dropped superseded {tid}", flush=True)


def fetch_table_contexts(
    jdf_tables: dict, dataflows: dict, datastructures: dict
) -> int:
    """Attach ``valid_context`` / ``default_context`` to each JDF table."""
    print("[JDF] Deriving hierarchical-table contexts...", flush=True)
    constraints = fetch_jdf_constraints(jdf_tables)
    _drop_superseded(jdf_tables, constraints)
    derived = 0
    for table in jdf_tables.values():
        dataflow = dataflows.get(table.get("dataflow_id"))
        if not dataflow:
            continue
        dsd = datastructures.get(dataflow.get("dsd_id"))
        if not dsd:
            continue
        dsd_dims = dsd.get("dimensions", [])
        constraint = constraints.get(table.get("id"))
        valid, default, row_dims, records = _derive_table_context(
            table, dsd_dims, constraint
        )
        if not valid:
            continue
        if constraint:
            tree_dims = _tree_dims(table, dsd_dims)
            for dim, values in constraint.items():
                if dim in row_dims or not values:
                    continue
                if dim not in tree_dims:
                    valid[dim] = values
                if default.get(dim) not in values:
                    default[dim] = values[0]
        table["valid_context"] = valid
        table["default_context"] = default
        table["leaf_keys"] = _resolve_leaf_keys(table, dsd_dims, records, default)
        derived += 1
    print(f"      {derived} tables with derived context", flush=True)
    return derived


def fetch_content_constraints() -> dict[str, dict[str, list[str]]]:
    """Return ``{dataflow_id: {dim_id: [allowed_code, ...]}}`` from constraints."""
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
            flow_id
            for ref in constraint.findall(
                "str:ConstraintAttachment/str:Dataflow/Ref", _NS
            )
            if (flow_id := ref.get("id"))
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


def _sanitize_dsetinfo(fragment: str) -> str:
    """Reduce a data-information fragment to safe inline HTML with absolute links."""
    fragment = _STRIP_BLOCK_RE.sub(" ", fragment)
    fragment = fragment.replace('href="/', f'href="{PORTAL_URL}/')
    out: list[str] = []
    for token in re.split(r"(<[^>]+>)", fragment):
        if token.startswith("<"):
            if _KEEP_TAG_RE.match(token):
                out.append(_ATTR_RE.sub("", token))
        else:
            out.append(token)
    text = re.sub(r"<[^>]*$", "", "".join(out))
    return re.sub(r"\s+", " ", text).strip()


def _extract_dataset_info(html: str) -> dict | None:
    """Parse a dataset ``data-information`` page into title + fields, or None."""
    fields: list[dict] = []
    for match in _DSETINFO_RE.finditer(html):
        key, body = match.group(1), match.group(2)
        label_match = _FIELD_LABEL_RE.search(body)
        label = _clean_html(label_match.group(1)) if label_match else key
        content = body[label_match.end() :] if label_match else body
        content = _sanitize_dsetinfo(content)[:4000]
        if content:
            fields.append({"key": key, "label": label, "html": content})
    if not fields:
        return None
    title_match = _TITLE_RE.search(html)
    title = _clean_html(title_match.group(1)).split(" | ")[0] if title_match else ""
    download = _DOWNLOAD_RE.search(html)
    return {
        "title": title,
        "catalogue": (
            f"{PORTAL_URL}/data/datasets/{download.group(1)}/download"
            if download
            else ""
        ),
        "fields": fields,
    }


def fetch_dataflow_info(dataflow_ids: list[str]) -> dict[str, dict]:
    """Return the ``data-information`` metadata for each dataflow that has it."""
    print("[8/10] Fetching dataflow data-information...", flush=True)

    def _one(flow_id: str) -> tuple[str, dict | None]:
        html = _get_text(
            f"{PORTAL_URL}/data/datasets/{flow_id.lower()}/data-information?layerType=KL"
        )
        return flow_id, (_extract_dataset_info(html) if html else None)

    out: dict[str, dict] = {}
    pending = list(dataflow_ids)
    for _ in range(3):
        if not pending:
            break
        with ThreadPoolExecutor(max_workers=6) as pool:
            for flow_id, info in pool.map(_one, pending):
                if info:
                    out[flow_id] = info
        pending = [flow_id for flow_id in pending if flow_id not in out]
    print(f"      {len(out)} dataflows with data-information", flush=True)
    return out


def fetch_portal_concepts(dataflow_ids: set[str]) -> dict[str, dict]:
    """Return the ECB data-portal concepts with their dataset members."""
    print("[9/10] Fetching data-portal concepts...", flush=True)
    index = _get_text(f"{PORTAL_URL}/data/concepts")
    slugs = sorted(set(_CONCEPT_REF_RE.findall(index)))

    def _one(slug: str) -> tuple[str, dict]:
        html = _get_text(
            f"{PORTAL_URL}/data/concepts/{slug}/data-information?layerType=KL"
        )
        title_match = _TITLE_RE.search(html)
        name = (
            _clean_html(title_match.group(1)).split(" | ")[0] if title_match else slug
        )
        datasets = sorted(
            {
                d.upper()
                for d in _DATASET_REF_RE.findall(html)
                if d.upper() in dataflow_ids
            }
        )
        return slug, {"slug": slug, "name": name, "datasets": datasets}

    out: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for slug, record in pool.map(_one, slugs):
            out[slug] = record
    print(f"      {len(out)} concepts", flush=True)
    return out


def main() -> None:
    """Generate ``ecb_cache.json.xz`` and write it to ``ASSETS_DIR``."""
    t0 = time.time()
    print("Generating ECB SDMX 2.1 cache...", flush=True)

    dataflows = fetch_dataflows()
    datastructures = fetch_datastructures()
    codelists = fetch_codelists()
    concepts = fetch_concepts()
    categories, df_to_cat, cat_to_df = fetch_categories()
    publications = fetch_presentation_tables()
    prune_dead_tables(publications)
    jdf_tables, row_labels = fetch_jdf_tables()
    fetch_table_contexts(jdf_tables, dataflows, datastructures)
    presentation_tables = {**publications, **jdf_tables}
    dataflow_constraints = fetch_content_constraints()
    dataflow_info = fetch_dataflow_info(list(dataflows))
    portal_concepts = fetch_portal_concepts(set(dataflows))

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
        "dataflow_info": dataflow_info,
        "portal_concepts": portal_concepts,
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
        f"{len(dataflow_constraints)} constrained dataflows, "
        f"{len(dataflow_info)} data-information sheets, "
        f"{len(portal_concepts)} concepts.",
        flush=True,
    )


if __name__ == "__main__":
    sys.exit(main())
