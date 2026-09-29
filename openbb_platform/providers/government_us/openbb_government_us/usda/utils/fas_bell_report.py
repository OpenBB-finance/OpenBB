"""USDA FAS Bell Report fetching."""

import re
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any
from urllib.parse import urlencode

REPORT_HOST = "apps.fas.usda.gov"
BASE_URL = f"https://{REPORT_HOST}/esrqs/"
API_URL = f"{BASE_URL}api/"
TOKEN_URL = f"{BASE_URL}token"
PUBLIC_CLIENT_ID = "eAuth_Client"
PUBLIC_CLIENT_SECRET = (
    "00000000-0000-0000-0000-00000000000000000000-0000-0000-0000-000000000000"  # noqa: S105
)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/126 Safari/537.36"
)

REPORT_NAMES = {"my1": "BR", "my2": "BRMY2", "my3": "BRMY3"}
YEAR_AGO_DAYS = 364
PUBLISHED_STATUS_ID = 2
EMPTY_REPORT_MARKER = "Outstanding Export Sales"

SESSION_PATTERN = re.compile(r"ReportSession=([A-Za-z0-9]+)")
CONTROL_PATTERN = re.compile(r"ControlID=([A-Za-z0-9]+)")

_TOKEN: dict[str, Any] = {}


def year_ago_date(week_ending: dateType) -> dateType:
    """Derive the year-ago period ending date, preserving the weekday.

    Parameters
    ----------
    week_ending : dateType
        The period ending date.

    Returns
    -------
    dateType
        The date 52 weeks earlier, which is what the source publishes as the
        year-ago comparison.
    """
    return week_ending - timedelta(days=YEAR_AGO_DAYS)


def format_date(value: dateType) -> str:
    """Format a date as MM/DD/YYYY, the only format the report accepts."""
    return value.strftime("%m/%d/%Y")


async def get_token() -> str:
    """Get an anonymous bearer token for the ESR API.

    Returns
    -------
    str
        The access token, cached until it expires.

    Raises
    ------
    OpenBBError
        If the token endpoint does not return an access token.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request

    now = datetime.now().timestamp()
    if _TOKEN and _TOKEN["expires_at"] > now:
        return _TOKEN["access_token"]

    payload = urlencode(
        {
            "client_id": PUBLIC_CLIENT_ID,
            "client_secret": PUBLIC_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
    )
    response = await amake_request(
        TOKEN_URL,
        method="POST",
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
    )
    if not isinstance(response, dict) or "access_token" not in response:
        raise OpenBBError(f"FAS token request failed -> {response}")
    _TOKEN.update(
        {
            "access_token": response["access_token"],
            "expires_at": now + int(response.get("expires_in", 0)) - 60,
        }
    )
    return _TOKEN["access_token"]


async def get_lookup(path: str, authorize: bool = True, timeout: int = 120) -> Any:
    """Fetch an ESR API lookup.

    Parameters
    ----------
    path : str
        Path under the API base, e.g. 'lookups/Commodities'.
    authorize : bool
        Whether to attach the bearer token. The commodity list is public.
    timeout : int
        Seconds to wait. GetWeekEndingDates returns several megabytes, so the
        default is well above the platform's ten second default.

    Returns
    -------
    Any
        The decoded JSON response.
    """
    from openbb_core.provider.utils.helpers import amake_request

    headers = {"User-Agent": USER_AGENT}
    if authorize:
        headers["Authorization"] = f"Bearer {await get_token()}"
    return await amake_request(f"{API_URL}{path}", headers=headers, timeout=timeout)


async def get_commodities() -> list[dict]:
    """Get the commodity list, mapping the published code to the report's id.

    Returns
    -------
    list[dict]
        Records with id, commodity_code, and commodity_name keys, sorted by
        commodity code.
    """
    rows = await get_lookup("lookups/Commodities", authorize=False)
    return sorted(
        (
            {
                "id": row["id"],
                "commodity_code": row["commodityCode"],
                "commodity_name": row["commodityName"].strip(),
            }
            for row in rows or []
        ),
        key=lambda row: row["commodity_code"],
    )


async def get_published_weeks() -> list[dict]:
    """Get the published period ending dates and their release timestamps.

    Returns
    -------
    list[dict]
        Records with week_ending and released_at keys for weeks the source
        has published, newest first. Unpublished weeks are excluded so an
        embargoed report is never requested.
    """
    rows = await get_lookup("lookups/GetWeekEndingDates")
    weeks = [
        {
            "week_ending": datetime.fromisoformat(row["weekEndingDate"]).date(),
            "released_at": (
                datetime.fromisoformat(row["publishedDatetime"])
                if row.get("publishedDatetime")
                else None
            ),
        }
        for row in rows or []
        if row.get("weekEndingDateStatusId") == PUBLISHED_STATUS_ID
        and row.get("publishedDatetime")
    ]
    return sorted(weeks, key=lambda row: row["week_ending"], reverse=True)


async def _get_session():
    """Return an aiohttp session that keeps the report viewer's cookies."""
    from openbb_core.provider.utils.helpers import get_async_requests_session

    return await get_async_requests_session()


