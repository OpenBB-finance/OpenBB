"""GovInfo bulk-data download, cache, and parse helpers."""

import asyncio
import io
import json
import os
import re
import zipfile
from collections.abc import Awaitable, Callable
from datetime import date as dateType

from openbb_congress_gov.utils.helpers import BillsState

GOVINFO_BASE = "https://www.govinfo.gov"
BULKDATA_BASE = f"{GOVINFO_BASE}/bulkdata"

_CCAL_CHAMBER_CODE = {"house": "h", "senate": "s"}
_CCAL_PKG_RE = re.compile(r"CCAL-(\d+)([hs])cal-(\d{4}-\d{2}-\d{2})")

_MEMBER_RE = re.compile(r"-(\d+)([a-z]+)(\d+)\.xml$", re.IGNORECASE)
_BILL_URL_RE = re.compile(r"/bill/(\d+)/([a-z]+)/(\d+)", re.IGNORECASE)
_BILL_REF_RE = re.compile(r"^/?(\d+)[-/]([a-z]+)[-/](\d+)", re.IGNORECASE)
_AMENDMENT_URL_RE = re.compile(r"/amendment/(\d+)/([a-z]+)/(\d+)", re.IGNORECASE)
_AMENDMENT_REF_RE = re.compile(r"^/?(\d+)[-/]([a-z]+)[-/](\d+)", re.IGNORECASE)
_PKG_RE = re.compile(r"/content/pkg/([^/]+)/")


def bulk_zip_url(collection: str, congress: int, bill_type: str) -> str:
    """Build the consolidated bulk ZIP URL for a collection/congress/bill type."""
    bt = bill_type.lower()
    return (
        f"{BULKDATA_BASE}/{collection}/{congress}/{bt}/{collection}-{congress}-{bt}.zip"
    )


def parse_bill_ref(bill_ref: str) -> tuple[int, str, int]:
    """Parse a bill reference into ``(congress, bill_type, number)``."""
    match = _BILL_URL_RE.search(bill_ref) or _BILL_REF_RE.match(bill_ref)
    if not match:
        from openbb_core.app.model.abstract.error import OpenBBError

        raise OpenBBError(
            f"Could not parse a bill reference (congress/type/number) from: {bill_ref}"
        )
    return int(match.group(1)), match.group(2).lower(), int(match.group(3))


def parse_amendment_ref(amendment_ref: str) -> tuple[int, str, str]:
    """Parse an amendment reference into ``(congress, amendment_type, number)``."""
    match = _AMENDMENT_URL_RE.search(amendment_ref) or _AMENDMENT_REF_RE.match(
        amendment_ref
    )
    if not match:
        from openbb_core.app.model.abstract.error import OpenBBError

        raise OpenBBError(
            "Could not parse an amendment reference (congress/type/number)"
            f" from: {amendment_ref}"
        )
    return int(match.group(1)), match.group(2).lower(), match.group(3)


def _cache_dir() -> str | None:
    """Return the on-disk bulk-data cache directory, or None if it is not writable."""
    from openbb_core.app.utils import get_user_cache_directory

    path = f"{get_user_cache_directory()}/congress_gov/bulkdata"
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        return None
    return path


def _write_cache(path: str, meta_path: str, content: bytes, headers) -> None:
    """Persist downloaded content and conditional-GET metadata, ignoring write errors."""
    try:
        with open(path, "wb") as f:
            f.write(content)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "etag": headers.get("ETag"),
                    "last_modified": headers.get("Last-Modified"),
                },
                f,
            )
    except OSError:
        pass


async def _cached_get(url: str, filename: str) -> tuple[bytes, bool]:
    """Fetch ``url`` with a conditional GET, caching the body on disk when writable."""
    import aiohttp
    from openbb_core.app.model.abstract.error import OpenBBError

    cache_dir = _cache_dir()
    path = f"{cache_dir}/{filename}" if cache_dir else None
    meta_path = f"{path}.meta.json" if path else None

    meta: dict = {}
    if meta_path and os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

    headers: dict = {}
    if path and os.path.exists(path):
        if meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        if meta.get("last_modified"):
            headers["If-Modified-Since"] = meta["last_modified"]

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, headers=headers) as response,
        ):
            if response.status == 304 and path and os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read(), False

            response.raise_for_status()
            content = await response.read()
            if path and meta_path:
                _write_cache(path, meta_path, content, response.headers)
            return content, True
    except Exception as exc:  # noqa: BLE001
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                return f.read(), False
        raise OpenBBError(f"Failed to download data from {url} -> {exc}") from exc


async def _download_zip(
    collection: str, congress: int, bill_type: str
) -> tuple[bytes, bool]:
    """Download a bulk ZIP using a conditional GET."""
    bt = bill_type.lower()
    return await _cached_get(
        bulk_zip_url(collection, congress, bt),
        f"{collection}-{congress}-{bt}.zip",
    )


def _text(element, path: str) -> str:
    """Return the stripped text at ``path`` under ``element`` (empty if absent)."""
    node = element.find(path)
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def _item_dict(item) -> dict:
    """Flatten a leaf XML ``<item>`` into a dict of ``{tag: text}``."""
    return {child.tag: (child.text or "").strip() for child in item}


def parse_billstatus(zip_bytes: bytes) -> list[dict]:
    """Parse a BILLSTATUS ZIP into a list of API-shaped bill records."""
    from defusedxml.ElementTree import fromstring

    records: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xml"):
                continue
            bill = fromstring(archive.read(name)).find("bill")
            if bill is None:
                continue
            records.append(_billstatus_record(bill))
    return records


