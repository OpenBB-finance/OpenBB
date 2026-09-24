#!/usr/bin/env python
"""Generate the shipped ``government_ca_cache.json.xz`` catalog.

Self-contained build-time script for the Statistics Canada (StatsCan) SDMX
catalog. It uses **only** the Python standard library plus ``requests`` and
MUST NOT import ``openbb_core``, so the Hatchling build hook can invoke it by
path inside the isolated PEP 517 build environment.

StatsCan implements a narrow SDMX subset: there is no dataflow-listing, no
standalone codelist, and no availability endpoint (all 404). Everything is
fetched per-PID from ``GET .../rest/structure/Data_Structure_{pid}``, which
returns one bilingual SDMX-ML ``Structure_Message``.

The curated PID set is seeded from ``ind-econ.json``
(``results.indicators[].source``); the full StatsCan population is never
crawled.
"""

from __future__ import annotations

import json
import lzma
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

BASE_URL = "https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest"
IND_ECON_URL = "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
STRUCTURE_ACCEPT = "application/vnd.sdmx.structure+xml;version=2.1"
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
CACHE_FILE = ASSETS_DIR / "government_ca_cache.json.xz"
REQUEST_TIMEOUT = 30  # seconds, per request
MAX_ATTEMPTS = 5  # retries with exponential backoff
MAX_CACHE_BYTES = 1_048_576  # 1 MiB ceiling

# SDMX-ML v2.1 namespaces used by the StatsCan structure messages.
_NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class StructureParseError(Exception):
    """Raised when a Structure_Message body is malformed or unexpected.

    A plain ``Exception`` subclass (no ``openbb_core`` dependency) so the
    build-time generator stays self-contained; ``build_catalog`` catches it to
    skip the offending PID.
    """


def derive_pids(ind_econ: dict) -> list[str]:
    """Derive the curated PID set from an ``ind-econ.json`` payload.

    Parameters
    ----------
    ind_econ : dict
        The parsed ``ind-econ.json`` payload.

    Returns
    -------
    list[str]
        The ``results.indicators[].source`` values kept only when they are
        exactly 8 numeric digits, deduplicated while preserving first-seen
        order.
    """
    indicators = ind_econ.get("results", {}).get("indicators", [])
    pids: list[str] = []
    seen: set[str] = set()
    for indicator in indicators:
        pid = str(indicator.get("source", ""))
        if len(pid) == 8 and pid.isdigit() and pid not in seen:
            seen.add(pid)
            pids.append(pid)
    return pids


def _request_with_retries(
    session: requests.Session,
    url: str,
    accept: str,
    label: str,
) -> requests.Response:
    """GET ``url`` retrying transient failures with exponential backoff.

    Connection errors, timeouts, and HTTP status codes >= 400 are treated as
    transient and retried up to ``MAX_ATTEMPTS`` times. When the budget is
    exhausted an error is raised identifying ``label`` and the failure reason.

    Parameters
    ----------
    session : requests.Session
        The shared HTTP session.
    url : str
        The absolute URL to fetch.
    accept : str
        The ``Accept`` header value for the request.
    label : str
        A human-readable identifier used in the error message.

    Returns
    -------
    requests.Response
        The successful response (HTTP status < 400).
    """
    headers = {"Accept": accept}
    reason = "no attempts made"
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except (requests.ConnectionError, requests.Timeout) as exc:
            reason = f"{type(exc).__name__}: {exc}"
        else:
            if response.status_code < 400:
                return response
            reason = f"HTTP {response.status_code}"
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(2**attempt)
    raise RuntimeError(
        f"failed to fetch {label} after {MAX_ATTEMPTS} attempts: {reason}"
    )


def fetch_ind_econ(session: requests.Session) -> dict:
    """Fetch and parse ``ind-econ.json``.

    Parameters
    ----------
    session : requests.Session
        The shared HTTP session.

    Returns
    -------
    dict
        The parsed ``ind-econ.json`` payload.
    """
    response = _request_with_retries(
        session, IND_ECON_URL, "application/json", "ind-econ.json"
    )
    return response.json()


def fetch_structure(session: requests.Session, pid: str) -> str:
    """Fetch the SDMX-ML ``Structure_Message`` for a single CODR PID.

    Parameters
    ----------
    session : requests.Session
        The shared HTTP session.
    pid : str
        The 8-digit CODR PID.

    Returns
    -------
    str
        The raw bilingual SDMX-ML structure body.
    """
    url = f"{BASE_URL}/structure/Data_Structure_{pid}"
    response = _request_with_retries(
        session, url, STRUCTURE_ACCEPT, f"Data_Structure_{pid} (PID {pid})"
    )
    return response.text


