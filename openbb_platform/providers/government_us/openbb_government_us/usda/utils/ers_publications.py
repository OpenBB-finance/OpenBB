"""USDA ERS publications listing and full-report resolution."""

import re
from typing import Any
from urllib.parse import urlencode, urlparse

from openbb_government_us.usda.utils.ers_client import (
    BASE_URL,
    HEADING_PATTERN,
    LINK_PATTERN,
    get_cache,
)

API_URL = f"{BASE_URL}/api/publications/v1.0"
_MISSING = object()
PUBLICATION_HOST = "www.ers.usda.gov"
PUBLICATION_PATH = "/publications/"
MAX_ITEMS_PER_PAGE = 50
LISTING_TTL = 21600
REPORT_URL_TTL = 604800
REPORT_FILE_TTL = 604800
FULL_REPORT_HEADING = "full report"

SERIES_GROUPS: dict[str, list[str]] = {
    "outlook-reports": [
        "AES",
        "CWS",
        "FDS",
        "FTS",
        "GFA",
        "LDPM",
        "OCE",
        "OCS",
        "RCS",
        "SSSM",
        "TBS",
        "VGS",
        "WHS",
    ],
    "research-reports": ["AP", "CCR", "EB", "EIB", "ERR", "TB"],
    "discontinued-reports": [
        "AER",
        "AGES",
        "AH",
        "AIB",
        "AIS",
        "AR",
        "BIO",
        "BLA",
        "EFAN",
        "FANRR",
        "FAU",
        "IUS",
        "MP",
        "RA",
        "RDRR",
        "SB",
        "WAOB",
        "WRS",
    ],
}

SERIES_CODES: dict[str, str] = {
    "AES": "Outlook for U.S. Agricultural Trade",
    "CWS": "Cotton and Wool Outlook",
    "FDS": "Feed Outlook",
    "FTS": "Fruit and Tree Nuts Outlook",
    "GFA": "Food Security Assessment Situation and Outlook",
    "LDPM": "Livestock, Dairy, and Poultry Outlook",
    "OCE": "USDA Agricultural Projections",
    "OCS": "Oil Crops Outlook",
    "RCS": "Rice Outlook",
    "SSSM": "Sugar and Sweeteners Outlook",
    "TBS": "Tobacco Outlook",
    "VGS": "Vegetables and Pulses Outlook",
    "WHS": "Wheat Outlook",
    "AP": "Administrative Publication",
    "CCR": "Contractor and Cooperator Reports",
    "EB": "Economic Brief",
    "EIB": "Economic Information Bulletin",
    "ERR": "Economic Research Report",
    "TB": "Technical Bulletin",
    "AER": "Agricultural Economic Report",
    "AGES": "AGES",
    "AH": "Agricultural Handbook",
    "AIB": "Agricultural Information Bulletin",
    "AIS": "Agricultural Income and Finance Outlook",
    "AR": "Agricultural Resources Situation and Outlook",
    "BIO": "Bioenergy",
    "BLA": "Bibliographies and Literature of Agriculture",
    "EFAN": (
        "Electronic Publications from the Food Assistance & Nutrition Research Program"
    ),
    "FANRR": "Food Assistance & Nutrition Research Program",
    "FAU": "U.S. Agricultural Trade Update",
    "IUS": ("Industrial Uses of Agricultural Materials Situation and Outlook Report"),
    "MP": "Miscellaneous Publication",
    "RA": "Rural America",
    "RDRR": "Rural Development Research Report",
    "SB": "Statistical Bulletin",
    "WAOB": "WAOB",
    "WRS": "International Agriculture and Trade Outlook",
}

DOWNLOAD_BLOCK_PATTERN = re.compile(
    r'id="download".*?<ul\s+class="usa-collection">(.*?)</ul>',
    re.DOTALL,
)
PUBLICATION_ITEM_PATTERN = re.compile(
    r'<li\s+class="usa-collection__item[^>]*">.*?</li>',
    re.DOTALL,
)


def coerce_sentinel(value: Any) -> Any:
    """Coerce the API's literal int 0 placeholder to None.

    Parameters
    ----------
    value : Any
        A field the API types as a string or object, which it fills with the
        int 0 instead of null when the field is unset.

    Returns
    -------
    Any
        None when the value is the int 0 sentinel, otherwise the value.
    """
    if isinstance(value, bool):
        return value
    return None if isinstance(value, int) and value == 0 else value