def _billstatus_record(bill) -> dict:
    """Map a single ``<bill>`` element to the API-shaped record dict."""
    congress = int(_text(bill, "congress") or 0)
    number = int(_text(bill, "number") or 0)
    bill_type = _text(bill, "type")

    titles = [_item_dict(i) for i in bill.findall("titles/item")]
    for title in titles:
        title.setdefault("type", title.get("titleType", ""))

    cosponsors = [_item_dict(i) for i in bill.findall("cosponsors/item")]
    for cosponsor in cosponsors:
        cosponsor["isOriginalCosponsor"] = (
            cosponsor.get("isOriginalCosponsor") == "True"
        )

    summaries: list[dict] = []
    for summary in bill.findall("summaries/summary"):
        summaries.append(
            {
                "versionCode": _text(summary, "versionCode"),
                "actionDate": _text(summary, "actionDate"),
                "actionDesc": _text(summary, "actionDesc"),
                "updateDate": _text(summary, "updateDate"),
                "text": _text(summary, "cdata/text"),
            }
        )

    return {
        "congress": congress,
        "number": number,
        "type": bill_type,
        "bill_id": f"{congress}-{bill_type.lower()}-{number}",
        "originChamber": _text(bill, "originChamber"),
        "originChamberCode": _text(bill, "originChamberCode"),
        "title": _text(bill, "title"),
        "introducedDate": _text(bill, "introducedDate"),
        "updateDate": _text(bill, "updateDate"),
        "updateDateIncludingText": _text(bill, "updateDateIncludingText"),
        "latestAction": {
            "actionDate": _text(bill, "latestAction/actionDate"),
            "text": _text(bill, "latestAction/text"),
        },
        "policyArea": {"name": _text(bill, "policyArea/name")},
        "sponsors": [_item_dict(i) for i in bill.findall("sponsors/item")],
        "cosponsors": cosponsors,
        "actions": [_item_dict(i) for i in bill.findall("actions/item")],
        "committees": [_item_dict(i) for i in bill.findall("committees/item")],
        "relatedBills": [_item_dict(i) for i in bill.findall("relatedBills/item")],
        "subjects": [
            _item_dict(i) for i in bill.findall("subjects/legislativeSubjects/item")
        ],
        "titles": titles,
        "summaries": summaries,
        "textVersions": [
            {
                "type": _text(item, "type"),
                "date": _text(item, "date"),
                "formats": [
                    {"url": _text(fmt, "url")} for fmt in item.findall("formats/item")
                ],
            }
            for item in bill.findall("textVersions/item")
        ],
        "amendments": [
            _amendment_record(am) for am in bill.findall("amendments/amendment")
        ],
    }


def _amendment_record(am) -> dict:
    """Map a single ``<amendment>`` element to an amendment record dict."""
    congress = int(_text(am, "congress") or 0)
    number = _text(am, "number")
    amd_type = _text(am, "type")

    amended_bill: dict = {}
    ab = am.find("amendedBill")
    if ab is not None:
        amended_bill = {
            "congress": _text(ab, "congress"),
            "type": _text(ab, "type"),
            "number": _text(ab, "number"),
            "title": _text(ab, "title"),
        }

    amended_amendment: dict = {}
    aa = am.find("amendedAmendment")
    if aa is not None:
        amended_amendment = {
            "congress": _text(aa, "congress"),
            "type": _text(aa, "type"),
            "number": _text(aa, "number"),
        }

    return {
        "amendment_id": f"{congress}-{amd_type.lower()}-{number}",
        "congress": congress,
        "number": number,
        "type": amd_type,
        "description": _text(am, "description"),
        "purpose": _text(am, "purpose"),
        "chamber": _text(am, "chamber"),
        "updateDate": _text(am, "updateDate"),
        "proposedDate": _text(am, "proposedDate"),
        "submittedDate": _text(am, "submittedDate"),
        "latestAction": {
            "actionDate": _text(am, "latestAction/actionDate"),
            "actionTime": _text(am, "latestAction/actionTime"),
            "text": _text(am, "latestAction/text"),
        },
        "sponsors": [_item_dict(i) for i in am.findall("sponsors/item")],
        "cosponsors": [_item_dict(i) for i in am.findall("cosponsors/item")],
        "actions": [_item_dict(i) for i in am.findall("actions/actions/item")],
        "links": [_item_dict(i) for i in am.findall("links/link")],
        "amendedBill": amended_bill,
        "amendedAmendment": amended_amendment,
    }


def parse_billsum(zip_bytes: bytes) -> dict[int, list[dict]]:
    """Parse a BILLSUM ZIP into ``{bill_number: [summary, ...]}``."""
    from defusedxml.ElementTree import fromstring

    out: dict[int, list[dict]] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in archive.namelist():
            match = _MEMBER_RE.search(name)
            if not match:
                continue
            number = int(match.group(3))
            root = fromstring(archive.read(name))
            summaries: list[dict] = []
            for item in root.findall("item"):
                summary = item.find("summary")
                if summary is None:
                    continue
                summaries.append(
                    {
                        "actionDate": _text(summary, "action-date"),
                        "actionDesc": _text(summary, "action-desc"),
                        "text": _text(summary, "summary-text"),
                    }
                )
            if summaries:
                out[number] = summaries
    return out


_LOAD_LOCKS: dict[str, asyncio.Lock] = {}


async def _memoized(key: str, loader: Callable[[], Awaitable]):
    """Return ``BillsState.bulk[key]``, computing it once via ``loader``."""
    state = BillsState()
    cached = state.bulk.get(key)
    if cached is not None:
        return cached

    lock = _LOAD_LOCKS.setdefault(key, asyncio.Lock())
    async with lock:
        cached = state.bulk.get(key)
        if cached is not None:
            return cached
        records = await loader()
        state.bulk[key] = records
        return records


async def load_billstatus(congress: int, bill_type: str) -> list[dict]:
    """Load (cached) BILLSTATUS records for a Congress and bill type."""

    async def _load():
        zip_bytes, _ = await _download_zip("BILLSTATUS", congress, bill_type)
        return parse_billstatus(zip_bytes)

    return await _memoized(f"BILLSTATUS_{congress}_{bill_type.lower()}", _load)


