"""Federal Reserve Bank of St. Louis data client.

The St. Louis Fed data hosts vary in their bot protection. ``www.stlouisfed.org``
sits behind Akamai bot management and ``fred.stlouisfed.org`` rejects ordinary
HTTP clients on a TLS-fingerprint basis; both require a browser-impersonating
``curl_cffi`` session warmed against the host home page (the same technique used
for the FFIEC NIC client). ``fraser.stlouisfed.org`` serves its archive PDFs only
after the session is warmed as well. A single warmed session therefore backs
every St. Louis download, and payloads are disk-cached at each dataset's release
cadence.
"""

from __future__ import annotations

import html
import re
from typing import Any

from openbb_federal_reserve.utils.curl_session import (
    get_session,
    reset_session as _reset,
)

FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
FRED_MD_URL = (
    "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research"
    "/fred-md/monthly/current.csv"
)
FRED_QD_URL = (
    "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research"
    "/fred-md/quarterly/current.csv"
)
FRASER_BASE = "https://fraser.stlouisfed.org"
FRASER_SYNOPSES_TITLE = f"{FRASER_BASE}/title/economic-synopses-6715"

_WARMUP_HOSTS = (
    "https://www.stlouisfed.org/",
    "https://fred.stlouisfed.org/",
    "https://fraser.stlouisfed.org/",
)


def _warmup(session: Any) -> None:
    """Prime the session against every St. Louis Fed host."""
    for host in _WARMUP_HOSTS:
        session.get(host, timeout=60)


def _get_session() -> Any:
    """Return a ``curl_cffi`` session warmed against the St. Louis Fed hosts."""
    return get_session("st_louis", _warmup)


def reset_session() -> None:
    """Drop the cached session so the next call re-warms it."""
    _reset("st_louis")


def fetch_text(url: str, referer: str | None = None) -> str:
    """Fetch a St. Louis Fed URL as text, re-warming the session once on a 403.

    Parameters
    ----------
    url : str
        The absolute URL to fetch.
    referer : str | None
        An optional ``Referer`` header value.

    Returns
    -------
    str
        The decoded response body.
    """
    headers = {"Referer": referer} if referer else {}
    session = _get_session()
    response = session.get(url, headers=headers, timeout=180)
    if response.status_code == 403:
        reset_session()
        response = _get_session().get(url, headers=headers, timeout=180)
    response.raise_for_status()
    return response.text


def fetch_bytes(url: str, referer: str | None = None) -> bytes:
    """Fetch a St. Louis Fed URL as bytes, re-warming the session once on a 403.

    Parameters
    ----------
    url : str
        The absolute URL to fetch.
    referer : str | None
        An optional ``Referer`` header value.

    Returns
    -------
    bytes
        The raw response body.
    """
    headers = {"Referer": referer} if referer else {}
    session = _get_session()
    response = session.get(url, headers=headers, timeout=180)
    if response.status_code == 403:
        reset_session()
        response = _get_session().get(url, headers=headers, timeout=180)
    response.raise_for_status()
    return response.content


def fetch_fred_graph_csv(series_id: str) -> str:
    """Download a ``fredgraph.csv`` two-column series, cached weekly.

    Parameters
    ----------
    series_id : str
        The FRED series identifier (for example ``STLFSI4``).

    Returns
    -------
    str
        The raw two-column ``observation_date,<series_id>`` CSV text.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    return cached(
        ("st_louis_fredgraph", series_id),
        lambda: seconds_until_next_release("weekly"),
        lambda: fetch_text(FRED_GRAPH_URL.format(series_id=series_id)),
    )


def fetch_fred_panel(frequency: str) -> str:
    """Download the FRED-MD or FRED-QD wide panel CSV, cached monthly.

    Parameters
    ----------
    frequency : str
        One of ``"monthly"`` (FRED-MD) or ``"quarterly"`` (FRED-QD).

    Returns
    -------
    str
        The raw panel CSV text including its header and transform/factor rows.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if frequency not in ("monthly", "quarterly"):
        raise ValueError("frequency must be 'monthly' or 'quarterly'.")
    url = FRED_MD_URL if frequency == "monthly" else FRED_QD_URL
    return cached(
        ("st_louis_fred_panel", frequency),
        lambda: seconds_until_next_release("monthly"),
        lambda: fetch_text(url),
    )


