"""Congressional Committees Utilities."""

# pylint: disable=C0302,R0914,R0917

from openbb_congress_gov.utils.constants import base_url
from openbb_core.app.model.abstract.error import OpenBBError

_CONGRESS_GOV_TO_THOMAS_ID: dict[str, str] = {
    "JJEC": "JSEC",
    "JHJE": "JSEC",
}

_GOVTRACK_DATA_CACHE: dict[str, object] = {}


def _system_code_to_thomas_id(system_code: str) -> str:
    """Convert a Congress.gov committee systemCode to a govtrack/unitedstates thomas_id.

    Examples
    --------
    ssaf00 -> SSAF   (full committee, trailing '00' stripped)
    ssaf13 -> SSAF13 (subcommittee, non-zero suffix kept)
    hsag00 -> HSAG
    hsag03 -> HSAG03
    hzgo34 -> HZGO34 (task forces: not in external datasets, returns empty)
    jjec00 -> JSEC   (Joint Economic Committee - Congress.gov/govtrack code mismatch)
    jhje00 -> JSEC   (Joint Economic Committee - House side variant)
    """
    code = system_code.upper()

    if code.endswith("00"):
        base = code[:-2]
        return _CONGRESS_GOV_TO_THOMAS_ID.get(base, base)

    return code


async def get_committee_members(system_code: str) -> list:
    """Fetch current committee members from unitedstates/congress-legislators.

    Data source:
    - https://unitedstates.github.io/congress-legislators/committee-membership-current.json

    Parameters
    ----------
    system_code : str
        The Congress.gov committee systemCode (e.g., 'ssaf00', 'hsag00').

    Returns
    -------
    list[dict]
        Each dict has: name, party ("majority"/"minority"), rank, title, bioguide.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    thomas_id = _system_code_to_thomas_id(system_code)

    if "committee_membership" not in _GOVTRACK_DATA_CACHE:
        url = (
            "https://unitedstates.github.io/congress-legislators/"
            "committee-membership-current.json"
        )
        try:
            data = await amake_request(url, timeout=30)
        except Exception:
            return []

        if not isinstance(data, dict):
            return []

        _GOVTRACK_DATA_CACHE["committee_membership"] = data

    membership: dict = _GOVTRACK_DATA_CACHE["committee_membership"]  # type: ignore

    return membership.get(thomas_id, [])


async def _committee_docs_detail_fetch(
    url: str, api_key: str, sem, session=None
) -> dict | None:
    """Fetch a single detail endpoint, respecting a shared semaphore.

    Retries up to 3 times with exponential backoff on rate-limit responses.

    Parameters
    ----------
    url : str
        The detail endpoint URL.
    api_key : str
        The congress.gov API key.
    sem : asyncio.Semaphore
        Shared concurrency limiter.
    session : optional
        Cached aiohttp session.

    Returns
    -------
    dict | None
        The JSON response dict, or None on failure.
    """
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    sep = "&" if "?" in url else "?"
    full_url = f"{url}{sep}format=json&api_key={api_key}"
    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    for attempt in range(4):
        async with sem:
            try:
                resp = await amake_request(full_url, timeout=15, **kwargs)
            except Exception:
                return None

        if not isinstance(resp, dict):
            return None

        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            if attempt < 3:
                await asyncio.sleep(2**attempt)
                continue

            return None

        return resp

    return None


def _witness_label(url: str) -> str:
    """Derive a human-readable label from a witness document PDF URL."""
    filename = url.rsplit("/", 1)[-1].replace(".pdf", "")
    parts = filename.split("-")

    if len(parts) >= 6 and len(parts[-1]) == 8 and parts[-1].isdigit():
        kind = parts[-3]
        name_part = parts[-2]
    elif len(parts) >= 5:
        kind = parts[-2]
        name_part = parts[-1]
    else:
        return filename

    if kind.startswith("Wstate"):
        return f"Testimony \u2014 {name_part}"

    if kind.startswith("Bio"):
        return f"Bio \u2014 {name_part}"

    return f"{kind} \u2014 {name_part}"


async def _fetch_committee_legislation(
    chamber: str, system_code: str, congress: int, api_key: str, session=None
) -> list[dict]:
    """Fetch legislation PDFs associated with a committee."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    _intro_suffix = {
        "hr": "ih",
        "hres": "ih",
        "hjres": "ih",
        "hconres": "ih",
        "s": "is",
        "sres": "is",
        "sjres": "is",
        "sconres": "is",
    }

    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    bills_base = f"{base_url}committee/{chamber}/{system_code}/bills"
    first_url = f"{bills_base}?format=json&limit=250&offset=0&api_key={api_key}"
    resp = await amake_request(first_url, timeout=20, **kwargs)
    all_bills: list[dict] = []

    if isinstance(resp, dict):
        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            raise OpenBBError(
                ValueError(
                    "Congress.gov API rate limit exceeded. Please wait a moment and try again."
                )
            )

        cb = resp.get("committee-bills", {})
        all_bills = list(cb.get("bills", []) if isinstance(cb, dict) else [])
        total = resp.get("pagination", {}).get("count", 0)

        if total > 250 and all_bills:
            remaining_urls = [
                f"{bills_base}?format=json&limit=250&offset={off}&api_key={api_key}"
                for off in range(250, total, 250)
            ]
            page_sem = asyncio.Semaphore(10)

            async def _fetch_bills_page(page_url: str) -> list[dict]:
                async with page_sem:
                    try:
                        r = await amake_request(page_url, timeout=20, **kwargs)
                    except Exception:
                        return []

                    if not isinstance(r, dict):
                        return []

                    cb2 = r.get("committee-bills", {})

                    return list(cb2.get("bills", []) if isinstance(cb2, dict) else [])

            pages = await asyncio.gather(
                *[_fetch_bills_page(u) for u in remaining_urls]
            )

            for page in pages:
                all_bills.extend(page)

    matched = [b for b in all_bills if b.get("congress") == congress]
    matched = matched[:200]

    items: list[dict] = []

    for b in matched:
        bill_type = b.get("type", "")
        bill_number = b.get("number", "")
        relationship = b.get("relationshipType", "")

        if not bill_type or not bill_number:
            continue

        type_lower = bill_type.lower()
        suffix = _intro_suffix.get(type_lower)

        if not suffix:
            continue

        pdf_url = (
            f"https://www.congress.gov/{congress}/bills/"
            f"{type_lower}{bill_number}/BILLS-{congress}{type_lower}{bill_number}{suffix}.pdf"
        )
        title = b.get("title") or f"{bill_type} {bill_number}"
        citation = f"{bill_type} {bill_number}"

        if relationship:
            title = f"{title} ({relationship})"

        action_date = b.get("actionDate", "")

        if action_date:
            date_str = action_date[:10]
            title = f"[{date_str}] {title}"

        items.append(
            {
                "doc_type": "legislation",
                "citation": citation or None,
                "title": title,
                "congress": congress,
                "chamber": chamber.title(),
                "doc_url": pdf_url,
            }
        )

    return items