async def load_billsum(congress: int, bill_type: str) -> dict[int, list[dict]]:
    """Load (cached) BILLSUM summaries for a Congress and bill type."""

    async def _load():
        zip_bytes, _ = await _download_zip("BILLSUM", congress, bill_type)
        return parse_billsum(zip_bytes)

    return await _memoized(f"BILLSUM_{congress}_{bill_type.lower()}", _load)


def package_urls(pkg: str) -> dict:
    """Build the PDF/HTM/XML content URLs for a GovInfo package id."""
    base = f"https://www.govinfo.gov/content/pkg/{pkg}"
    return {
        "pdf": f"{base}/pdf/{pkg}.pdf",
        "htm": f"{base}/html/{pkg}.htm",
        "xml": f"{base}/xml/{pkg}.xml",
    }


def derive_text_formats(version: dict) -> dict | None:
    """Build PDF/HTM/XML URLs for a BILLSTATUS text version."""
    url = next(
        (fmt.get("url") for fmt in version.get("formats") or [] if fmt.get("url")),
        None,
    )
    match = _PKG_RE.search(url or "")
    if not match:
        return None

    return {
        "version_type": version.get("type", ""),
        "version_date": version.get("date", ""),
        **package_urls(match.group(1)),
    }


def to_list_item(record: dict) -> dict:
    """Project a full BILLSTATUS record to the slim ``bills`` list shape."""
    return {
        "updateDate": (record.get("updateDate") or "")[:10],
        "bill_id": record.get("bill_id"),
        "congress": record.get("congress"),
        "number": record.get("number"),
        "originChamber": record.get("originChamber"),
        "originChamberCode": record.get("originChamberCode"),
        "type": record.get("type"),
        "title": record.get("title"),
        "latestAction": record.get("latestAction", {}),
        "updateDateIncludingText": record.get("updateDateIncludingText"),
    }


def filter_bills(
    records: list[dict],
    *,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "desc",
) -> list[dict]:
    """Apply post-fetch filtering, sorting, and pagination to bill records."""

    def updated(record: dict) -> str:
        return (record.get("updateDate") or "")[:10]

    def sort_key(record: dict) -> str:
        latest = record.get("latestAction") or {}
        return latest.get("actionDate") or record.get("updateDate") or ""

    out = records
    if start_date is not None:
        out = [r for r in out if updated(r) and updated(r) >= str(start_date)]
    if end_date is not None:
        out = [r for r in out if updated(r) and updated(r) <= str(end_date)]

    out = sorted(out, key=sort_key, reverse=sort_by == "desc")

    out = out[offset or 0 :]

    if limit is None:
        return out[:100]
    if limit == 0:
        return out
    return out[:limit]


async def load_bill_record(bill_id: str) -> dict:
    """Load a single bill's full record, with BILLSUM summaries merged in."""
    from openbb_core.app.model.abstract.error import OpenBBError

    congress, bill_type, number = parse_bill_ref(bill_id)
    records = await load_billstatus(congress, bill_type)
    record = next((r for r in records if r.get("number") == number), None)

    if record is None:
        raise OpenBBError(
            f"Bill not found in bulk data: {congress}/{bill_type}/{number}"
        )

    record = dict(record)
    billsum = await load_billsum(congress, bill_type)
    if number in billsum:
        record["summaries"] = billsum[number]

    return record


def to_amendment_list_item(record: dict) -> dict:
    """Project a full amendment record to the slim ``amendments`` list shape."""
    return {
        "amendment_id": record.get("amendment_id"),
        "congress": record.get("congress"),
        "number": record.get("number"),
        "type": record.get("type"),
        "description": record.get("description") or None,
        "purpose": record.get("purpose") or None,
        "updateDate": (record.get("updateDate") or "")[:10] or None,
        "submittedDate": record.get("submittedDate"),
        "latestAction": record.get("latestAction") or {},
        "sponsors": record.get("sponsors") or [],
        "amendedBill": record.get("amendedBill") or {},
        "amendedAmendment": record.get("amendedAmendment") or {},
    }


async def load_amendments(
    congress: int, amendment_type: str | None = None
) -> list[dict]:
    """Load (cached) amendments for a Congress from the BILLSTATUS archives."""
    from openbb_congress_gov.utils.constants import BillTypes

    async def _load():
        groups = await asyncio.gather(
            *[load_billstatus(congress, bt) for bt in BillTypes]
        )
        seen: dict[tuple[str, str], dict] = {}
        for group in groups:
            for bill in group:
                for amendment in bill.get("amendments") or []:
                    key = (amendment["type"], amendment["number"])
                    seen.setdefault(key, amendment)
        return list(seen.values())

    records = await _memoized(f"AMENDMENTS_{congress}", _load)

    if amendment_type is not None:
        wanted = amendment_type.lower()
        records = [r for r in records if (r.get("type") or "").lower() == wanted]

    return records


async def load_amendment_record(amendment_id: str) -> dict:
    """Load a single amendment's full record from the BILLSTATUS archives."""
    from openbb_core.app.model.abstract.error import OpenBBError

    congress, amendment_type, number = parse_amendment_ref(amendment_id)
    records = await load_amendments(congress, amendment_type)
    record = next((r for r in records if r.get("number") == number), None)

    if record is None:
        raise OpenBBError(
            f"Amendment not found in bulk data: {congress}/{amendment_type}/{number}"
        )

    return record


def filter_amendments(
    records: list[dict],
    *,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "desc",
) -> list[dict]:
    """Apply post-fetch filtering, sorting, and pagination to amendment records."""

    def updated(record: dict) -> str:
        return (record.get("updateDate") or "")[:10]

    def sort_key(record: dict) -> str:
        latest = record.get("latestAction") or {}
        return latest.get("actionDate") or record.get("updateDate") or ""

    out = records
    if start_date is not None:
        out = [r for r in out if updated(r) and updated(r) >= str(start_date)]
    if end_date is not None:
        out = [r for r in out if updated(r) and updated(r) <= str(end_date)]

    out = sorted(out, key=sort_key, reverse=sort_by == "desc")
    out = out[offset or 0 :]

    if limit is None:
        return out[:100]
    if limit == 0:
        return out
    return out[:limit]


