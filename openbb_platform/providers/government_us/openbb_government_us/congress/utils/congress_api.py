"""Congress.gov API v3 client.

GovInfo publishes BILLSTATUS bulk archives only from the 108th Congress onward.
Anything older has to come from the Congress.gov API, which needs an API key.
Records returned here are shaped exactly like``bulk.parse_billstatus``.

A key is free from https://api.congress.gov/sign-up/ and is set as the
``congress_gov_api_key`` credential.
"""

import asyncio
import logging

logger = logging.getLogger("uvicorn.error")

CONGRESS_API_BASE = "https://api.congress.gov/v3"

# The oldest Congress GovInfo publishes a BILLSTATUS bulk archive for; anything
# below this routes here instead. Mirrors bulk._BILLSTATUS_MIN_CONGRESS.
_BULK_FLOOR = 108

# Congress.gov carries bill data back to the 93rd Congress (1973). The 6th-42nd
# are present only as scanned volumes with no structured bill records.
API_MIN_CONGRESS = 93

# The API caps a page at 250 records.
_PAGE_LIMIT = 250

# Backstop only. Paging normally stops on the collection's reported total; the
# busiest Congress on record (the 93rd, 17,690 House bills) needs 71 pages.
_MAX_PAGES = 400

_SUB_RESOURCES = (
    "actions",
    "amendments",
    "committees",
    "cosponsors",
    "relatedbills",
    "subjects",
    "summaries",
    "text",
    "titles",
)


def user_credentials() -> dict[str, str]:
    """Read the Congress.gov key from user settings.

    Router endpoints (the bill/amendment text pickers) are plain routes rather
    than fetchers, so nothing injects credentials into them. They resolve the
    key themselves through this.
    """
    try:
        from openbb_core.app.service.user_service import UserService

        credentials = UserService().default_user_settings.credentials
        key = getattr(credentials, "congress_gov_api_key", None)
    except Exception as exc:  # noqa: BLE001
        logger.warning("congress_gov: could not read user credentials: %s", exc)
        return {}

    if not key:
        return {}

    return {
        "congress_gov_api_key": str(getattr(key, "get_secret_value", lambda: key)())
    }


def api_key(credentials: dict[str, str] | None) -> str:
    """Return the Congress.gov API key, raising a directed error when it is unset."""
    from openbb_core.app.model.abstract.error import OpenBBError

    key = (credentials or {}).get("congress_gov_api_key") or user_credentials().get(
        "congress_gov_api_key"
    )

    if not key:
        raise OpenBBError(
            "A Congress.gov API key is required for Congresses before the"
            f" {_BULK_FLOOR}th, which predate the GovInfo bulk archives."
            " Get a free key at https://api.congress.gov/sign-up/ and set it as"
            " 'congress_gov_api_key'."
        )

    return key


