#!/usr/bin/env python
"""Generate the shipped ``imf_cache.json.xz`` baseline cache."""

from __future__ import annotations

import json
import lzma
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CACHE_FILE = ASSETS_DIR / "imf_cache.json.xz"
BASE_URL = "https://api.imf.org/external/sdmx/3.0"

_VINTAGE_RE = re.compile(r"_\d{4}_[A-Z]{3}_VINTAGE$")
_DSD_URN_RE = re.compile(r"DataStructure=([^:]+):([^(]+)\(([^)]+)\)")
_CONCEPT_URN_RE = re.compile(r"Concept=([^:]+):([^(]+)\(([^)]+)\)\.([^)]+)$")
_CODELIST_URN_RE = re.compile(r"Codelist=([^:]+):([^(]+)\(([^)]+)\)")

_session = requests.Session()
_session.headers["Accept"] = "application/json"
_session.headers["User-Agent"] = "openbb-imf build hook"


def _get(url: str, retries: int = 5, backoff: float = 3.0) -> dict:
    """GET ``url`` and return parsed JSON."""
    for attempt in range(retries):
        try:
            resp = _session.get(url, timeout=300)
            if resp.status_code == 429:
                wait = max(15, backoff * (attempt + 1) * 5)
                time.sleep(wait)
                continue
            if resp.status_code in (400, 404):
                return {}
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    raise requests.RequestException(f"failed after {retries} attempts: {url}")


def _normalize_version(version: str) -> str:
    """Strip the SDMX 3 ``+`` wildcard from a version string."""
    return version.replace("+", "")


def _english(d) -> str:
    """Return the English string from an SDMX names/descriptions dict."""
    if not d:
        return ""
    if isinstance(d, str):
        return d
    if isinstance(d, dict):
        val = d.get("en", "") or next(iter(d.values()), "")
        return val if isinstance(val, str) else ""
    return ""


def _parse_structure_ref(struct_urn: str) -> dict:
    """Parse a DataStructure URN into the cached ``structureRef`` dict."""
    m = _DSD_URN_RE.search(struct_urn or "")
    if not m:
        return {}
    return {
        "agencyID": m.group(1),
        "id": m.group(2),
        "version": _normalize_version(m.group(3)),
        "package": "datastructure",
        "class": "DataStructure",
    }


def _parse_concept_ref(concept_urn: str) -> dict:
    """Parse a Concept URN into the cached ``conceptRef`` dict."""
    m = _CONCEPT_URN_RE.search(concept_urn or "")
    if not m:
        return {}
    return {
        "maintainableParentID": m.group(2),
        "maintainableParentVersion": _normalize_version(m.group(3)),
        "agencyID": m.group(1),
        "id": m.group(4),
        "package": "conceptscheme",
        "class": "Concept",
    }


def _parse_presentations(annotations: list) -> list:
    """Extract DATAFLOW_PRESENTATION annotations into structured form."""
    out: list = []
    for ann in annotations or []:
        if ann.get("type") != "DATAFLOW_PRESENTATION":
            continue
        text = ann.get("text") or _english(ann.get("texts"))
        if not text:
            continue
        entry: dict = {}
        for part in text.split(";"):
            if "=" in part:
                key, val = part.split("=", 1)
                key = key.strip()
                val = val.strip()
                if key in ("presentation_title", "presentation_description"):
                    entry[key] = val
        if entry:
            out.append(entry)
    return out


def fetch_dataflows() -> dict[str, dict]:
    """Return dataflows keyed by id, with VINTAGE snapshots filtered out."""
    print("[1/6] Fetching dataflows...", flush=True)
    raw = _get(f"{BASE_URL}/structure/dataflow/*/*/latest?detail=full")
    out: dict[str, dict] = {}
    total = 0
    for df in raw.get("data", {}).get("dataflows", []):
        total += 1
        df_id = df.get("id", "")
        if not df_id or _VINTAGE_RE.search(df_id):
            continue
        agency_id = df.get("agencyID", "")
        version = _normalize_version(df.get("version", ""))
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
            f"{agency_id}:{df_id}({version})"
        )
        out[df_id] = {
            "urn": urn,
            "agencyID": agency_id,
            "id": df_id,
            "version": version,
            "name": df.get("name", "") or _english(df.get("names", {})),
            "description": df.get("description", "")
            or _english(df.get("descriptions", {})),
            "structureRef": _parse_structure_ref(df.get("structure", "")),
            "presentations": _parse_presentations(df.get("annotations", [])),
        }
    print(
        f"      {len(out)} dataflows kept (out of {total}; "
        f"{total - len(out)} VINTAGE snapshots filtered)",
        flush=True,
    )
    return out


def _convert_components(comp_list: list) -> list:
    """Translate SDMX 3 dimension/attribute entries into the cached shape."""
    out: list = []
    for comp in comp_list or []:
        entry: dict = {"id": comp.get("id", "")}
        if "position" in comp:
            entry["position"] = str(comp["position"])
        concept_urn = comp.get("conceptIdentity", "")
        if concept_urn:
            entry["conceptRef"] = _parse_concept_ref(concept_urn)
        out.append(entry)
    return out