async def _fetch_meeting_documents(
    congress: int, chamber: str, event_id: str, api_key: str, sem, session=None
) -> list[dict]:
    """Fetch all documents for a committee meeting."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    url = (
        f"{base_url}committee-meeting/{congress}"
        f"/{'nochamber' if chamber.lower() == 'joint' else chamber}/{event_id}"
        f"?format=json&api_key={api_key}"
    )
    resp = None

    for attempt in range(4):
        async with sem:
            try:
                resp = await amake_request(url, timeout=20, **kwargs)
            except Exception:
                return []

        if (
            isinstance(resp, dict)
            and resp.get("error", {}).get("code") == "OVER_RATE_LIMIT"
        ):
            if attempt < 3:
                await asyncio.sleep(2**attempt)
                continue

            return []

        break

    if not isinstance(resp, dict):
        return []

    meeting = resp.get("committeeMeeting", resp)
    title = meeting.get("title", "")
    raw_date = meeting.get("date", "")
    date_prefix = f"[{raw_date[:10]}] " if raw_date else ""
    event_codes = {c.get("systemCode", "") for c in meeting.get("committees", [])}
    items: list[dict] = []

    for wd in meeting.get("witnessDocuments", []):
        pdf_url = wd.get("url", "")

        if not pdf_url or wd.get("format") != "PDF":
            continue

        witness = _witness_label(pdf_url)
        label = (
            f"{date_prefix}{witness} \u2014 {title}"
            if title
            else f"{date_prefix}{witness}"
        )
        items.append(
            {
                "doc_type": "meeting",
                "citation": None,
                "title": label,
                "congress": congress,
                "chamber": chamber.title(),
                "doc_url": pdf_url,
                "_committee_codes": event_codes,
            }
        )

    for md in meeting.get("meetingDocuments", []):
        pdf_url = md.get("url", "")

        if not pdf_url or md.get("format") != "PDF":
            continue

        doc_name = md.get("name") or md.get("documentType", "")
        label = (
            f"{date_prefix}{doc_name} \u2014 {title}"
            if doc_name
            else f"{date_prefix}{title}"
        )
        items.append(
            {
                "doc_type": "meeting",
                "citation": None,
                "title": label,
                "congress": congress,
                "chamber": chamber.title(),
                "doc_url": pdf_url,
                "_committee_codes": event_codes,
            }
        )

    return items


async def _resolve_committee_name(
    chamber: str, system_code: str, api_key: str, session=None
) -> str | None:
    """Resolve a committee's libraryOfCongressName from its system code."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}
    if session is not None:
        kwargs["session"] = session

    is_sub = len(system_code) > 4 and not system_code.endswith("00")
    lookup_code = system_code[: len(system_code) - 2] + "00" if is_sub else system_code

    url = f"{base_url}committee/{chamber}/{lookup_code}?format=json&api_key={api_key}"
    try:
        resp = await amake_request(url, timeout=15, **kwargs)
    except Exception:
        return None

    if not isinstance(resp, dict):
        return None

    committee = resp.get("committee", {})

    if is_sub:
        for sc in committee.get("subcommittees", []):
            if sc.get("systemCode") == system_code:
                return sc.get("name")

    for h in committee.get("history", []):
        return h.get("libraryOfCongressName") or h.get("officialName", "")

    return committee.get("name")