async def _resolve_link(url: str) -> str | None:
    """Resolve a GovInfo link-service URL to its final document URL."""
    import aiohttp

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, allow_redirects=False) as response,
        ):
            if response.status in (301, 302, 303, 307, 308):
                return response.headers.get("Location")
            return None
    except Exception:  # noqa: BLE001
        return None


def amendment_link_base(record: dict) -> str | None:
    """Build the GovInfo link-service base URL for an amendment record."""
    congress = record.get("congress")
    number = record.get("number")
    amd_type = (record.get("type") or "").upper()

    if amd_type == "HAMDT":
        amended_bill = record.get("amendedBill") or {}
        bill_type = (amended_bill.get("type") or "").lower()
        bill_number = amended_bill.get("number")
        if not bill_type or not bill_number:
            return None
        return (
            f"{GOVINFO_BASE}/link/crec/hamendment"
            f"/{congress}/{bill_type}/{bill_number}/{number}"
        )

    return f"{GOVINFO_BASE}/link/crec/samendment/{congress}/{number}"


async def resolve_amendment_text(record: dict) -> list[dict]:
    """Resolve an amendment's Congressional Record documents via the link service."""
    base = amendment_link_base(record)
    if base is None:
        return []

    formats = [("HTML", "htm", ""), ("PDF", "pdf", "pdf")]
    resolved = await asyncio.gather(
        *[
            _resolve_link(base + (f"?link-type={lt}" if lt else ""))
            for _, _, lt in formats
        ]
    )

    out: list[dict] = []
    for (label, key, _), url in zip(formats, resolved):
        if not url:
            continue
        date_match = re.search(r"CREC-(\d{4}-\d{2}-\d{2})", url)
        out.append(
            {
                "format": label,
                "format_key": key,
                "date": date_match.group(1) if date_match else "",
                "url": url,
            }
        )

    return out


def _local(tag: str) -> str:
    """Return an XML tag's local name, stripping any namespace prefix."""
    return tag.rsplit("}", maxsplit=1)[-1]


def parse_plaw(zip_bytes: bytes) -> list[dict]:
    """Parse a PLAW ZIP into a list of enacted-law records."""
    from defusedxml.ElementTree import fromstring

    records: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xml"):
                continue
            pkg = name.rsplit("/", 1)[-1][:-4]
            root = fromstring(archive.read(name))
            meta = next((el for el in root.iter() if _local(el.tag) == "meta"), None)
            if meta is None:
                continue
            records.append(_plaw_record(meta, pkg))
    return records


def _plaw_record(meta, pkg: str) -> dict:
    """Map a USLM ``<meta>`` element and package id to a law record dict."""
    fields: dict = {}
    citations: list[str] = []
    for child in meta:
        tag = _local(child.tag)
        text = (child.text or "").strip()
        if tag == "citableAs":
            citations.append(text)
        else:
            fields.setdefault(tag, text)

    congress = int(fields.get("congress") or 0)
    number = int(fields.get("docNumber") or 0)
    full_title = fields.get("title", "")
    title = full_title.split(": ", 1)[1] if ": " in full_title else full_title

    return {
        "congress": congress,
        "law_number": number,
        "law_type": fields.get("publicPrivate", ""),
        "law_id": f"{congress}-{number}",
        "package_id": pkg,
        "title": title,
        "citation": citations[0] if citations else fields.get("type", ""),
        "statute_citation": citations[1] if len(citations) > 1 else "",
        "enacted_date": fields.get("approvedDate") or fields.get("date") or "",
        **package_urls(pkg),
    }


async def load_plaw(congress: int, law_type: str) -> list[dict]:
    """Load (cached) PLAW law records for a Congress and law type (public/private)."""
    lt = law_type.lower()

    async def _load():
        zip_bytes, _ = await _download_zip("PLAW", congress, lt)
        return parse_plaw(zip_bytes)

    return await _memoized(f"PLAW_{congress}_{lt}", _load)


def filter_laws(
    records: list[dict],
    *,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "desc",
) -> list[dict]:
    """Sort enacted-law records by law number and apply pagination."""
    out = sorted(
        records, key=lambda r: r.get("law_number", 0), reverse=sort_by == "desc"
    )
    out = out[offset or 0 :]
    if limit is None:
        return out[:100]
    if limit == 0:
        return out
    return out[:limit]


def _congress_years(congress: int) -> list[int]:
    """Return the two calendar years spanned by a Congress (e.g. 119 -> [2025, 2026])."""
    start = 1789 + 2 * (congress - 1)
    return [start, start + 1]


async def load_calendars(congress: int, chamber: str) -> list[dict]:
    """Load (cached) Congressional Calendar editions for a Congress and chamber."""
    chamber = chamber.lower()
    code = _CCAL_CHAMBER_CODE[chamber]

    async def _load():
        records: list[dict] = []
        seen: set[str] = set()
        for year in _congress_years(congress):
            body, _ = await _cached_get(
                f"{GOVINFO_BASE}/sitemap/CCAL_{year}_sitemap.xml",
                f"CCAL_{year}_sitemap.xml",
            )
            text = body.decode("utf-8", errors="replace")
            for match in _CCAL_PKG_RE.finditer(text):
                pkg_congress, pkg_code, date = match.groups()
                if (
                    int(pkg_congress) != congress
                    or pkg_code != code
                    or match.group(0) in seen
                ):
                    continue
                seen.add(match.group(0))
                records.append(
                    {
                        "package_id": match.group(0),
                        "congress": congress,
                        "chamber": chamber,
                        "calendar_date": date,
                        "title": f"{chamber.title()} Calendar - {date}",
                        **package_urls(match.group(0)),
                    }
                )
        return records

    return await _memoized(f"CCAL_{congress}_{chamber}", _load)