def resolve_series(series: str | list[str]) -> list[str]:
    """Expand series groups to codes and reject anything unrecognized.

    Parameters
    ----------
    series : str | list[str]
        Group names, series codes, or a comma-separated string of either.

    Returns
    -------
    list[str]
        Deduplicated series codes, in the order first requested.

    Raises
    ------
    OpenBBError
        If a token is neither a known group nor a known series code. The API
        silently ignores an unknown series and returns the entire corpus, so
        an unvalidated token would masquerade as a successful query.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    tokens = series.split(",") if isinstance(series, str) else list(series)
    requested = [token.strip() for token in tokens if token and token.strip()]
    if not requested:
        raise OpenBBError(
            "No publication series requested. Valid groups are: "
            + ", ".join(sorted(SERIES_GROUPS))
        )
    codes: list[str] = []
    unknown: list[str] = []
    lookup = {code.casefold(): code for code in SERIES_CODES}
    for token in requested:
        group = SERIES_GROUPS.get(token.casefold())
        if group is not None:
            codes.extend(group)
            continue
        code = lookup.get(token.casefold())
        if code is None:
            unknown.append(token)
            continue
        codes.append(code)
    if unknown:
        raise OpenBBError(
            f"Invalid publication series: {', '.join(unknown)}."
            + " Valid groups are: "
            + ", ".join(sorted(SERIES_GROUPS))
            + ". Valid series codes are: "
            + ", ".join(sorted(SERIES_CODES))
        )
    return list(dict.fromkeys(codes))


def publication_page_url(row: dict) -> str:
    """Build the canonical publication page URL of a listing row.

    Parameters
    ----------
    row : dict
        A listing row, carrying the site-relative 'url' key.

    Returns
    -------
    str
        The https page URL. The row's own baseUrl is http and redirects, so
        the canonical https origin is used instead.
    """
    return f"{BASE_URL}{row['url']}"


def normalize_row(row: dict) -> dict:
    """Normalize a listing row, coercing every int 0 sentinel to None.

    Parameters
    ----------
    row : dict
        A raw listing row from the API.

    Returns
    -------
    dict
        A record whose optional fields are None rather than the int 0
        sentinel, with authors coerced per element.
    """
    series = coerce_sentinel(row.get("series"))
    series = series if isinstance(series, dict) else {}
    authors = [
        {
            "id": author.get("id"),
            "name": author.get("name"),
            "url": coerce_sentinel(author.get("url")),
        }
        for author in row.get("authors") or []
    ]
    image = coerce_sentinel(row.get("newsroomImage"))
    return {
        "id": row["id"],
        "title": row["title"],
        "release_date": row["releaseDate"],
        "series_code": coerce_sentinel(series.get("code")),
        "series_name": coerce_sentinel(series.get("name")),
        "series_full_name": coerce_sentinel(series.get("fullName")),
        "pub_type": coerce_sentinel(row.get("pubType")),
        "report_number": coerce_sentinel(row.get("reportNumber")),
        "url": publication_page_url(row),
        "authors": authors,
        "description": coerce_sentinel(row.get("description")),
        "short_description": coerce_sentinel(row.get("shortDescription")),
        "image_url": image.get("url") if isinstance(image, dict) else None,
        "topics": [
            topic.get("name") for topic in row.get("relatedTopics") or [] if topic
        ],
    }


def build_listing_url(code: str, page: int = 0) -> str:
    """Build the listing request URL for one series code and page.

    Parameters
    ----------
    code : str
        A single series code. Codes are paginated one at a time because a
        multi-code query has no deterministic tiebreak and both duplicates
        and drops rows across page boundaries.
    page : int
        Zero-based page index.

    Returns
    -------
    str
        The listing URL.
    """
    return f"{API_URL}?" + urlencode(
        {
            "series": code,
            "items_per_page": MAX_ITEMS_PER_PAGE,
            "sort_by": "releaseDate",
            "sort_order": "DESC",
            "page": page,
        }
    )


async def _get_listing_page(code: str, page: int) -> dict:
    """Request one page of one series code's listing."""
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request

    response = await amake_request(build_listing_url(code, page))
    if not isinstance(response, dict) or "rows" not in response:
        raise OpenBBError(
            f"Unexpected ERS publications response for series {code} -> {response}"
        )
    return response