async def _fetch_meetings_via_search(
    chamber: str,
    system_code: str,
    congress: int,
    api_key: str,
    sem,
    session=None,
) -> list[dict]:
    """Fetch meeting/hearing documents using congress.gov search for discovery.

    Step 1: Use search to get the filtered list of event IDs for this committee
            (replaces the broken "list ALL meetings and filter by code" approach).
    Step 2: Skip future-dated events (they have no documents yet).
    Step 3: Fetch API detail for each past event to extract witness/meeting document PDFs.
    Step 4: For past events with no attached PDFs, return the event page URL as fallback.
    """
    # pylint: disable=import-outside-toplevel
    import asyncio
    import re
    from datetime import datetime

    from openbb_congress_gov.utils.congress_search import search_async
    from openbb_core.provider.utils.helpers import amake_request

    committee_name = await _resolve_committee_name(
        chamber, system_code, api_key, session
    )
    if not committee_name:
        return []

    results = await search_async(
        congress=congress,
        sources=["committee-meetings"],
        committee=committee_name,
        chamber=chamber.lower(),  # type: ignore
    )
    if not results:
        return []

    today = datetime.now().date()
    event_pattern = re.compile(r"(?:senate|house|joint)-event/(\d+)")
    event_ids: list[str] = []
    search_meta: dict[str, dict] = {}

    for r in results:
        url = r.get("url", "")
        m = event_pattern.search(url)
        if not m:
            continue

        raw_date = r.get("date", "")
        if raw_date:
            date_part = raw_date.split("\u2014")[0].strip()
            try:
                event_date = datetime.strptime(date_part, "%B %d, %Y").date()
                if event_date > today:
                    continue
            except ValueError:
                pass

        eid = m.group(1)
        if eid not in search_meta:
            event_ids.append(eid)
            search_meta[eid] = r

    if not event_ids:
        return []

    kwargs: dict = {}
    if session is not None:
        kwargs["session"] = session

    api_chamber = "nochamber" if chamber.lower() == "joint" else chamber
    items: list[dict] = []

    async def _process_event(eid: str):
        detail_url = (
            f"{base_url}committee-meeting/{congress}/{api_chamber}/{eid}"
            f"?format=json&api_key={api_key}"
        )
        resp = None
        for attempt in range(4):
            async with sem:
                try:
                    resp = await amake_request(detail_url, timeout=20, **kwargs)
                except Exception:
                    break
            if (
                isinstance(resp, dict)
                and resp.get("error", {}).get("code") == "OVER_RATE_LIMIT"
            ):
                if attempt < 3:
                    await asyncio.sleep(2**attempt)
                    continue
                break
            break

        if not isinstance(resp, dict):
            return

        meeting = resp.get("committeeMeeting", resp)
        title = meeting.get("title", "")
        raw_date = meeting.get("date", "")
        date_prefix = f"[{raw_date[:10]}] " if raw_date else ""

        event_codes = {c.get("systemCode", "") for c in meeting.get("committees", [])}

        for wd in meeting.get("witnessDocuments", []):
            pdf_url = wd.get("url", "")
            if not pdf_url or wd.get("format") != "PDF":
                continue
            witness = _witness_label(pdf_url)
            label = (
                f"{date_prefix}{witness} \u2014 {title}"
                if title
                else f"{date_prefix}{witness}"
            )
            items.append(
                {
                    "doc_type": "meeting",
                    "citation": None,
                    "title": label,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                    "_committee_codes": event_codes,
                }
            )

        ch_prefix = {"house": "h", "senate": "s"}.get(chamber.lower(), "j")
        for ht in meeting.get("hearingTranscript", []):
            jn = ht.get("jacketNumber")
            if not jn:
                continue
            pkg = f"CHRG-{congress}{ch_prefix}hrg{jn}"
            pdf_url = f"https://www.govinfo.gov/content/pkg/{pkg}/pdf/{pkg}.pdf"
            label = f"{date_prefix}{title}" if title else f"{date_prefix}Hearing {jn}"
            items.append(
                {
                    "doc_type": "meeting",
                    "citation": None,
                    "title": label,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                    "_committee_codes": event_codes,
                }
            )

    await asyncio.gather(
        *[_process_event(eid) for eid in event_ids],
        return_exceptions=True,
    )

    return items