def _bilingual_name(element: ET.Element, what: str) -> dict[str, str]:
    """Read an element's ``com:Name`` children into bilingual labels.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        The element carrying ``com:Name`` children tagged with ``xml:lang``.
    what : str
        A label used in the error message when no English name is found.

    Returns
    -------
    dict[str, str]
        ``{"en": ..., "fr": ...}`` where the French label falls back to the
        English label when it is absent.
    """
    names: dict[str, str] = {}
    for name in element.findall("com:Name", _NS):
        lang = name.get(_XML_LANG)
        if lang:
            names[lang] = (name.text or "").strip()
    en = names.get("en")
    if en is None:
        raise StructureParseError(f"missing English name for {what}")
    return {"en": en, "fr": names.get("fr") or en}


def _parse_codelists(root: ET.Element) -> dict[str, list[dict[str, str]]]:
    """Map each codelist id to its ordered code-to-bilingual-label pairs.

    Parameters
    ----------
    root : xml.etree.ElementTree.Element
        The parsed ``Structure_Message`` root.

    Returns
    -------
    dict[str, list[dict[str, str]]]
        Codelist id mapped to a list of ``{"code", "en", "fr"}`` records.
    """
    codelists: dict[str, list[dict[str, str]]] = {}
    for codelist in root.findall(".//str:Codelists/str:Codelist", _NS):
        cl_id = codelist.get("id", "")
        codes: list[dict[str, str]] = []
        for code in codelist.findall("str:Code", _NS):
            label = _bilingual_name(code, f"code {code.get('id')} in {cl_id}")
            codes.append({"code": code.get("id", ""), **label})
        codelists[cl_id] = codes
    return codelists


