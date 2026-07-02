"""Kansas City Fed Agricultural Bulletin PDF indexing and presentation."""

from __future__ import annotations

import re
from typing import Any

from openbb_federal_reserve.utils.kansas_city import SITE_HOST, fetch_kansas_city

LISTING_URL = (
    f"{SITE_HOST}/center-for-agriculture-and-the-economy/"
    "agricultural-data-and-indicators/"
)
_PDF_PATTERN = r"/(?:Agriculture/)?documents/\d+/[^\"']+\.pdf"
_WORDED_QUARTERS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
}


def _parse_quarter_year(filename: str) -> tuple[int, int] | None:
    """Resolve a (year, quarter) from an Ag Bulletin filename, or ``None``."""
    low = filename.lower()
    year_quarter = re.search(r"(20\d{2})[^a-z0-9]?q([1-4])", low)
    if year_quarter:
        return int(year_quarter.group(1)), int(year_quarter.group(2))
    quarter_year = re.search(r"q([1-4])[^a-z0-9]?(20\d{2})", low)
    if quarter_year:
        return int(quarter_year.group(2)), int(quarter_year.group(1))
    worded = re.search(r"(first|second|third|fourth)quarter(20\d{2})", low)
    if worded:
        return int(worded.group(2)), _WORDED_QUARTERS[worded.group(1)]
    short_year = re.search(r"q([1-4])(\d{2})(?:\D|$)", low)
    if short_year:
        return 2000 + int(short_year.group(2)), int(short_year.group(1))
    return None


def list_ag_bulletins() -> list[dict[str, Any]]:
    """Return the catalog of Agricultural Bulletin PDFs, newest first."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Scrape the listing page and classify each bulletin PDF link."""
        html = fetch_kansas_city(LISTING_URL).decode("utf-8", "ignore")
        records: dict[tuple[int, int], dict[str, Any]] = {}
        for href in sorted(set(re.findall(_PDF_PATTERN, html))):
            filename = href.rsplit("/", 1)[-1]
            parsed = _parse_quarter_year(filename)
            if parsed is None:
                continue
            year, quarter = parsed
            records[(year, quarter)] = {
                "date": f"{year}-{quarter * 3 - 2:02d}-01",
                "year": year,
                "quarter": quarter,
                "title": f"Agricultural Bulletin Q{quarter} {year}",
                "url": f"{SITE_HOST}{href}",
            }
        return [records[key] for key in sorted(records, reverse=True)]

    return cached(
        "kansas_city_ag_bulletins",
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def fetch_ag_bulletin_pdf(date: str | None = None) -> dict[str, Any]:
    """Return a selected Agricultural Bulletin as a base64-encoded PDF payload.

    Parameters
    ----------
    date : str | None
        The bulletin quarter as ``YYYY-MM``; defaults to the most recent release.

    Returns
    -------
    dict[str, Any]
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    catalog = list_ag_bulletins()
    if not catalog:
        raise OpenBBError("No Agricultural Bulletin reports are available.")

    selected = catalog[0]
    if date:
        target = date[:7]
        selected = next(  # type: ignore[assignment]
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(f"No Agricultural Bulletin for '{date}'.")

    content = cached(
        ("kansas_city_ag_bulletin_pdf", selected["date"]),
        lambda: seconds_until_next_release("quarterly"),
        lambda: base64.b64encode(fetch_kansas_city(selected["url"])).decode("utf-8"),
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"KC_AgBulletin_{selected['date']}.pdf",
        },
    }