def build_report_url(
    report: str,
    week_ending: dateType,
    release_date: dateType,
    commodity_ids: list[int],
) -> str:
    """Build the ReportsHome URL that opens a Bell Report session.

    Parameters
    ----------
    report : str
        One of my1, my2, or my3.
    week_ending : dateType
        The period ending date.
    release_date : dateType
        The date the report was released.
    commodity_ids : list[int]
        Commodity ids, which are not the published commodity codes.

    Returns
    -------
    str
        The ReportsHome URL.
    """
    params: dict[str, Any] = {
        "RN": REPORT_NAMES[report],
        "wed": format_date(week_ending),
    }
    if report == "my1":
        params["YGO"] = format_date(year_ago_date(week_ending))
    params["RD"] = format_date(release_date)
    params["MY"] = "N"
    params["CID"] = "".join(f"{i}," for i in commodity_ids)
    params["AppUserId"] = 0
    return f"{BASE_URL}ReportsHome.aspx?{urlencode(params)}"


def report_from_url(url: str) -> str:
    """Return the marketing year report a ReportsHome URL addresses.

    Parameters
    ----------
    url : str
        A ReportsHome URL.

    Returns
    -------
    str
        One of my1, my2, or my3.

    Raises
    ------
    OpenBBError
        If the URL does not address the FAS report viewer, or names an
        unknown report.
    """
    from urllib.parse import parse_qs, urlparse

    from openbb_core.app.model.abstract.error import OpenBBError

    parsed = urlparse(url)
    if parsed.netloc != REPORT_HOST or not parsed.path.endswith("ReportsHome.aspx"):
        raise OpenBBError(
            f"Invalid Bell Report URL -> {url}."
            f" Expected a {REPORT_HOST} report viewer URL."
        )
    name = (parse_qs(parsed.query).get("RN") or [""])[0]
    for report, report_name in REPORT_NAMES.items():
        if report_name == name:
            return report
    raise OpenBBError(f"Unknown Bell Report -> '{name}' in {url}.")


def report_file_name(url: str) -> str:
    """Build a descriptive PDF file name for a ReportsHome URL."""
    from urllib.parse import parse_qs, urlparse

    params = parse_qs(urlparse(url).query)
    report = report_from_url(url)
    week = (params.get("wed") or [""])[0].replace("/", "")
    codes = "_".join(i for i in (params.get("CID") or [""])[0].split(",") if i)
    return f"bell_report_{report}_{codes}_{week}.pdf"


def build_export_url(session_id: str, control_id: str, file_name: str) -> str:
    """Build the report viewer export URL that returns the PDF."""
    return f"{BASE_URL}Reserved.ReportViewerWebControl.axd?" + urlencode(
        {
            "ReportSession": session_id,
            "Culture": 1033,
            "CultureOverrides": "True",
            "UICulture": 1033,
            "UICultureOverrides": "True",
            "ReportStack": 1,
            "ControlID": control_id,
            "OpType": "Export",
            "FileName": file_name,
            "ContentDisposition": "OnlyHtmlInline",
            "Format": "PDF",
        }
    )


async def afetch_report(url: str) -> bytes:
    """Fetch a Bell Report as PDF bytes from its report viewer URL.

    The report viewer binds its session to a cookie, so the session-opening
    request and the export request share one session.

    Parameters
    ----------
    url : str
        A ReportsHome URL, as built by ``build_report_url``.

    Returns
    -------
    bytes
        The PDF content.

    Raises
    ------
    OpenBBError
        If the report session cannot be opened or the export is not a PDF.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    report = report_from_url(url)
    session = await _get_session()
    try:
        response = await session.get(url, headers={"User-Agent": USER_AGENT})
        html = await response.text()
        session_match = SESSION_PATTERN.search(html)
        control_match = CONTROL_PATTERN.search(html)
        if not (session_match and control_match):
            raise OpenBBError(
                f"The FAS report viewer did not open a session for {url}."
            )
        export_url = build_export_url(
            session_match.group(1), control_match.group(1), f"Bell{report.upper()}"
        )
        response = await session.get(export_url, headers={"User-Agent": USER_AGENT})
        content = await response.read()
    finally:
        await session.close()

    if not content.startswith(b"%PDF"):
        raise OpenBBError(
            f"The FAS report viewer returned {len(content)} bytes that are not a PDF."
        )
    return content