def parse_structure(xml_text: str, pid: str) -> dict:
    """Digest a bilingual SDMX-ML ``Structure_Message`` into a table entry.

    One generic parser for every cube: the StatsCan DSD shape is uniform, so no
    per-table special-casing is needed.

    Parameters
    ----------
    xml_text : str
        The raw SDMX-ML structure body.
    pid : str
        The 8-digit CODR PID, echoed into the returned entry.

    Returns
    -------
    dict
        A ``Normalized_Table_Entry``: ``pid``, bilingual ``name``, ``frequency``
        (placeholder, finalized later via ``classify_frequency``), ``freq_text``
        (the raw English text of the DataStructure ``freq`` annotation, or ``""``
        when absent), ``dimensions`` ordered by ascending declared position, and
        the declared ``attributes``.

    Raises
    ------
    StructureParseError
        When the body is malformed XML or missing expected structure elements.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise StructureParseError(f"malformed XML for PID {pid}: {exc}") from exc

    dataflow = root.find(".//str:Dataflows/str:Dataflow", _NS)
    if dataflow is None:
        raise StructureParseError(f"no Dataflow for PID {pid}")
    name = _bilingual_name(dataflow, f"dataflow {pid}")

    data_structure = root.find(".//str:DataStructures/str:DataStructure", _NS)
    if data_structure is None:
        raise StructureParseError(f"no DataStructure for PID {pid}")

    components = data_structure.find("str:DataStructureComponents", _NS)
    if components is None:
        raise StructureParseError(f"no DataStructureComponents for PID {pid}")

    codelists = _parse_codelists(root)

    dimensions: list[dict] = []
    for dim in components.findall("str:DimensionList/str:Dimension", _NS):
        try:
            position = int(dim.get("position", ""))
        except ValueError as exc:
            raise StructureParseError(
                f"invalid dimension position for PID {pid}: {dim.get('position')!r}"
            ) from exc
        ref = dim.find("str:LocalRepresentation/str:Enumeration/Ref", _NS)
        codelist_id = ref.get("id", "") if ref is not None else ""
        dimensions.append(
            {
                "id": dim.get("id", ""),
                "position": position,
                "codelist_id": codelist_id,
                "codes": codelists.get(codelist_id, []),
            }
        )
    dimensions.sort(key=lambda d: d["position"])

    attributes = [
        attr.get("id", "")
        for attr in components.findall("str:AttributeList/str:Attribute", _NS)
    ]

    freq_text = _freq_annotation_text(data_structure)

    return {
        "pid": pid,
        "name": name,
        "frequency": "undetermined",
        "freq_text": freq_text,
        "dimensions": dimensions,
        "attributes": attributes,
    }


def _freq_annotation_text(data_structure: ET.Element) -> str:
    """Read the English text of the DataStructure's ``freq`` annotation.

    Scoped to the ``DataStructure`` element's OWN direct ``com:Annotations``
    child, selecting the annotation whose ``com:AnnotationType`` text equals
    ``"freq"`` (case-insensitive, trimmed). This avoids matching the many
    footnote annotations carried on dimensions and codes elsewhere in the
    structure message.

    Parameters
    ----------
    data_structure : xml.etree.ElementTree.Element
        The ``str:DataStructure`` element.

    Returns
    -------
    str
        The English (``xml:lang="en"``) annotation text of the ``freq``
        annotation, or ``""`` when the annotation is absent.
    """
    for annotation in data_structure.findall("com:Annotations/com:Annotation", _NS):
        ann_type = annotation.find("com:AnnotationType", _NS)
        if ann_type is None or (ann_type.text or "").strip().lower() != "freq":
            continue
        for text in annotation.findall("com:AnnotationText", _NS):
            if text.get(_XML_LANG) == "en":
                return (text.text or "").strip()
    return ""


def classify_frequency(freq_text: str) -> str:
    """Classify the DataStructure ``freq`` annotation text into a frequency.

    StatsCan has no ``FREQ`` dimension and the TimeDimension ``TextFormat`` is
    empty; frequency is read from the ``freq`` annotation on the cube's
    ``DataStructure``. The function is total: any string maps to one of the four
    known values.

    Parameters
    ----------
    freq_text : str
        The English annotation text of the ``freq`` annotation (e.g.
        ``"Monthly"``, ``"Annual"``, ``"Quarterly"``).

    Returns
    -------
    str
        ``"monthly"`` for ``"Monthly"``, ``"annual"`` for ``"Annual"`` or
        ``"Annually"``, ``"quarterly"`` for ``"Quarterly"`` (compared
        case-insensitively after ``strip()``), else ``"undetermined"``.
    """
    normalized = freq_text.strip().lower()
    if normalized == "monthly":
        return "monthly"
    if normalized in ("annual", "annually"):
        return "annual"
    if normalized == "quarterly":
        return "quarterly"
    return "undetermined"


def serialize_catalog(blob: dict) -> bytes:
    """Serialize a catalog blob to compact UTF-8 JSON bytes.

    Parameters
    ----------
    blob : dict
        The ``Catalog_Cache`` blob.

    Returns
    -------
    bytes
        Compact JSON (``separators=(",", ":")``) with non-ASCII characters
        preserved (``ensure_ascii=False``), encoded as UTF-8.
    """
    return json.dumps(blob, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compress(payload: bytes) -> bytes:
    """Compress a payload with LZMA in the XZ container format.

    Parameters
    ----------
    payload : bytes
        The serialized catalog bytes.

    Returns
    -------
    bytes
        The LZMA/xz-compressed payload (``preset=6``).
    """
    return lzma.compress(payload, format=lzma.FORMAT_XZ, preset=6)


def write_cache(compressed: bytes) -> None:
    """Write the compressed catalog to the single ``.json.xz`` asset.

    Creates the ``assets/`` directory when absent and enforces the
    ``MAX_CACHE_BYTES`` ceiling. When the payload exceeds the bound the existing
    cache file is left unchanged and an error is raised.

    Parameters
    ----------
    compressed : bytes
        The LZMA/xz-compressed catalog payload.

    Raises
    ------
    ValueError
        When the compressed payload exceeds ``MAX_CACHE_BYTES``.
    """
    if len(compressed) > MAX_CACHE_BYTES:
        raise ValueError(
            f"compressed catalog is {len(compressed)} bytes, "
            f"exceeding the {MAX_CACHE_BYTES} byte ceiling"
        )
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_bytes(compressed)


def build_catalog(session: requests.Session | None = None) -> dict:
    """Orchestrate the catalog build, returning the ``Catalog_Cache`` blob.

    Fetches ``ind-econ.json``, derives the curated PID set, then fetches and
    parses each structure. A transport/fetch failure (raised by
    ``fetch_structure``) aborts the whole run by propagating. A
    ``StructureParseError`` skips only that PID and the run continues. Each
    successfully parsed entry's ``frequency`` is finalized via
    ``classify_frequency``.

    Parameters
    ----------
    session : requests.Session | None, optional
        The shared HTTP session; a fresh one is created when omitted.

    Returns
    -------
    dict
        The ``Catalog_Cache`` blob: ``schema_version`` (1), ``source``
        (``"statcan-sdmx"``), and ``tables`` keyed by CODR_PID.
    """
    if session is None:
        session = requests.Session()

    ind_econ = fetch_ind_econ(session)
    pids = derive_pids(ind_econ)

    tables: dict[str, dict] = {}
    for pid in pids:
        xml_text = fetch_structure(session, pid)
        try:
            entry = parse_structure(xml_text, pid)
        except StructureParseError:
            continue
        entry["frequency"] = classify_frequency(entry.pop("freq_text"))
        tables[pid] = entry

    return {
        "schema_version": 1,
        "source": "statcan-sdmx",
        "tables": tables,
    }


def main() -> None:
    """Generate the shipped ``government_ca_cache.json.xz`` catalog.

    Orchestrates the full build: builds the ``Catalog_Cache`` blob, serializes
    it to compact JSON, LZMA/xz-compresses it, and writes the single
    ``.json.xz`` asset. Returns on success and propagates any error on failure,
    so the same function backs both the ``generate-government-ca-cache`` console
    script and the Hatchling build hook.

    Raises
    ------
    Exception
        Any error raised while building, serializing, compressing, or writing
        the catalog propagates to the caller (no existing cache is changed when
        ``write_cache`` rejects an over-bound payload).
    """
    blob = build_catalog()
    write_cache(compress(serialize_catalog(blob)))


if __name__ == "__main__":
    main()
