"""Atlanta Fed publication-archive indexing and PDF presentation."""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.atlantafed.org"
GDPNOW_SLIDES_URL = (
    f"{BASE_URL}/-/media/Project/Atlanta/FRBA/Documents"
    "/cqer/researchcq/gdpnow/RealGDPTrackingSlides.pdf"
)

_BIE_LISTING = f"{BASE_URL}/research-and-data/surveys/business-inflation-expectations"
_BIE_PATTERN = (
    r"/-/media/Project/Atlanta/FRBA/Documents/research/inflationproject/bie"
    r"/(\d{4})/(\d{2})/([^\"']+chart-pack\.pdf)"
)
_SBU_LISTING = f"{BASE_URL}/research-and-data/surveys/business-uncertainty"
_SBU_PATTERN = (
    r"/-/media/Project/Atlanta/FRBA/Documents/datafiles/research/surveys"
    r"/business-uncertainty/monthly-report/(\d{4})/(\d{4})-(\d{2})\.pdf"
)
_WORKING_PAPERS_PAGE_SIZE = 50
_WORKING_PAPERS_API = (
    f"{BASE_URL}/api/feed/getFilteredResults"
    "?DataSourceId=34e83453b5ee407cb4fdd56c6fb51bce"
    "&ContextId=4bf680469cff43b29350606fdd631ece"
    f"&PageSize={_WORKING_PAPERS_PAGE_SIZE}"
    "&PageNumber={page}"
)
_WORKING_PAPER_PDF_PATTERN = r"(/-/media/[^\"']+/working-paper/[^\"']+\.pdf)"

_SERIES_LABELS = {
    "bie_chart_pack": "BIE Monthly Chart Pack",
    "sbu_monthly_report": "SBU Monthly Report",
    "working_paper": "Working Paper",
}


def _index_listing(series: str) -> list[dict[str, Any]]:
    """Scrape a listing page and classify its monthly-PDF links."""
    from openbb_core.provider.utils.helpers import make_request

    listing, pattern, label = (
        (_BIE_LISTING, _BIE_PATTERN, _SERIES_LABELS["bie_chart_pack"])
        if series == "bie_chart_pack"
        else (_SBU_LISTING, _SBU_PATTERN, _SERIES_LABELS["sbu_monthly_report"])
    )
    response = make_request(listing)
    response.raise_for_status()
    records: dict[str, dict[str, Any]] = {}
    for match in re.findall(pattern, response.text):
        if series == "bie_chart_pack":
            year, month, filename = match
            href = (
                "/-/media/Project/Atlanta/FRBA/Documents/research"
                f"/inflationproject/bie/{year}/{month}/{filename}"
            )
        else:
            year, _, month = match
            href = (
                "/-/media/Project/Atlanta/FRBA/Documents/datafiles/research"
                f"/surveys/business-uncertainty/monthly-report/{year}/{year}-{month}.pdf"
            )
        pub_date = dateType(int(year), int(month), 1)
        identifier = f"{series}_{year}-{month}"
        records[identifier] = {
            "series": series,
            "id": identifier,
            "date": pub_date.isoformat(),
            "title": f"{label} {pub_date.strftime('%B %Y')}",
            "url": f"{BASE_URL}{href}",
        }
    return [records[key] for key in sorted(records, reverse=True)]