async def _get(path: str, key: str, **params) -> dict:
    """Issue one Congress.gov API request and return its decoded body."""
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request

    query = {"format": "json", "api_key": key, **params}
    url = f"{CONGRESS_API_BASE}/{path.lstrip('/')}"

    try:
        data = await amake_request(url, params=query, timeout=30)
    except Exception as exc:  # noqa: BLE001
        raise OpenBBError(f"Congress.gov API request failed -> {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise OpenBBError(f"Unexpected Congress.gov API response for {path}: {data!r}")

    if data.get("error"):
        raise OpenBBError(f"Congress.gov API error for {path}: {data['error']}")

    return data


async def _paged(path: str, key: str, field: str, limit: int | None = None) -> list:
    """Walk a paginated Congress.gov collection and return its items."""
    items: list = []
    offset = 0
    total: int | None = None

    for _ in range(_MAX_PAGES):
        want = _PAGE_LIMIT if limit is None else min(_PAGE_LIMIT, limit - len(items))
        if want <= 0:
            break

        data = await _get(path, key, offset=offset, limit=want)
        pagination = data.get("pagination") or {}

        if total is None and isinstance(pagination.get("count"), int):
            total = pagination["count"]

        page = data.get(field) or []

        if isinstance(page, dict):
            # ``subjects`` nests its lists under the field rather than listing them.
            return [page]

        items.extend(page)

        if not page or len(page) < want or not pagination.get("next"):
            break

        if total is not None and len(items) >= total:
            break

        offset += len(page)

    return items


def _latest_action(payload: dict) -> dict:
    """Normalize a latestAction block to the BILLSTATUS record shape."""
    latest = payload.get("latestAction") or {}
    return {
        "actionDate": latest.get("actionDate") or "",
        "text": latest.get("text") or "",
    }


def bill_id(congress: int, bill_type: str, number: int | str) -> str:
    """Build the canonical ``{congress}-{type}-{number}`` bill id."""
    return f"{congress}-{str(bill_type).lower()}-{number}"


def _list_item(payload: dict) -> dict:
    """Project an API bill-list entry onto the store's slim bills-list shape."""
    congress = int(payload.get("congress") or 0)
    bill_type = payload.get("type") or ""
    number = payload.get("number") or ""

    return {
        "updateDate": (payload.get("updateDate") or "")[:10] or None,
        "bill_id": bill_id(congress, bill_type, number),
        "congress": congress,
        "number": int(number) if str(number).isdigit() else 0,
        "originChamber": payload.get("originChamber") or "",
        "originChamberCode": payload.get("originChamberCode") or "",
        "type": bill_type,
        "title": payload.get("title") or "",
        "latestAction": {
            "actionDate": _latest_action(payload).get("actionDate") or None,
            "text": _latest_action(payload).get("text") or None,
        },
        "updateDateIncludingText": (payload.get("updateDateIncludingText") or "")[:10]
        or None,
    }


def slim_record(payload: dict) -> dict:
    """Build a BILLSTATUS-shaped record from a bill-list entry.

    The list endpoint carries only headline fields, so the nested collections
    start empty and ``_detailed`` stays False. ``load_bill_record`` hydrates the
    row from the detail endpoint the first time a single bill is opened.
    """
    congress = int(payload.get("congress") or 0)
    bill_type = payload.get("type") or ""
    number = payload.get("number") or ""

    return {
        "congress": congress,
        "number": int(number) if str(number).isdigit() else 0,
        "type": bill_type,
        "bill_id": bill_id(congress, bill_type, number),
        "originChamber": payload.get("originChamber") or "",
        "originChamberCode": payload.get("originChamberCode") or "",
        "title": payload.get("title") or "",
        "introducedDate": payload.get("introducedDate") or "",
        "updateDate": payload.get("updateDate") or "",
        "updateDateIncludingText": payload.get("updateDateIncludingText") or "",
        "latestAction": _latest_action(payload),
        "policyArea": {"name": ""},
        "sponsors": [],
        "cosponsors": [],
        "actions": [],
        "committees": [],
        "relatedBills": [],
        "subjects": [],
        "titles": [],
        "summaries": [],
        "textVersions": [],
        "amendments": [],
        "_detailed": False,
    }


async def fetch_bill_list(
    congress: int, bill_type: str, credentials: dict[str, str] | None
) -> list[dict]:
    """Return every bill of one type in a Congress, shaped for the store."""
    key = api_key(credentials)
    _require_coverage(congress)

    entries = await _paged_filtered(f"bill/{congress}/{bill_type.lower()}", key, {})

    return [slim_record(entry) for entry in entries]


def _sort_key(item: dict) -> str:
    """Order by latest action date, falling back to the update date, as the store does."""
    latest = (item.get("latestAction") or {}).get("actionDate")
    return latest or item.get("updateDate") or ""


async def list_bills(
    congress: int,
    bill_types: list[str],
    credentials: dict[str, str] | None,
    *,
    start_date=None,
    end_date=None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "desc",
) -> list[dict]:
    """Return a Congress's bills from the API, shaped like the bulk store's list."""
    key = api_key(credentials)
    _require_coverage(congress)

    params: dict = {}
    if start_date is not None:
        params["fromDateTime"] = f"{start_date}T00:00:00Z"
    if end_date is not None:
        params["toDateTime"] = f"{end_date}T23:59:59Z"

    async def _one(bill_type: str) -> list[dict]:
        path = f"bill/{congress}/{bill_type.lower()}"
        try:
            return await _paged_filtered(path, key, params)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "congress_gov: Congress.gov API list failed for %s-%s: %s",
                congress,
                bill_type,
                exc,
            )
            return []

    pages = await asyncio.gather(*[_one(bt) for bt in bill_types])
    items = [_list_item(entry) for page in pages for entry in page]

    items.sort(key=_sort_key, reverse=sort_by != "asc")

    start = offset or 0
    if limit == 0:
        return items[start:]

    return items[start : start + (limit or 100)]


async def _paged_filtered(path: str, key: str, params: dict) -> list:
    """Walk a bill-list collection in full, forwarding the date-window parameters.

    Paging runs until the collection's reported ``count`` has been collected, so
    a Congress with more bills than any fixed page budget is never silently
    truncated. A short page or a missing ``next`` link also ends the walk.
    """
    items: list = []
    offset = 0
    total: int | None = None

    for _ in range(_MAX_PAGES):
        data = await _get(path, key, offset=offset, limit=_PAGE_LIMIT, **params)
        pagination = data.get("pagination") or {}

        if total is None and isinstance(pagination.get("count"), int):
            total = pagination["count"]

        page = data.get("bills") or []
        items.extend(page)

        if not page or len(page) < _PAGE_LIMIT or not pagination.get("next"):
            break

        if total is not None and len(items) >= total:
            break

        offset += len(page)

    if total is not None and len(items) < total:
        logger.warning(
            "congress_gov: %s returned %d of %d records; the page budget (%d)"
            " was exhausted",
            path,
            len(items),
            total,
            _MAX_PAGES,
        )

    return items


