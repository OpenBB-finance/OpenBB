"""Federal Reserve Bank of Philadelphia publication-archive indexing.

The Philadelphia Fed publishes the Survey of Professional Forecasters (SPF), the
Manufacturing and Nonmanufacturing Business Outlook Surveys (MBOS, NBOS), and the
Livingston Survey as per-release PDFs linked from their landing pages. This module
discovers those links, classifies each into a catalog record (series, id, date,
url) by parsing the filename, and serves a selected report as a base64-encoded PDF
for an OpenBB Workspace PDF widget.
"""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

from openbb_federal_reserve.utils.philadelphia import BASE_URL

_MONTH_ABBR = (
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
)

_SERIES = {
    "spf": {
        "listing": (
            f"{BASE_URL}/surveys-and-data/real-time-data-research"
            "/survey-of-professional-forecasters"
        ),
        "pattern": (
            r"/-/media/[Ff][Rr][Bb][Pp]/[Aa]ssets/[Ss]urveys-[Aa]nd-[Dd]ata"
            r"/survey-of-professional-forecasters/\d{4}/spfq\d{3}\.pdf"
        ),
        "label": "Survey of Professional Forecasters",
    },
    "mbos": {
        "listing": (
            f"{BASE_URL}/surveys-and-data/regional-economic-analysis"
            "/manufacturing-business-outlook-survey"
        ),
        "pattern": (
            r"/-/media/[Ff][Rr][Bb][Pp]/[Aa]ssets/[Ss]urveys-[Aa]nd-[Dd]ata"
            r"/[Mm][Bb][Oo][Ss]/\d{4}/bos\d{4}\.pdf"
        ),
        "label": "Manufacturing Business Outlook Survey",
    },
    "nbos": {
        "listing": (
            f"{BASE_URL}/surveys-and-data/regional-economic-analysis"
            "/nonmanufacturing-business-outlook-survey"
        ),
        "pattern": (
            r"/-/media/[Ff][Rr][Bb][Pp]/[Aa]ssets/[Ss]urveys-[Aa]nd-[Dd]ata"
            r"/[Nn][Bb][Oo][Ss]/\d{4}/nbos\d{4}\.pdf"
        ),
        "label": "Nonmanufacturing Business Outlook Survey",
    },
    "livingston": {
        "listing": (
            f"{BASE_URL}/surveys-and-data/real-time-data-research/livingston-survey"
        ),
        "pattern": (
            r"/-/media/[Ff][Rr][Bb][Pp]/[Aa]ssets/[Ss]urveys-[Aa]nd-[Dd]ata"
            r"/[Ll]ivingston-[Ss]urvey/\d{4}/liv[a-z]{3}\d{2}\.pdf"
        ),
        "label": "Livingston Survey",
    },
}


def _pivot_year(two_digit: int) -> int:
    """Map a two-digit year to its century, treating future years as 20th-century."""
    from datetime import date as date_cls

    current = date_cls.today().year % 100
    return 2000 + two_digit if two_digit <= current else 1900 + two_digit


def _classify(series: str, href: str) -> dict[str, Any] | None:
    """Classify a publication PDF href into a catalog record."""
    filename = href.rsplit("/", 1)[-1].lower()
    stem = filename[:-4]
    label = _SERIES[series]["label"]
    if series == "spf":
        match = re.match(r"spfq(\d)(\d{2})$", stem)
        if match is None:
            return None
        quarter, year = int(match.group(1)), _pivot_year(int(match.group(2)))
        if not 1 <= quarter <= 4:
            return None
        pub_date = dateType(year, (quarter - 1) * 3 + 1, 1)
        title = f"{label} {year}:Q{quarter}"
    elif series == "livingston":
        match = re.match(r"liv([a-z]{3})(\d{2})$", stem)
        if match is None or match.group(1) not in _MONTH_ABBR:
            return None
        month = _MONTH_ABBR.index(match.group(1)) + 1
        year = _pivot_year(int(match.group(2)))
        pub_date = dateType(year, month, 1)
        title = f"{label} {pub_date.strftime('%B %Y')}"
    else:
        prefix = "bos" if series == "mbos" else "nbos"
        match = re.match(rf"{prefix}(\d{{2}})(\d{{2}})$", stem)
        if match is None:
            return None
        month, year = int(match.group(1)), _pivot_year(int(match.group(2)))
        if not 1 <= month <= 12:
            return None
        pub_date = dateType(year, month, 1)
        title = f"{label} {pub_date.strftime('%B %Y')}"
    return {
        "series": series,
        "id": f"{series}_{stem}",
        "date": pub_date.isoformat(),
        "title": title,
        "url": f"{BASE_URL}{href}",
    }


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Philadelphia Fed publication PDFs, newest first.

    Parameters
    ----------
    series : str | None
        One of ``"spf"``, ``"mbos"``, ``"nbos"``, or ``"livingston"``; ``None``
        returns all four merged.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records, newest first.
    """
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    targets = [series] if series else list(_SERIES)

    def _producer() -> list[dict[str, Any]]:
        """Scrape and classify every publication PDF for the target series."""
        records: dict[str, dict[str, Any]] = {}
        for name in targets:
            spec = _SERIES[name]
            response = make_request(spec["listing"])
            response.raise_for_status()
            for href in re.findall(spec["pattern"], response.text):
                record = _classify(name, href)
                if record is not None:
                    records[record["id"]] = record
        return [
            records[key]
            for key in sorted(
                records, key=lambda key: (records[key]["date"], key), reverse=True
            )
        ]

    return cached(
        ("philadelphia_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(
    series: str = "spf",
    date: str | None = None,
) -> dict[str, Any]:
    """Return a selected Philadelphia Fed publication PDF as a base64 payload.

    Parameters
    ----------
    series : str
        One of ``"spf"``, ``"mbos"``, ``"nbos"``, or ``"livingston"``.
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
        raise OpenBBError(f"No Philadelphia Fed '{series}' publications are available.")

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next(
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(
                f"No Philadelphia Fed '{series}' publication for '{date}'."
            )

    stem = selected["id"]

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        response = make_request(selected["url"], timeout=60)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("philadelphia_publication_pdf", stem),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"Philadelphia_{stem}.pdf",
        },
    }