def _resolve_working_paper_pdf(landing_url: str) -> str | None:
    """Resolve a Working Paper landing page to its direct PDF URL, cached per paper.

    Parameters
    ----------
    landing_url : str
        The absolute Working Paper landing-page URL.

    Returns
    -------
    str | None
        The direct PDF URL, or ``None`` when the landing page exposes no PDF.
    """
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> str:
        """Scrape the landing page for its working-paper PDF link."""
        page = make_request(landing_url)
        page.raise_for_status()
        match = re.search(_WORKING_PAPER_PDF_PATTERN, page.text)
        return f"{BASE_URL}{match.group(1)}" if match else ""

    resolved = cached(
        ("atlanta_working_paper_pdf_url", landing_url),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return resolved or None


def _index_working_papers() -> list[dict[str, Any]]:
    """Page the Working Papers JSON feed and resolve each item's direct PDF URL."""
    import json

    from openbb_core.provider.utils.helpers import make_request

    records: dict[str, dict[str, Any]] = {}
    page = 1
    while page <= 50:
        response = make_request(_WORKING_PAPERS_API.format(page=page))
        response.raise_for_status()
        if "json" not in (response.headers.get("Content-Type") or ""):
            break
        payload = response.json()
        raw = payload.get("FilteredFeedItemsJson")
        items = json.loads(raw) if isinstance(raw, str) else (raw or [])
        if not items:
            break
        for item in items:
            url = item.get("Url") or item.get("UrlNoLang") or ""
            if not url:
                continue
            identifier = url.rstrip("/").rsplit("/", 1)[-1]
            landing_url = url if url.startswith("http") else f"{BASE_URL}{url}"
            pdf_url = _resolve_working_paper_pdf(landing_url)
            if not pdf_url:
                continue
            authors = ", ".join(
                re.sub(r"\s+", " ", a.get("FullName", "")).strip()
                for a in item.get("Authors", [])
                if a.get("FullName")
            )
            records[identifier] = {
                "series": "working_paper",
                "id": identifier,
                "date": (item.get("Date") or "")[:10],
                "title": re.sub(r"\s+", " ", item.get("Title", "")).strip(),
                "url": pdf_url,
                "authors": authors or None,
            }
        if len(items) < _WORKING_PAPERS_PAGE_SIZE:
            break
        page += 1
    return [
        records[key]
        for key in sorted(records, key=lambda k: records[k]["date"], reverse=True)
    ]


def _gdpnow_slides_record() -> dict[str, Any]:
    """Return the GDPNow slide-deck catalog record, dated today so it sorts first."""
    return {
        "series": "gdpnow_slides",
        "id": "gdpnow_slides",
        "date": dateType.today().isoformat(),
        "title": "GDPNow Real GDP Tracking Slides",
        "url": GDPNOW_SLIDES_URL,
    }


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Atlanta Fed publication PDFs, newest first.

    Parameters
    ----------
    series : str | None
        One of ``"bie_chart_pack"``, ``"sbu_monthly_report"``,
        ``"working_paper"``, or ``"gdpnow_slides"``; ``None`` returns all merged.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records, newest first.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    targets = [series] if series else [*_SERIES_LABELS, "gdpnow_slides"]

    def _producer() -> list[dict[str, Any]]:
        """Index every target series and merge, newest first."""
        records: list[dict[str, Any]] = []
        for name in targets:
            if name == "working_paper":
                records.extend(_index_working_papers())
            elif name == "gdpnow_slides":
                records.append(_gdpnow_slides_record())
            else:
                records.extend(_index_listing(name))
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("atlanta_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(
    series: str = "bie_chart_pack",
    date: str | None = None,
) -> dict[str, Any]:
    """Return a selected Atlanta Fed publication PDF as a base64 payload.

    Parameters
    ----------
    series : str
        One of ``"bie_chart_pack"``, ``"sbu_monthly_report"``, or
        ``"working_paper"``.
    date : str | None
        The publication month as ``YYYY-MM``; defaults to the most recent release.

    Returns
    -------
    dict[str, Any]
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    catalog = list_publications(series)
    if not catalog:
        raise OpenBBError(f"No Atlanta Fed '{series}' publications are available.")

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next(
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(f"No Atlanta Fed '{series}' publication for '{date}'.")

    period = selected["date"][:7]
    url = selected["url"]

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        response = make_request(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("atlanta_publication_pdf", series, period),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"Atlanta_{series}_{period}.pdf",
        },
    }