def _require_coverage(congress: int) -> None:
    """Raise when a Congress predates structured bill records on Congress.gov."""
    from openbb_core.app.model.abstract.error import OpenBBError

    if congress < API_MIN_CONGRESS:
        raise OpenBBError(
            f"Congress {congress} predates structured bill data. GovInfo bulk"
            f" archives start at the {_BULK_FLOOR}th Congress and the Congress.gov"
            f" API reaches back to the {API_MIN_CONGRESS}rd (1973)."
        )


def _text_versions(payload: list) -> list[dict]:
    """Normalize the API's text versions onto the BILLSTATUS record shape."""
    versions: list[dict] = []

    for version in payload:
        versions.append(
            {
                "type": version.get("type") or "",
                "date": version.get("date") or "",
                "formats": [
                    {"url": fmt.get("url") or ""}
                    for fmt in version.get("formats") or []
                    if fmt.get("url")
                ],
            }
        )

    return versions


def _committees(payload: list) -> list[dict]:
    """Normalize committee entries, keeping activities and subcommittees."""
    committees: list[dict] = []

    for committee in payload:
        committees.append(
            {
                "systemCode": committee.get("systemCode") or "",
                "name": committee.get("name") or "",
                "chamber": committee.get("chamber") or "",
                "type": committee.get("type") or "",
                "activities": committee.get("activities") or [],
                "subcommittees": committee.get("subcommittees") or [],
            }
        )

    return committees


def _cosponsors(payload: list) -> list[dict]:
    """Normalize cosponsors, coercing the original-cosponsor flag to a bool."""
    cosponsors: list[dict] = []

    for cosponsor in payload:
        entry = dict(cosponsor)
        entry["isOriginalCosponsor"] = bool(cosponsor.get("isOriginalCosponsor"))
        cosponsors.append(entry)

    return cosponsors


async def bill_record(
    congress: int,
    bill_type: str,
    number: int,
    credentials: dict[str, str] | None,
) -> dict:
    """Assemble a full bill record from the API, shaped like a BILLSTATUS record.

    The API splits a bill across a detail document and nine sub-collections, so
    they are fetched concurrently and folded back into the single nested record
    the bulk path produces.
    """

    key = api_key(credentials)
    _require_coverage(congress)

    bt = bill_type.lower()
    base = f"bill/{congress}/{bt}/{number}"

    detail = await _get(base, key)
    bill = detail.get("bill")

    if not bill:
        from openbb_government_us.congress.utils.bulk import BillNotFound

        raise BillNotFound(f"Bill not found on Congress.gov: {congress}/{bt}/{number}")

    fields = {
        "actions": "actions",
        "amendments": "amendments",
        "committees": "committees",
        "cosponsors": "cosponsors",
        "relatedbills": "relatedBills",
        "subjects": "subjects",
        "summaries": "summaries",
        "text": "textVersions",
        "titles": "titles",
    }

    async def _sub(resource: str) -> tuple[str, list]:
        try:
            return resource, await _paged(f"{base}/{resource}", key, fields[resource])
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "congress_gov: %s for %s unavailable: %s", resource, base, exc
            )
            return resource, []

    parts = dict(await asyncio.gather(*[_sub(r) for r in _SUB_RESOURCES]))

    subjects_block = parts.get("subjects") or []
    subjects_payload = subjects_block[0] if subjects_block else {}
    legislative_subjects = subjects_payload.get("legislativeSubjects") or []
    policy_area = (bill.get("policyArea") or {}).get("name") or (
        subjects_payload.get("policyArea") or {}
    ).get("name")

    titles = []
    for title in parts.get("titles") or []:
        entry = dict(title)
        entry.setdefault("type", entry.get("titleType") or "")
        titles.append(entry)

    return {
        "congress": int(bill.get("congress") or congress),
        "number": int(bill.get("number") or number),
        "type": bill.get("type") or bill_type.upper(),
        "bill_id": bill_id(congress, bt, number),
        "originChamber": bill.get("originChamber") or "",
        "originChamberCode": bill.get("originChamberCode") or "",
        "title": bill.get("title") or "",
        "introducedDate": bill.get("introducedDate") or "",
        "updateDate": bill.get("updateDate") or "",
        "updateDateIncludingText": bill.get("updateDateIncludingText") or "",
        "latestAction": _latest_action(bill),
        "policyArea": {"name": policy_area or ""},
        "sponsors": bill.get("sponsors") or [],
        "cosponsors": _cosponsors(parts.get("cosponsors") or []),
        "actions": parts.get("actions") or [],
        "committees": _committees(parts.get("committees") or []),
        "relatedBills": parts.get("relatedbills") or [],
        "subjects": legislative_subjects,
        "titles": titles,
        "summaries": parts.get("summaries") or [],
        "textVersions": _text_versions(parts.get("text") or []),
        "amendments": parts.get("amendments") or [],
        "_detailed": True,
    }