def fetch_datastructures() -> dict[str, dict]:
    """Return DSDs keyed by id."""
    print("[2/6] Fetching data structures...", flush=True)
    raw = _get(f"{BASE_URL}/structure/datastructure/*/*/latest?detail=full")
    out: dict[str, dict] = {}
    for ds in raw.get("data", {}).get("dataStructures", []):
        ds_id = ds.get("id", "")
        if not ds_id:
            continue
        agency_id = ds.get("agencyID", "")
        version = _normalize_version(ds.get("version", ""))
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
            f"{agency_id}:{ds_id}({version})"
        )
        components = ds.get("dataStructureComponents", {})
        dim_list = components.get("dimensionList", {}).get("dimensions", [])
        attr_list = components.get("attributeList", {}).get("attributes", [])
        out[ds_id] = {
            "id": ds_id,
            "urn": urn,
            "agencyID": agency_id,
            "version": version,
            "name": ds.get("name", "") or _english(ds.get("names", {})),
            "dimensions": _convert_components(dim_list),
            "attributes": _convert_components(attr_list),
        }
    print(f"      {len(out)} data structures", flush=True)
    return out


def fetch_conceptschemes() -> dict[str, dict]:
    """Return concept schemes keyed by id."""
    print("[3/6] Fetching concept schemes...", flush=True)
    raw = _get(f"{BASE_URL}/structure/conceptscheme/*/*/latest?detail=full")
    out: dict[str, dict] = {}
    for cs in raw.get("data", {}).get("conceptSchemes", []):
        cs_id = cs.get("id", "")
        if not cs_id:
            continue
        agency_id = cs.get("agencyID", "")
        version = _normalize_version(cs.get("version", ""))
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.conceptscheme.ConceptScheme="
            f"{agency_id}:{cs_id}({version})"
        )
        concepts: list = []
        for c in cs.get("concepts", []):
            c_id = c.get("id", "")
            if not c_id:
                continue
            entry: dict = {
                "id": c_id,
                "name": c.get("name", "") or _english(c.get("names", {})),
            }
            enum = (c.get("coreRepresentation") or {}).get("enumeration")
            if isinstance(enum, str):
                m = _CODELIST_URN_RE.search(enum)
                if m:
                    entry["codelist_id"] = m.group(2)
                    entry["codelist_agency"] = m.group(1)
            concepts.append(entry)
        out[cs_id] = {
            "id": cs_id,
            "urn": urn,
            "agencyID": agency_id,
            "version": version,
            "name": cs.get("name", "") or _english(cs.get("names", {})),
            "concepts": concepts,
        }
    print(f"      {len(out)} concept schemes", flush=True)
    return out


def fetch_codelists() -> tuple[dict[str, dict], dict[str, dict]]:
    """Return ``(codelists, descriptions)`` for every codelist."""
    print("[4/6] Fetching codelists...", flush=True)
    raw = _get(f"{BASE_URL}/structure/codelist/*/*/latest?detail=full")
    codes_by_id: dict[str, dict] = {}
    descs_by_id: dict[str, dict] = {}
    for cl in raw.get("data", {}).get("codelists", []):
        cl_id = cl.get("id", "")
        if not cl_id:
            continue
        labels: dict[str, str] = {}
        descs: dict[str, str] = {}
        for code in cl.get("codes", []):
            code_id = code.get("id", "")
            if not code_id:
                continue
            label = _english(code.get("names")) or code.get("name") or code_id
            description = (
                _english(code.get("descriptions")) or code.get("description") or label
            )
            labels[code_id] = label
            descs[code_id] = description
        codes_by_id[cl_id] = labels
        descs_by_id[cl_id] = descs
    print(f"      {len(codes_by_id)} codelists", flush=True)
    return codes_by_id, descs_by_id


def fetch_hierarchies() -> dict[str, dict]:
    """Return hierarchical code lists keyed by id."""
    print("[5/6] Fetching hierarchies...", flush=True)
    raw = _get(f"{BASE_URL}/structure/hierarchy/*/*/latest?detail=full")
    out: dict[str, dict] = {}
    for h in raw.get("data", {}).get("hierarchies", []):
        h_id = h.get("id", "")
        if not h_id:
            continue
        out[h_id] = h
    print(f"      {len(out)} hierarchies", flush=True)
    return out


_CONSTRAINT_CACHE_KEY_TEMPLATE = "{df_id}:all:all:available:all:()"