async def _fetch_meetings_via_listing(
    chamber: str,
    system_code: str,
    parent_code: str,
    congress: int,
    api_key: str,
    sem,
    session=None,
) -> list[dict]:
    """Fetch meeting documents by listing committee-meeting endpoint directly."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}
    if session is not None:
        kwargs["session"] = session

    api_chamber = "nochamber" if chamber.lower() == "joint" else chamber
    url = (
        f"{base_url}committee-meeting/{congress}/{api_chamber}"
        f"?format=json&limit=250&api_key={api_key}"
    )
    all_event_ids: list[str] = []

    while url:
        async with sem:
            try:
                resp = await amake_request(url, timeout=20, **kwargs)
            except Exception:
                break

        if not isinstance(resp, dict):
            break

        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            await asyncio.sleep(2)
            continue

        for m in resp.get("committeeMeetings", []):
            eid = m.get("eventId")
            if eid:
                all_event_ids.append(str(eid))

        next_url = resp.get("pagination", {}).get("next")
        if not next_url:
            break

        url = f"{next_url}&format=json&api_key={api_key}"
        await asyncio.sleep(0.2)

    if not all_event_ids:
        return []

    items: list[dict] = []
    target_codes = {system_code, parent_code}

    async def _process_meeting(eid: str):
        detail_url = (
            f"{base_url}committee-meeting/{congress}/{api_chamber}/{eid}"
            f"?format=json&api_key={api_key}"
        )
        resp = None
        for attempt in range(3):
            async with sem:
                try:
                    resp = await amake_request(detail_url, timeout=20, **kwargs)
                except Exception:
                    return
            if (
                isinstance(resp, dict)
                and resp.get("error", {}).get("code") == "OVER_RATE_LIMIT"
            ):
                await asyncio.sleep(2**attempt)
                continue
            break
        else:
            return

        if not isinstance(resp, dict):
            return

        meeting = resp.get("committeeMeeting", {})
        codes = {c.get("systemCode", "") for c in meeting.get("committees", [])}
        if not codes & target_codes:
            return

        title = meeting.get("title", "")
        raw_date = meeting.get("date", "")
        date_prefix = f"[{raw_date[:10]}] " if raw_date else ""

        for wd in meeting.get("witnessDocuments", []):
            pdf_url = wd.get("url", "")
            if not pdf_url or wd.get("format") != "PDF":
                continue
            witness = _witness_label(pdf_url)
            label = (
                f"{date_prefix}{witness} \u2014 {title}"
                if title
                else f"{date_prefix}{witness}"
            )
            items.append(
                {
                    "doc_type": "meeting",
                    "citation": None,
                    "title": label,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                }
            )

        for md in meeting.get("meetingDocuments", []):
            pdf_url = md.get("url", "")
            if not pdf_url or md.get("format") != "PDF":
                continue
            doc_name = md.get("name") or md.get("documentType", "")
            label = (
                f"{date_prefix}{doc_name} \u2014 {title}"
                if doc_name
                else f"{date_prefix}{title}"
            )
            items.append(
                {
                    "doc_type": "meeting",
                    "citation": None,
                    "title": label,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                }
            )

    await asyncio.gather(
        *[_process_meeting(eid) for eid in all_event_ids],
        return_exceptions=True,
    )

    return items


async def _fetch_reports_via_api(
    chamber: str, system_code: str, congress: int, api_key: str, sem, session=None
) -> list[dict]:
    """Fetch reports for a committee via the committee-specific reports endpoint."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    matched: list[dict] = []
    url = (
        f"{base_url}committee/{chamber}/{system_code}/reports"
        f"?format=json&limit=250&api_key={api_key}"
    )

    while url:
        async with sem:
            try:
                resp = await amake_request(url, timeout=20, **kwargs)
            except Exception:
                break

        if not isinstance(resp, dict):
            break

        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            await asyncio.sleep(2)
            continue

        for rpt in resp.get("reports", []):
            if rpt.get("congress") != congress:
                continue

            matched.append(rpt)

        next_url = resp.get("pagination", {}).get("next")

        if not next_url:
            break

        has_target = False

        for rpt in resp.get("reports", []):
            if rpt.get("congress", 0) <= congress:
                has_target = True
                break

        if not has_target:
            break

        url = f"{next_url}&format=json&api_key={api_key}"
        await asyncio.sleep(0.2)

    if not matched:
        return []

    async def _fetch_report_detail(rpt: dict) -> dict | None:
        citation = rpt.get("citation", "")
        rpt_type = rpt.get("type", "")
        number = rpt.get("number")
        part = rpt.get("part", 1)

        if not number or not rpt_type:
            return None

        type_lower = rpt_type.lower()
        base = f"CRPT-{congress}{type_lower}{number}"

        if ",Part" in citation:
            pdf_url = f"https://www.congress.gov/{congress}/crpt/{type_lower}{number}/{base}-pt{part}.pdf"
        else:
            pdf_url = f"https://www.congress.gov/{congress}/crpt/{type_lower}{number}/{base}.pdf"

        detail_url = (
            f"{base_url}committee-report/{congress}/{rpt_type}/{number}"
            f"?format=json&api_key={api_key}"
        )
        title = citation
        issue_date = ""

        async with sem:
            try:
                detail = await amake_request(detail_url, timeout=20, **kwargs)
            except Exception:
                detail = None

        if isinstance(detail, dict):
            for cr in detail.get("committeeReports", []):
                title = cr.get("title") or citation
                issue_date = (cr.get("issueDate") or "")[:10]
                break

        if issue_date:
            title = f"[{issue_date}] {title}"

        return {
            "doc_type": "report",
            "citation": citation or None,
            "title": title,
            "congress": congress,
            "chamber": chamber.title(),
            "doc_url": pdf_url,
        }

    results = await asyncio.gather(
        *[_fetch_report_detail(r) for r in matched],
        return_exceptions=True,
    )

    return [r for r in results if isinstance(r, dict)]