_SYNOPSES_DECADES = ("2000s", "2010s", "2020s")
_ITEM_PATTERN = re.compile(
    r'data-id="(\d+)"\s+data-type="item"\s+'
    r'href="(/title/economic-synopses-6715/[^"]+)"[^>]*>\s*'
    r'<span class="list-item-title">(.*?)(?:</span>|</a>)',
    re.DOTALL,
)
_TITLE_TAIL_PATTERN = re.compile(r",\s*(\d{4}),\s*No\.\s*(\d+)\s*$")
_PDF_META_PATTERN = re.compile(r'citation_pdf_url"\s*content="([^"]+)"')
_PDF_DATE_PATTERN = re.compile(r"economicsynopses_stls_(\d{8})\.pdf")


def _parse_synopsis_item(item_id: str, href: str, raw_title: str) -> dict[str, Any]:
    """Build a catalog record from a FRASER browse-list article entry."""
    title = html.unescape(re.sub(r"\s+", " ", raw_title).strip())
    year: int | None = None
    issue: int | None = None
    match = _TITLE_TAIL_PATTERN.search(title)
    if match:
        year, issue = int(match.group(1)), int(match.group(2))
        title = title[: match.start()].strip()
    return {
        "item_id": item_id,
        "title": title,
        "year": year,
        "issue": issue,
        "url": f"{FRASER_BASE}{href}",
    }


def list_economic_synopses() -> list[dict[str, Any]]:
    """Return the FRASER catalog of Economic Synopses articles, newest first.

    Returns
    -------
    list[dict[str, Any]]
        One record per article with ``item_id``, ``title``, ``year``, ``issue``,
        ``date``, the FRASER landing-page ``url``, and the direct ``pdf_url``. The
        ``date`` is the ``YYYY-MM-DD`` publication date resolved from the article's
        PDF filename, or ``""`` when no dated PDF is published; ``pdf_url`` is the
        direct article PDF link, or ``""`` when none is published.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Scrape each decade browse page and resolve every article's PDF and date."""
        records: dict[str, dict[str, Any]] = {}
        for decade in _SYNOPSES_DECADES:
            text = fetch_text(f"{FRASER_SYNOPSES_TITLE}?browse={decade}")
            for item_id, href, raw_title in _ITEM_PATTERN.findall(text):
                record = _parse_synopsis_item(item_id, href, raw_title)
                records[item_id] = record
        for record in records.values():
            try:
                resolved = resolve_synopsis_pdf_url(record["url"])
                record["date"] = resolved["date"]
                record["pdf_url"] = resolved["url"]
            except Exception:  # noqa: BLE001, S110
                record["date"] = ""
                record["pdf_url"] = ""
        return sorted(
            records.values(),
            key=lambda r: (r["date"], r["year"] or 0, r["issue"] or 0, r["item_id"]),
            reverse=True,
        )

    return cached(
        "st_louis_economic_synopses",
        lambda: seconds_until_next_release("weekly"),
        _producer,
    )


def list_publications() -> list[dict[str, Any]]:
    """Return the catalog of St. Louis Fed publication PDFs, newest first.

    Every St. Louis Fed PDF published to FRASER is folded into one catalog: each
    Economic Synopses issue carrying a direct article PDF link is exposed as a
    publication record for the multi-file viewer.

    Returns
    -------
    list[dict[str, Any]]
        One record per PDF with ``series``, ``id``, ``date``, ``title``, and the
        direct ``url`` to the publication PDF, newest first.
    """
    records: list[dict[str, Any]] = []
    for article in list_economic_synopses():
        pdf_url = article.get("pdf_url") or ""
        if not pdf_url:
            continue
        records.append(
            {
                "series": "economic_synopses",
                "id": article["item_id"],
                "date": article["date"] or None,
                "title": article["title"],
                "url": pdf_url,
            }
        )
    return records


def resolve_synopsis_pdf_url(landing_url: str) -> dict[str, str]:
    """Resolve an Economic Synopses landing page to its direct PDF URL and date.

    Parameters
    ----------
    landing_url : str
        The FRASER article landing-page URL.

    Returns
    -------
    dict[str, str]
        ``url`` is the direct PDF link and ``date`` is the ``YYYY-MM-DD``
        publication date parsed from the PDF filename when present.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    text = fetch_text(landing_url)
    match = _PDF_META_PATTERN.search(text)
    if not match:
        raise OpenBBError(f"No PDF is published for '{landing_url}'.")
    pdf_url = html.unescape(match.group(1))
    date_match = _PDF_DATE_PATTERN.search(pdf_url)
    published = ""
    if date_match:
        stamp = date_match.group(1)
        published = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
    return {"url": pdf_url, "date": published}