def _fetch_one_constraint(df_id: str, agency_id: str) -> tuple[str, dict]:
    """Fetch the default constraint payload for a single dataflow."""
    url = (
        f"{BASE_URL}/availability/dataflow/{agency_id}/{df_id}/%2B/all/all"
        "?mode=available&references=all"
    )
    cache_key = _CONSTRAINT_CACHE_KEY_TEMPLATE.format(df_id=df_id)
    try:
        json_response = _get(url)
    except Exception:
        return cache_key, {}
    if not json_response:
        return cache_key, {}

    extracted: dict[str, list] = {}
    data = json_response.get("data", {})
    for constraint in data.get("dataConstraints", []):
        for region in constraint.get("cubeRegions", []):
            for kv in region.get("keyValues", []):
                dim_id = kv.get("id")
                if not dim_id:
                    continue
                extracted.setdefault(dim_id, [])
                for val in kv.get("values", []):
                    if isinstance(val, dict):
                        extracted[dim_id].append(val.get("value"))
                    else:
                        extracted[dim_id].append(val)
            for comp in region.get("components", []):
                dim_id = comp.get("id")
                if not dim_id:
                    continue
                extracted.setdefault(dim_id, [])
                for val in comp.get("values", []):
                    if isinstance(val, dict):
                        extracted[dim_id].append(val.get("value"))
                    else:
                        extracted[dim_id].append(val)
    for dim_id, values in list(extracted.items()):
        extracted[dim_id] = list({v for v in values if v})
    key_values = [{"id": k, "values": v} for k, v in extracted.items()]
    return cache_key, {"key_values": key_values, "full_response": json_response}


def fetch_constraints(dataflows: dict[str, dict]) -> dict[str, dict]:
    """Fetch availability constraints for every dataflow in parallel."""
    print(
        f"[6/6] Fetching availability constraints for {len(dataflows)} "
        "dataflows (parallel)...",
        flush=True,
    )
    out: dict[str, dict] = {}
    failures = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {
            pool.submit(_fetch_one_constraint, df_id, df["agencyID"]): df_id
            for df_id, df in dataflows.items()
        }
        done = 0
        for fut in as_completed(futures):
            df_id = futures[fut]
            done += 1
            try:
                key, payload = fut.result()
            except Exception as exc:
                failures += 1
                print(
                    f"      ! constraint fetch failed for {df_id}: {exc}",
                    flush=True,
                )
                continue
            if payload:
                out[key] = payload
            else:
                failures += 1
            if done % 25 == 0 or done == len(futures):
                print(
                    f"      {done}/{len(futures)} dataflows processed",
                    flush=True,
                )
    print(
        f"      {len(out)} constraint entries cached "
        f"({failures} fetch failures / empty responses)",
        flush=True,
    )
    return out


def derive_dataflow_groups(dataflows: dict[str, dict]) -> dict[str, list]:
    """Group dataflow stubs by agency id."""
    groups: dict[str, list] = {}
    for df in dataflows.values():
        groups.setdefault(df["agencyID"], []).append(
            {
                "urn": df["urn"],
                "agencyID": df["agencyID"],
                "id": df["id"],
                "version": df["version"],
                "name": df["name"],
                "description": df["description"],
            }
        )
    for items in groups.values():
        items.sort(key=lambda d: d["id"])
    return groups


def main() -> None:
    """Generate ``imf_cache.json.xz`` and write it to ``ASSETS_DIR``."""
    t0 = time.time()
    print("Generating IMF SDMX 3.0 cache...", flush=True)

    dataflows = fetch_dataflows()
    datastructures = fetch_datastructures()
    conceptschemes = fetch_conceptschemes()
    codelist_cache, codelist_descriptions = fetch_codelists()
    hierarchies = fetch_hierarchies()
    constraints_cache = fetch_constraints(dataflows)

    dataflow_groups = derive_dataflow_groups(dataflows)

    blob = {
        "dataflows": dataflows,
        "datastructures": datastructures,
        "conceptschemes": conceptschemes,
        "dataflow_groups": dataflow_groups,
        "metadata_cache": {},
        "constraints_cache": constraints_cache,
        "codelist_cache": codelist_cache,
        "codelist_descriptions": codelist_descriptions,
        "dataflow_parameters": {},
        "dataflow_indicators": {},
        "hierarchies": hierarchies,
    }

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print("Compressing and writing cache...", flush=True)
    payload = json.dumps(blob, separators=(",", ":")).encode("utf-8")
    with lzma.open(CACHE_FILE, "wb", format=lzma.FORMAT_XZ, preset=6) as fh:
        fh.write(payload)

    size_mb = CACHE_FILE.stat().st_size / (1024 * 1024)
    elapsed = time.time() - t0
    print(
        f"Wrote {CACHE_FILE} "
        f"({size_mb:.1f} MB compressed, "
        f"{len(payload) / (1024 * 1024):.1f} MB JSON) "
        f"in {elapsed:.0f}s — "
        f"{len(dataflows)} dataflows, "
        f"{len(datastructures)} DSDs, "
        f"{len(codelist_cache)} codelists, "
        f"{len(hierarchies)} hierarchies, "
        f"{len(constraints_cache)} constraint entries.",
        flush=True,
    )


if __name__ == "__main__":
    sys.exit(main())