def filter_calendars(
    records: list[dict],
    *,
    publishdate: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "desc",
) -> list[dict]:
    """Filter calendar editions by publish date and paginate."""
    out = sorted(records, key=lambda r: r["calendar_date"], reverse=sort_by == "desc")

    if publishdate == "mostrecent":
        return out[:1]
    if publishdate:
        return [r for r in out if r["calendar_date"] == publishdate]

    out = out[offset or 0 :]
    if limit is None:
        return out[:100]
    if limit == 0:
        return out
    return out[:limit]


async def fetch_cmr(congress: int, pagesize: int = 100, offset: int = 0) -> list[dict]:
    """Fetch Congressionally Mandated Reports from the keyless GovInfo link API."""
    from openbb_core.provider.utils.helpers import amake_request

    url = (
        f"{GOVINFO_BASE}/link/cmr/tableOfReports?congress={congress}"
        f"&link-type=json&pagesize={pagesize}&offset={offset}"
    )
    response = await amake_request(url)
    result_set = response.get("resultSet", []) if isinstance(response, dict) else []
    records = parse_cmr(result_set)
    records.sort(key=lambda r: r.get("publication_date") or "", reverse=True)
    return records


def parse_cmr(result_set: list[dict]) -> list[dict]:
    """Map raw CMR ``resultSet`` records to the data-model shape."""
    records: list[dict] = []
    for item in result_set:
        pkg = item.get("packageId", "")
        records.append(
            {
                "package_id": pkg,
                "title": item.get("title", ""),
                "submitting_agency": item.get("submittingAgency", ""),
                "publication_date": item.get("publicationDate") or None,
                "date_submitted_to_congress": item.get("dateSubmittedToCongress")
                or None,
                "date_required": item.get("dateRequiredToBeSubmittedToGPO") or None,
                "is_on_time": item.get("isOnTime") == "true",
                "pdf": item.get("pdfLink") or (package_urls(pkg)["pdf"] if pkg else ""),
                "details_link": item.get("detailsLink", ""),
                "mods_link": item.get("modsLink", ""),
            }
        )
    return records


WSSEARCH_URL = f"{GOVINFO_BASE}/wssearch/search"

DOC_TYPE_COLLECTION = {
    "report": "CRPT",
    "publication": "CPRT",
    "meeting": "CHRG",
    "legislation": "BILLS",
}

_CITATION_RE = re.compile(r"^(.*?)\s+-\s+", re.DOTALL)
_DATE_RE = re.compile(r"([A-Z][a-z]+ \d{1,2}, \d{4})")
_PKG_CHAMBER_RE = re.compile(r"-\d+([hsj])")


async def wssearch(
    query: str, *, offset: int = 0, pagesize: int = 20, sort: str = "2"
) -> dict:
    """Query the keyless GovInfo ``wssearch`` backend and return the parsed JSON."""
    import aiohttp
    from openbb_core.app.model.abstract.error import OpenBBError

    body = {
        "query": query,
        "offset": offset,
        "pageSize": pagesize,
        "sortBy": sort,
        "historical": False,
    }
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.post(WSSEARCH_URL, json=body) as response,
        ):
            response.raise_for_status()
            return await response.json()
    except Exception as exc:  # noqa: BLE001
        raise OpenBBError(f"GovInfo search failed for '{query}' -> {exc}") from exc


def _chamber_from_package(package_id: str) -> str:
    """Infer the chamber (House/Senate/Joint) from a package id."""
    match = _PKG_CHAMBER_RE.search(package_id)
    return {"h": "House", "s": "Senate", "j": "Joint"}.get(
        match.group(1) if match else "", ""
    )


def _wssearch_record(item: dict, doc_type: str, congress: int) -> dict:
    """Map a wssearch ``resultSet`` item to a committee-document record."""
    field_map = item.get("fieldMap", {})
    package_id = field_map.get("packageid", "")
    line1 = item.get("line1", "")
    line2 = item.get("line2", "")

    citation_match = _CITATION_RE.match(line1)
    citation = citation_match.group(1).strip() if citation_match else None

    date = None
    date_match = _DATE_RE.search(line2)
    if date_match:
        from datetime import datetime

        try:
            date = (
                datetime.strptime(date_match.group(1), "%B %d, %Y").date().isoformat()
            )
        except ValueError:
            date = None

    return {
        "doc_type": doc_type,
        "citation": citation,
        "title": field_map.get("title") or line1,
        "congress": congress,
        "chamber": _chamber_from_package(package_id),
        "date": date,
        "package_id": package_id,
        "doc_url": package_urls(package_id)["pdf"] if package_id else "",
    }


