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
    """Return DSDs keyed by id."""
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
    """Return ``{concept_id: name}`` for the ECB concept schemes."""
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
    presentation_tables = fetch_presentation_tables()
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