async def fetch_series_rows(code: str) -> list[dict]:
    """Fetch every listing row of one series code.

    Parameters
    ----------
    code : str
        A single series code.

    Returns
    -------
    list[dict]
        The series' raw rows, deduplicated by id.
    """
    first = await _get_listing_page(code, 0)
    rows: dict[str, dict] = {row["id"]: row for row in first["rows"]}
    total = int((first.get("pager") or {}).get("total_items") or 0)
    pages = -(-total // MAX_ITEMS_PER_PAGE)
    for page in range(1, pages):
        payload = await _get_listing_page(code, page)
        for row in payload["rows"]:
            rows[row["id"]] = row
    return list(rows.values())


async def fetch_publications(
    series: str | list[str],
    start_date: Any = None,
    end_date: Any = None,
    use_cache: bool = True,
) -> list[dict]:
    """Fetch normalized publication rows for the requested series.

    Parameters
    ----------
    series : str | list[str]
        Group names or series codes, validated before any request is made.
    start_date : Any
        Earliest release date to keep, as a date or YYYY-MM-DD string.
    end_date : Any
        Latest release date to keep, as a date or YYYY-MM-DD string.
    use_cache : bool
        Whether to read and write the listing disk cache.

    Returns
    -------
    list[dict]
        Normalized records, newest release first.
    """
    import asyncio

    codes = resolve_series(series)

    async def one(code: str) -> list[dict]:
        key = f"publications:{code}"
        if use_cache:
            with get_cache() as cache:
                cached = cache.get(key)
            if cached is not None:
                return cached
        rows = await fetch_series_rows(code)
        if use_cache:
            with get_cache() as cache:
                cache.set(key, rows, expire=LISTING_TTL)
        return rows

    fetched = await asyncio.gather(*(one(code) for code in codes))
    records: dict[str, dict] = {}
    for rows in fetched:
        for row in rows:
            record = normalize_row(row)
            records[record["id"]] = record
    results = list(records.values())
    if start_date is not None:
        results = [row for row in results if row["release_date"] >= str(start_date)]
    if end_date is not None:
        results = [row for row in results if row["release_date"] <= str(end_date)]
    results.sort(key=lambda row: (row["release_date"], row["id"]), reverse=True)
    return results


def validate_publication_url(url: str) -> str:
    """Validate that a URL addresses an ERS publication page.

    Parameters
    ----------
    url : str
        The candidate publication page URL.

    Returns
    -------
    str
        The URL, stripped of surrounding whitespace.

    Raises
    ------
    OpenBBError
        If the URL is not an ERS publication page.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    target = url.strip()
    parsed = urlparse(target)
    if parsed.netloc != PUBLICATION_HOST or not parsed.path.startswith(
        PUBLICATION_PATH
    ):
        raise OpenBBError(
            f"Invalid ERS publication URL -> {url}."
            f" Expected a https://{PUBLICATION_HOST}{PUBLICATION_PATH}"
            "{id} page URL."
        )
    return target


def parse_full_report_path(html: str) -> str | None:
    """Find the Full Report PDF path in a publication page's download block.

    Parameters
    ----------
    html : str
        The publication page's HTML.

    Returns
    -------
    str | None
        The '/media/{id}/{name}.pdf' path of the item headed 'Full Report',
        or None when the page offers no such PDF. The block also lists
        summaries, frontmatter, appendices and spreadsheet companions, and a
        'Report Summary' PDF can precede the full report, so the heading is
        matched rather than the first PDF taken.
    """
    block = DOWNLOAD_BLOCK_PATTERN.search(html)
    if block is None:
        return None
    for item in PUBLICATION_ITEM_PATTERN.finditer(block.group(1)):
        text = item.group(0)
        heading = HEADING_PATTERN.search(text)
        if heading is None or heading.group(1).strip().casefold() != (
            FULL_REPORT_HEADING
        ):
            continue
        for path in LINK_PATTERN.findall(text):
            if path.casefold().endswith(".pdf"):
                return path
    return None


async def resolve_full_report(page_url: str, use_cache: bool = True) -> str | None:
    """Resolve a publication page to its Full Report PDF URL.

    Parameters
    ----------
    page_url : str
        An ERS publication page URL.
    use_cache : bool
        Whether to read and write the resolution disk cache.

    Returns
    -------
    str | None
        The full https media URL of the Full Report PDF, or None when the
        page offers no full-report PDF. The listing carries no PDF field and
        the media id is not derivable from the publication id, so the page
        must be parsed.
    """
    from openbb_government_us.usda.utils import ers_client

    target = validate_publication_url(page_url)
    key = f"publication_report:{target}"
    if use_cache:
        with get_cache() as cache:
            cached = cache.get(key, default=_MISSING)
        if cached is not _MISSING:
            return cached
    html = (await ers_client._download(target)).decode("utf-8", errors="replace")
    path = parse_full_report_path(html)
    report_url = f"{BASE_URL}{path}" if path else None
    if use_cache:
        with get_cache() as cache:
            cache.set(key, report_url, expire=REPORT_URL_TTL)
    return report_url


async def afetch_publication(page_url: str) -> tuple[bytes, str]:
    """Fetch a publication's Full Report PDF from its page URL.

    Parameters
    ----------
    page_url : str
        An ERS publication page URL.

    Returns
    -------
    tuple[bytes, str]
        The PDF content and its file name.

    Raises
    ------
    OpenBBError
        If the page offers no Full Report PDF, if the resolved media URL is
        not served by the ERS host, or if the response is not a PDF.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    report_url = await resolve_full_report(page_url)
    if report_url is None:
        raise OpenBBError(f"No Full Report PDF is published for {page_url}.")
    parsed = urlparse(report_url)
    if parsed.netloc != PUBLICATION_HOST:
        raise OpenBBError(
            f"Refusing to download {report_url}, which is not served by"
            f" {PUBLICATION_HOST}."
        )
    content = await afetch_ers_file(parsed.path, ttl=REPORT_FILE_TTL)
    if not content.startswith(b"%PDF"):
        raise OpenBBError(
            f"ERS returned {len(content)} bytes for {report_url} that are not a PDF."
        )
    return content, parsed.path.rsplit("/", 1)[-1]