async def _fetch_hearings_via_api(
    chamber: str,
    system_code: str,
    parent_code: str,
    congress: int,
    api_key: str,
    sem,
    session=None,
) -> list[dict]:
    """Fetch hearing documents for a committee via the hearing API.

    Lists all hearings for the congress/chamber, fetches details concurrently,
    filters by committee systemCode, and extracts PDF URLs + associated meeting docs.
    """
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    all_jacket_numbers: list[int] = []
    api_chamber = "nochamber" if chamber.lower() == "joint" else chamber
    url = (
        f"{base_url}hearing/{congress}/{api_chamber}"
        f"?format=json&limit=250&api_key={api_key}"
    )

    while url:
        async with sem:
            try:
                resp = await amake_request(url, timeout=20, **kwargs)
            except Exception:
                break

        if not isinstance(resp, dict):
            break

        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            await asyncio.sleep(2)
            continue

        for h in resp.get("hearings", []):
            jn = h.get("jacketNumber")

            if jn:
                all_jacket_numbers.append(jn)

        next_url = resp.get("pagination", {}).get("next")

        if not next_url:
            break

        url = f"{next_url}&format=json&api_key={api_key}"
        await asyncio.sleep(0.2)

    items: list[dict] = []
    meeting_event_ids: list[str] = []

    async def _process_hearing(jn: int):
        detail_url = (
            f"{base_url}hearing/{congress}/{api_chamber}/{jn}"
            f"?format=json&api_key={api_key}"
        )

        for attempt in range(3):
            async with sem:
                try:
                    resp = await amake_request(detail_url, timeout=20, **kwargs)
                except Exception:
                    return
            if (
                isinstance(resp, dict)
                and resp.get("error", {}).get("code") == "OVER_RATE_LIMIT"
            ):
                await asyncio.sleep(2**attempt)
                continue

            break

        else:
            return

        if not isinstance(resp, dict):
            return

        hearing = resp.get("hearing", {})
        committees = hearing.get("committees", [])
        codes = {c.get("systemCode", "") for c in committees}

        if not codes & {system_code, parent_code}:
            return

        title = hearing.get("title", "")
        hearing_dates = hearing.get("dates", [])
        hearing_date = hearing_dates[0].get("date", "") if hearing_dates else ""
        if hearing_date:
            title = f"[{hearing_date}] {title}"

        if system_code in codes:
            pdf_url = ""
            for fmt in hearing.get("formats", []):
                if fmt.get("type") == "PDF":
                    pdf_url = fmt.get("url", "")
                    break
            if not pdf_url:
                ch_prefix = {"house": "h", "senate": "s"}.get(chamber.lower(), "j")
                pkg = f"CHRG-{congress}{ch_prefix}hrg{jn}"
                pdf_url = f"https://www.govinfo.gov/content/pkg/{pkg}/pdf/{pkg}.pdf"
            items.append(
                {
                    "doc_type": "hearing",
                    "citation": hearing.get("citation"),
                    "title": title,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                    "_committee_codes": codes,
                }
            )

        assoc = hearing.get("associatedMeeting", {})
        event_id = assoc.get("eventId")

        if event_id:
            meeting_event_ids.append(event_id)

    await asyncio.gather(
        *[_process_hearing(jn) for jn in all_jacket_numbers],
        return_exceptions=True,
    )

    if meeting_event_ids:
        meeting_results = await asyncio.gather(
            *[
                _fetch_meeting_documents(congress, chamber, eid, api_key, sem, session)
                for eid in meeting_event_ids
            ],
            return_exceptions=True,
        )

        for result in meeting_results:
            if isinstance(result, list):
                items.extend(result)

    return items