async def search_committee_docs(
    system_code: str,
    doc_type: str,
    congress: int,
    *,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Search GovInfo for a committee's documents of a given doc type (keyless)."""
    collection = DOC_TYPE_COLLECTION[doc_type]
    query = (
        f'committee:"{system_code.lower()}" AND collection:{collection} '
        f"AND congress:{congress}"
    )
    response = await wssearch(query, offset=offset, pagesize=limit)
    result_set = response.get("resultSet", []) if isinstance(response, dict) else []
    return [_wssearch_record(item, doc_type, congress) for item in result_set]


async def load_committee_structure() -> list[dict]:
    """Load (cached) the unitedstates committees-current dataset."""
    from openbb_core.provider.utils.helpers import amake_request

    state = BillsState()
    if "committee_structure" not in state.bulk:
        url = (
            "https://unitedstates.github.io/congress-legislators/"
            "committees-current.json"
        )
        try:
            data = await amake_request(url, timeout=30)
        except Exception:  # noqa: BLE001
            data = []
        state.bulk["committee_structure"] = data if isinstance(data, list) else []
    return state.bulk["committee_structure"]


async def fetch_package_mods(package_id: str) -> bytes:
    """Fetch (cached) the keyless MODS metadata for a GovInfo package."""
    body, _ = await _cached_get(
        f"{GOVINFO_BASE}/metadata/pkg/{package_id}/mods.xml",
        f"{package_id}.mods.xml",
    )
    return body


def parse_mods(mods_bytes: bytes, package_id: str) -> dict:
    """Parse a package MODS document for committee-document detail."""
    from defusedxml.ElementTree import fromstring

    root = fromstring(mods_bytes)
    witnesses = [
        (el.text or "").strip()
        for el in root.iter()
        if _local(el.tag) == "witness" and (el.text or "").strip()
    ]
    held_dates = [
        (el.text or "").strip()
        for el in root.iter()
        if _local(el.tag) == "heldDate" and (el.text or "").strip()
    ]

    documents: list[dict] = []
    for related in root:
        if _local(related.tag) != "relatedItem" or related.get("type") != "constituent":
            continue
        access_id = next(
            (
                (e.text or "").strip()
                for e in related.iter()
                if _local(e.tag) == "accessId"
            ),
            "",
        )
        title = next(
            (
                (e.text or "").strip()
                for e in related.iter()
                if _local(e.tag) == "title" and (e.text or "").strip()
            ),
            "",
        )
        if access_id:
            documents.append(
                {
                    "granule_id": access_id,
                    "title": title,
                    "pdf": (
                        f"{GOVINFO_BASE}/content/pkg/{package_id}/pdf/{access_id}.pdf"
                    ),
                }
            )

    return {
        "witnesses": witnesses,
        "held_dates": held_dates,
        "documents": documents,
    }


CONGRESSIONAL_COLLECTIONS = [
    "BILLS",
    "CRPT",
    "CHRG",
    "CPRT",
    "CREC",
    "CCAL",
    "CMR",
    "PLAW",
]
COLLECTION_LABELS = {
    "BILLS": "Bills",
    "CRPT": "Committee Reports",
    "CHRG": "Hearings",
    "CPRT": "Committee Prints",
    "CREC": "Congressional Record",
    "CCAL": "Calendars",
    "CMR": "Mandated Reports",
    "PLAW": "Public Laws",
}

_PKG_CONGRESS_RE = re.compile(r"^[A-Z]+-(\d+)")


def _search_record(item: dict) -> dict:
    """Map a wssearch result item to a full-text search record."""
    field_map = item.get("fieldMap", {})
    package_id = field_map.get("packageid", "")
    base = _wssearch_record(item, "", 0)
    congress_match = _PKG_CONGRESS_RE.match(package_id)
    return {
        "title": base["title"],
        "collection": field_map.get("collectionCode", ""),
        "date": base["date"],
        "congress": int(congress_match.group(1)) if congress_match else None,
        "citation": base["citation"],
        "package_id": package_id,
        "doc_url": base["doc_url"],
    }


async def search_govinfo(
    query: str,
    *,
    collection: str | None = None,
    congress: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Full-text search across the congressional GovInfo collections (keyless)."""
    parts = [query]

    if collection:
        parts.append(f"collection:{collection}")
    else:
        parts.append(
            "("
            + " OR ".join(f"collection:{c}" for c in CONGRESSIONAL_COLLECTIONS)
            + ")"
        )

    if congress is not None:
        parts.append(f"congress:{congress}")

    if start_date or end_date:
        from datetime import datetime

        lower = start_date or "1789-01-01"
        upper = end_date or datetime.now().date().isoformat()
        parts.append(f"publishdate:range({lower},{upper})")

    response = await wssearch(" AND ".join(parts), offset=offset, pagesize=limit)
    result_set = response.get("resultSet", []) if isinstance(response, dict) else []
    records = [_search_record(item) for item in result_set]
    records.sort(key=lambda r: r.get("date") or "", reverse=True)
    return records


async def load_legislators() -> dict:
    """Load (cached) current legislators, indexed by bioguide id."""
    from openbb_core.provider.utils.helpers import amake_request

    state = BillsState()
    if "legislators" not in state.bulk:
        url = (
            "https://unitedstates.github.io/congress-legislators/"
            "legislators-current.json"
        )
        try:
            data = await amake_request(url, timeout=30)
        except Exception:  # noqa: BLE001
            data = []

        index: dict = {}
        for member in data if isinstance(data, list) else []:
            bioguide = member.get("id", {}).get("bioguide")
            if not bioguide:
                continue
            term = (member.get("terms") or [{}])[-1]
            index[bioguide] = {
                "party": term.get("party", ""),
                "state": term.get("state", ""),
                "full_name": member.get("name", {}).get("official_full", ""),
                "birthday": member.get("bio", {}).get("birthday", ""),
                "photo_url": (
                    f"https://unitedstates.github.io/images/congress/225x275/{bioguide}.jpg"
                ),
            }
        state.bulk["legislators"] = index

    return state.bulk["legislators"]


_LEGISLATORS_BASE = "https://unitedstates.github.io/congress-legislators"
_BILLSTATUS_MIN_CONGRESS = 108

VOTEVIEW_BASE = "https://voteview.com/static/data/out"
_CAST_CODES = {
    "1": "Yea",
    "2": "Yea",
    "3": "Yea",
    "4": "Nay",
    "5": "Nay",
    "6": "Nay",
    "7": "Present",
    "8": "Present",
    "9": "Not Voting",
}
_YEA_CODES = {"1", "2", "3"}
_NAY_CODES = {"4", "5", "6"}
_BILL_NUMBER_RE = re.compile(r"^([A-Z]+)(\d+)$")
_BILL_NUMBER_TYPES = {
    "HR",
    "S",
    "HRES",
    "SRES",
    "HJRES",
    "SJRES",
    "HCONRES",
    "SCONRES",
}


def _bill_number_to_id(bill_number: str, congress: int) -> str | None:
    """Convert a Voteview ``bill_number`` to a canonical bill id."""
    match = _BILL_NUMBER_RE.match((bill_number or "").strip().upper())
    if not match or match.group(1) not in _BILL_NUMBER_TYPES:
        return None
    return f"{congress}-{match.group(1).lower()}-{match.group(2)}"


def _chamber_from_term_type(term_type: str) -> str:
    """Map a term ``type`` (``rep``/``sen``) to a chamber label."""
    return {"rep": "house", "sen": "senate"}.get(term_type, "")


async def load_members() -> list[dict]:
    """Load (cached) the current members of Congress from the unitedstates dataset."""
    from openbb_core.provider.utils.helpers import amake_request

    state = BillsState()
    if "members" not in state.bulk:
        try:
            data = await amake_request(
                f"{_LEGISLATORS_BASE}/legislators-current.json", timeout=30
            )
        except Exception:  # noqa: BLE001
            data = []
        state.bulk["members"] = data if isinstance(data, list) else []
    return state.bulk["members"]


async def load_social_media() -> dict:
    """Load (cached) members' social-media handles, indexed by bioguide id."""
    from openbb_core.provider.utils.helpers import amake_request

    state = BillsState()
    if "social_media" not in state.bulk:
        try:
            data = await amake_request(
                f"{_LEGISLATORS_BASE}/legislators-social-media.json", timeout=30
            )
        except Exception:  # noqa: BLE001
            data = []
        index: dict = {}
        for entry in data if isinstance(data, list) else []:
            bioguide = entry.get("id", {}).get("bioguide")
            if bioguide:
                index[bioguide] = entry.get("social", {})
        state.bulk["social_media"] = index
    return state.bulk["social_media"]


async def load_committee_membership() -> dict:
    """Load (cached) the current committee-membership dataset (by THOMAS id)."""
    from openbb_core.provider.utils.helpers import amake_request

    state = BillsState()
    if "committee_membership" not in state.bulk:
        try:
            data = await amake_request(
                f"{_LEGISLATORS_BASE}/committee-membership-current.json", timeout=30
            )
        except Exception:  # noqa: BLE001
            data = {}
        state.bulk["committee_membership"] = data if isinstance(data, dict) else {}
    return state.bulk["committee_membership"]


async def member_committees(bioguide: str) -> list[dict]:
    """Return the committees and subcommittees a member sits on."""
    membership = await load_committee_membership()
    structure = await load_committee_structure()

    names: dict[str, str] = {}
    for committee in structure:
        tid = committee.get("thomas_id", "")
        if tid:
            names[tid] = committee.get("name", tid)
        for sub in committee.get("subcommittees") or []:
            sub_tid = f"{tid}{sub.get('thomas_id', '')}"
            names[sub_tid] = f"{committee.get('name', tid)} — {sub.get('name', '')}"

    out: list[dict] = []
    for tid, members in membership.items():
        for member in members:
            if member.get("bioguide") == bioguide:
                out.append(
                    {
                        "committee": names.get(tid, tid),
                        "rank": member.get("rank"),
                        "title": member.get("title", ""),
                        "side": member.get("party", ""),
                        "is_subcommittee": len(tid) > 4,
                    }
                )
    out.sort(key=lambda c: (c["is_subcommittee"], c["committee"]))
    return out


async def load_member_record(bioguide: str) -> dict:
    """Load a single current member's full record by bioguide id."""
    from openbb_core.app.model.abstract.error import OpenBBError

    members = await load_members()
    record = next(
        (m for m in members if m.get("id", {}).get("bioguide") == bioguide), None
    )
    if record is None:
        raise OpenBBError(f"Member not found in current Congress: {bioguide}")
    return record


def to_member_list_item(record: dict) -> dict:
    """Project a full member record to the slim ``members`` list shape."""
    term = (record.get("terms") or [{}])[-1]
    ids = record.get("id", {})
    name = record.get("name", {})
    return {
        "bioguide_id": ids.get("bioguide", ""),
        "name": name.get("official_full")
        or f"{name.get('first', '')} {name.get('last', '')}".strip(),
        "chamber": _chamber_from_term_type(term.get("type", "")),
        "party": term.get("party", ""),
        "state": term.get("state", ""),
        "district": term.get("district"),
        "term_start": term.get("start"),
        "term_end": term.get("end"),
        "website": term.get("url", ""),
    }


def filter_members(
    records: list[dict],
    *,
    chamber: str | None = None,
    state: str | None = None,
    party: str | None = None,
) -> list[dict]:
    """Filter slim member items by chamber, state, and party; sort by name."""
    out = records
    if chamber is not None:
        out = [r for r in out if r.get("chamber") == chamber]
    if state is not None:
        out = [r for r in out if (r.get("state") or "").upper() == state.upper()]
    if party is not None:
        out = [r for r in out if (r.get("party") or "").lower() == party.lower()]
    return sorted(out, key=lambda r: r.get("name") or "")


def member_served_congresses(record: dict) -> list[int]:
    """Return the Congress numbers a member served, newest first."""
    from openbb_congress_gov.utils.helpers import year_to_congress

    congresses: set[int] = set()
    for term in record.get("terms") or []:
        start = (term.get("start") or "")[:4]
        if not start.isdigit():
            continue
        try:
            congress = year_to_congress(int(start))
        except ValueError:
            continue
        if congress >= _BILLSTATUS_MIN_CONGRESS:
            congresses.add(congress)
    return sorted(congresses, reverse=True)


def member_service(record: dict) -> list[tuple[int, str]]:
    """Return the ``(congress, chamber)`` pairs a member served, newest first."""
    from openbb_congress_gov.utils.helpers import year_to_congress

    seen: dict[int, str] = {}
    for term in record.get("terms") or []:
        start = (term.get("start") or "")[:4]
        if not start.isdigit():
            continue
        try:
            congress = year_to_congress(int(start))
        except ValueError:
            continue
        seen[congress] = "H" if term.get("type") == "rep" else "S"
    return [(c, seen[c]) for c in sorted(seen, reverse=True)]


async def member_legislation(bioguide: str, congresses: list[int]) -> list[dict]:
    """Return bills a member sponsored or cosponsored across the given Congresses."""
    from openbb_congress_gov.utils.constants import BillTypes

    pairs = [(congress, bt) for congress in congresses for bt in BillTypes]
    groups = await asyncio.gather(*[load_billstatus(c, bt) for c, bt in pairs])

    out: list[dict] = []
    for (congress, _), group in zip(pairs, groups):
        for bill in group:
            sponsored = any(
                s.get("bioguideId") == bioguide for s in bill.get("sponsors") or []
            )
            cosponsored = any(
                c.get("bioguideId") == bioguide for c in bill.get("cosponsors") or []
            )
            if not sponsored and not cosponsored:
                continue
            latest = bill.get("latestAction") or {}
            out.append(
                {
                    "bill_id": bill.get("bill_id"),
                    "congress": congress,
                    "role": "Sponsor" if sponsored else "Cosponsor",
                    "title": bill.get("title"),
                    "introduced_date": bill.get("introducedDate"),
                    "latest_action_date": latest.get("actionDate"),
                    "latest_action": latest.get("text"),
                }
            )

    out.sort(key=lambda b: b.get("introduced_date") or "", reverse=True)
    return out


async def _voteview_text(kind: str, congress: int, chamber: str) -> str:
    """Fetch (and disk-cache) a Voteview CSV for a Congress and chamber."""
    url = f"{VOTEVIEW_BASE}/{kind}/{chamber}{congress}_{kind}.csv"
    try:
        data, _ = await _cached_get(url, f"voteview-{kind}-{chamber}{congress}.csv")
    except Exception:  # noqa: BLE001
        return ""
    return data.decode("utf-8", "replace")


async def load_voteview_members(congress: int, chamber: str) -> dict[str, str]:
    """Load (cached) a Voteview members file as ``{bioguide_id: icpsr}``."""
    import csv
    import io

    async def _load():
        text = await _voteview_text("members", congress, chamber)
        index: dict[str, str] = {}
        for row in csv.DictReader(io.StringIO(text)):
            bioguide = row.get("bioguide_id")
            icpsr = row.get("icpsr")
            if bioguide and icpsr:
                index[bioguide] = icpsr
        return index

    return await _memoized(f"VV_MEMBERS_{chamber}{congress}", _load)


async def load_voteview_rollcalls(congress: int, chamber: str) -> dict[str, dict]:
    """Load (cached) a Voteview rollcalls file as ``{rollnumber: metadata}``."""
    import csv
    import io

    async def _load():
        text = await _voteview_text("rollcalls", congress, chamber)
        rolls: dict[str, dict] = {}
        for row in csv.DictReader(io.StringIO(text)):
            rolls[row.get("rollnumber", "")] = {
                "bill_number": row.get("bill_number", ""),
                "question": row.get("vote_question", ""),
                "result": row.get("vote_result", ""),
                "title": row.get("vote_desc", ""),
                "date": row.get("date", ""),
            }
        return rolls

    return await _memoized(f"VV_ROLLCALLS_{chamber}{congress}", _load)


async def load_voteview_votes(congress: int, chamber: str) -> dict[str, list[tuple]]:
    """Load (cached) a Voteview votes file as ``{icpsr: [(rollnumber, cast_code)]}``."""
    import csv
    import io

    async def _load():
        text = await _voteview_text("votes", congress, chamber)
        index: dict[str, list[tuple]] = {}
        for row in csv.DictReader(io.StringIO(text)):
            index.setdefault(row.get("icpsr", ""), []).append(
                (row.get("rollnumber", ""), row.get("cast_code", ""))
            )
        return index

    return await _memoized(f"VV_VOTES_{chamber}{congress}", _load)


async def member_congress_votes(
    bioguide: str, congress: int, chamber: str
) -> list[dict]:
    """Return a member's roll-call votes for one Congress/chamber, from Voteview."""
    members = await load_voteview_members(congress, chamber)
    icpsr = members.get(bioguide)
    if icpsr is None:
        return []

    rollcalls = await load_voteview_rollcalls(congress, chamber)
    votes = await load_voteview_votes(congress, chamber)

    chamber_name = "house" if chamber == "H" else "senate"
    out: list[dict] = []
    for rollnumber, cast_code in votes.get(icpsr, []):
        position = _CAST_CODES.get(cast_code)
        if position is None:
            continue
        meta = rollcalls.get(rollnumber, {})
        out.append(
            {
                "congress": congress,
                "chamber": chamber_name,
                "rollnumber": int(rollnumber or 0),
                "position": position,
                "cast_code": cast_code,
                "bill_id": _bill_number_to_id(meta.get("bill_number", ""), congress),
                "legislation": meta.get("bill_number") or None,
                "title": meta.get("title") or None,
                "question": meta.get("question") or None,
                "result": meta.get("result") or None,
                "date": meta.get("date") or None,
            }
        )
    return out


async def member_votes(
    bioguide: str, service: list[tuple[int, str]], *, limit: int = 25
) -> list[dict]:
    """Return a member's most recent roll-call votes on legislation across tenure."""
    groups = await asyncio.gather(
        *[member_congress_votes(bioguide, c, ch) for c, ch in service]
    )
    votes = [vote for group in groups for vote in group if vote.get("bill_id")]
    votes.sort(
        key=lambda v: (v.get("date") or "", v.get("rollnumber") or 0), reverse=True
    )
    return votes[:limit]


async def member_passage_record(bioguide: str, service: list[tuple[int, str]]) -> dict:
    """Tally a member's Yea/Nay record on 'On Passage' votes across their tenure."""
    groups = await asyncio.gather(
        *[member_congress_votes(bioguide, c, ch) for c, ch in service]
    )
    yea = nay = 0
    for group in groups:
        for vote in group:
            if not (vote.get("question") or "").startswith("On Passage"):
                continue
            if vote["cast_code"] in _YEA_CODES:
                yea += 1
            elif vote["cast_code"] in _NAY_CODES:
                nay += 1

    total = yea + nay
    return {
        "yea": yea,
        "nay": nay,
        "total": total,
        "yea_pct": round(100 * yea / total, 1) if total else None,
    }
