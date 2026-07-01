"""Minneapolis Fed research-archive indexing and PDF presentation.

The Minneapolis Fed publishes its Working Papers, Institute Working Papers, CICD
Working Papers, Staff Reports, and Quarterly Review on a Sitecore/Next.js site
whose series listings are rendered client-side. The research hub page, however,
links every recent item across these series to a server-rendered landing page
that carries the direct PDF link, the publication date, the title, and the
author block. This module discovers those landing pages, resolves each to its
real PDF, and classifies them into catalog records served as base64-encoded PDFs
in the multi-file viewer.
"""

from __future__ import annotations

import re
from typing import Any

BASE_URL = "https://www.minneapolisfed.org"
_RESEARCH_HUB = f"{BASE_URL}/research"

_SERIES_FOLDERS = {
    "working-papers": "working_paper",
    "institute-working-papers": "institute_working_paper",
    "cicd-working-paper-series": "cicd_working_paper",
    "staff-reports": "staff_report",
    "quarterly-review": "quarterly_review",
}

_LANDING_PATTERN = (
    r"href=[\"'](/research/(?:" + "|".join(_SERIES_FOLDERS) + r")/[a-z0-9-]+)[\"']"
)
_PDF_PATTERN = r"(?:href|content)=[\"']((?:https?://[^\"' ]+|/[^\"' ]+)\.pdf)"
_DATE_PATTERN = r"name=\"sortDate\" content=\"([^\"]+)\""
_TITLE_PATTERN = r"name=\"title\" content=\"([^\"|]+)"
_AUTHOR_PATTERN = r"alt=\"photo of ([^\"]+)\""


def _index_research_hub() -> list[str]:
    """Return the deduplicated research landing-page paths linked from the hub."""
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(_RESEARCH_HUB)
    response.raise_for_status()
    return sorted(set(re.findall(_LANDING_PATTERN, response.text)))


def _resolve_landing(path: str) -> dict[str, Any] | None:
    """Resolve a research landing page to a catalog record, cached per landing.

    Parameters
    ----------
    path : str
        The site-relative landing-page path, e.g. ``/research/working-papers/x``.

    Returns
    -------
    dict[str, Any] | None
        The catalog record, or ``None`` when the landing page exposes no PDF. The
        resolution is disk-cached per landing page so it is not re-scraped on
        every catalog build.
    """
    import html

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    folder = path.split("/")[2]
    series = _SERIES_FOLDERS[folder]
    identifier = path.rstrip("/").rsplit("/", 1)[-1]

    def _producer() -> dict[str, Any]:
        """Scrape the landing page for its PDF, date, title, and authors."""
        page = make_request(f"{BASE_URL}{path}")
        page.raise_for_status()
        pdf_match = re.search(_PDF_PATTERN, page.text)
        if not pdf_match:
            return {}
        url = pdf_match.group(1)
        url = url if url.startswith("http") else f"{BASE_URL}{url}"
        date_match = re.search(_DATE_PATTERN, page.text)
        title_match = re.search(_TITLE_PATTERN, page.text)
        seen: set[str] = set()
        names: list[str] = []
        for name in re.findall(_AUTHOR_PATTERN, page.text):
            cleaned = html.unescape(name).strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                names.append(cleaned)
        title = (
            html.unescape(title_match.group(1)).strip()
            if title_match
            else identifier.replace("-", " ").title()
        )
        return {
            "series": series,
            "id": identifier,
            "date": date_match.group(1)[:10] if date_match else "",
            "title": title,
            "url": url,
            "authors": ", ".join(names) or None,
        }

    record = cached(
        ("minneapolis_publication_landing", path),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return record or None


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Minneapolis Fed research PDFs, newest first.

    Parameters
    ----------
    series : str | None
        One of ``"working_paper"``, ``"institute_working_paper"``,
        ``"cicd_working_paper"``, ``"staff_report"``, or ``"quarterly_review"``;
        ``None`` returns every series merged.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records, newest first.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Index every research landing page and merge, newest first."""
        records: list[dict[str, Any]] = []
        for path in _index_research_hub():
            record = _resolve_landing(path)
            if record and (series is None or record["series"] == series):
                records.append(record)
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("minneapolis_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(url: str) -> dict[str, Any]:
    """Return a selected Minneapolis Fed publication PDF as a base64 payload.

    Parameters
    ----------
    url : str
        The direct PDF URL, as carried by a catalog record.

    Returns
    -------
    dict[str, Any]
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        response = make_request(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("minneapolis_publication_pdf", url),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": url.rsplit("/", maxsplit=1)[-1],
        },
    }