async def _fetch_prints_via_api(
    chamber: str,
    system_code: str,
    congress: int,
    api_key: str,
    sem,
    session=None,
) -> list[dict]:
    """Fetch committee prints filtered by committee systemCode."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import amake_request

    kwargs: dict = {}

    if session is not None:
        kwargs["session"] = session

    all_print_urls: list[str] = []
    url = (
        f"{base_url}committee-print/{congress}/{chamber}"
        f"?format=json&limit=250&api_key={api_key}"
    )

    while url:
        async with sem:
            try:
                resp = await amake_request(url, timeout=20, **kwargs)
            except Exception:
                break

        if not isinstance(resp, dict):
            break

        if resp.get("error", {}).get("code") == "OVER_RATE_LIMIT":
            await asyncio.sleep(2)
            continue

        for p in resp.get("committeePrints", []):
            detail_url = p.get("url")

            if detail_url:
                all_print_urls.append(detail_url)

        next_url = resp.get("pagination", {}).get("next")

        if not next_url:
            break

        url = f"{next_url}&format=json&api_key={api_key}"
        await asyncio.sleep(0.2)

    items: list[dict] = []

    async def _process_print(detail_url: str):
        full_url = f"{detail_url}?format=json&api_key={api_key}"

        for attempt in range(3):
            async with sem:
                try:
                    resp = await amake_request(full_url, timeout=20, **kwargs)
                except Exception:
                    return

            if (
                isinstance(resp, dict)
                and resp.get("error", {}).get("code") == "OVER_RATE_LIMIT"
            ):
                await asyncio.sleep(2**attempt)
                continue
            break
        else:
            return

        if not isinstance(resp, dict):
            return

        for cp in resp.get("committeePrint", []):
            committees = cp.get("committees", [])
            codes = {c.get("systemCode", "") for c in committees}

            if system_code not in codes:
                continue

            title = cp.get("title", "")
            citation = cp.get("citation", "")
            jn = cp.get("jacketNumber")

            if not jn:
                continue

            ch_prefix = {"house": "H", "senate": "S"}.get(chamber.lower(), "J")
            pkg = f"CPRT-{congress}{ch_prefix}PRT{jn}"
            pdf_url = f"https://www.govinfo.gov/content/pkg/{pkg}/pdf/{pkg}.pdf"

            items.append(
                {
                    "doc_type": "publication",
                    "citation": citation or None,
                    "title": title,
                    "congress": congress,
                    "chamber": chamber.title(),
                    "doc_url": pdf_url,
                }
            )

    await asyncio.gather(
        *[_process_print(u) for u in all_print_urls],
        return_exceptions=True,
    )

    return items


async def fetch_committee_documents(
    chamber: str,
    system_code: str,
    congress: int,
    doc_type: str,
    api_key: str,
    use_cache: bool = True,
) -> list[dict]:
    """Fetch documents for a committee using congress.gov API v3 endpoints.

    Uses:
    - committee/{chamber}/{code}/reports for committee reports
    - hearing/{congress}/{chamber} + detail for hearing PDFs & associated meetings
    - committee-print/{congress}/{chamber} + detail for committee prints
    - committee-meeting detail for witness docs, meeting docs, hearing transcripts
    - committee/{chamber}/{code}/bills for legislation

    All API responses are cached to SQLite (7-day TTL) to avoid redundant requests.
    """
    # pylint: disable=import-outside-toplevel
    import asyncio
    import logging

    from aiohttp_client_cache import SQLiteBackend
    from aiohttp_client_cache.session import CachedSession
    from openbb_core.app.utils import get_user_cache_directory

    logger = logging.getLogger(__name__)
    sem = asyncio.Semaphore(5)
    items: list[dict] = []

    is_subcommittee = len(system_code) > 4 and not system_code.endswith("00")
    parent_code = (
        system_code[: len(system_code) - 2] + "00" if is_subcommittee else system_code
    )
    api_code = parent_code if is_subcommittee else system_code

    if use_cache:
        cache_dir = f"{get_user_cache_directory()}/http/congress_gov"
        backend = SQLiteBackend(cache_dir, expire_after=3600 * 24 * 7)
        _session_ctx = CachedSession(cache=backend)
    else:
        import aiohttp

        _session_ctx = aiohttp.ClientSession()

    async with _session_ctx as session:
        if use_cache:
            await session.delete_expired_responses()  # type: ignore[union-attr]

        tasks = []

        if doc_type in ("all", "report"):
            tasks.append(
                (
                    "report",
                    _fetch_reports_via_api(
                        chamber, api_code, congress, api_key, sem, session
                    ),
                )
            )

        if doc_type in ("all", "hearing", "meeting"):
            tasks.append(
                (
                    "hearing",
                    _fetch_hearings_via_api(
                        chamber,
                        system_code,
                        parent_code,
                        congress,
                        api_key,
                        sem,
                        session,
                    ),
                )
            )

        if doc_type in ("all", "meeting"):
            tasks.append(
                (
                    "meeting",
                    _fetch_meetings_via_search(
                        chamber,
                        system_code,
                        congress,
                        api_key,
                        sem,
                        session,
                    ),
                )
            )

        if doc_type in ("all", "publication"):
            tasks.append(
                (
                    "print",
                    _fetch_prints_via_api(
                        chamber,
                        system_code,
                        congress,
                        api_key,
                        sem,
                        session,
                    ),
                )
            )

        if doc_type in ("all", "legislation"):
            tasks.append(
                (
                    "legislation",
                    _fetch_committee_legislation(
                        chamber, system_code, congress, api_key, session
                    ),
                )
            )

        if tasks:
            results = await asyncio.gather(
                *[t[1] for t in tasks],
                return_exceptions=True,
            )
            for (label, _), result in zip(tasks, results):
                if isinstance(result, list):
                    items.extend(result)
                elif isinstance(result, BaseException):
                    logger.warning("%s pipeline error: %s", label, result)

    seen_urls: set[str] = set()
    deduped: list[dict] = []

    for item in items:
        url = item.get("doc_url", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(item)

    if is_subcommittee:
        url_code = system_code[2:].upper()
        pattern = f"-{url_code}-"
        filtered: list[dict] = []
        for d in deduped:
            codes = d.get("_committee_codes")
            if codes is not None:
                if system_code in codes:
                    filtered.append(d)
            elif pattern in d.get("doc_url", ""):
                filtered.append(d)
        deduped = filtered

    for d in deduped:
        d.pop("_committee_codes", None)

    return deduped
