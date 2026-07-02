"""New York Fed Empire State Manufacturing Survey full-report (PDF) helpers."""

from __future__ import annotations

import re
from typing import Any

BASE_URL = "https://www.newyorkfed.org"
ARCHIVES_URL = f"{BASE_URL}/survey/empire/empiresurvey_archives"

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_FULL_MONTHS = {name.lower(): index for index, name in enumerate(_MONTH_NAMES, 1)}
_ABBR_MONTHS = {
    abbr: index
    for index, abbr in enumerate(
        [
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
        ],
        1,
    )
}


def _classify(filename: str) -> str | None:
    """Resolve a ``YYYYMM`` period from an Empire archive PDF filename."""
    low = filename.lower()
    numeric = re.search(r"(\d{4})[_-]?(\d{1,2})", low)
    if numeric:
        year, month = int(numeric.group(1)), int(numeric.group(2))
        if 2000 <= year <= 2100 and 1 <= month <= 12:
            return f"{year:04d}{month:02d}"
    word = re.search(r"([a-z]+)\D*(\d{4})", low)
    if word:
        name, year = word.group(1), int(word.group(2))
        month = _FULL_MONTHS.get(name) or _ABBR_MONTHS.get(name[:3])
        if month and 2000 <= year <= 2100:
            return f"{year:04d}{month:02d}"
    return None


def list_empire_state_reports() -> list[dict[str, str]]:
    """Return available Empire State Survey reports as period/url records."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Scrape the archives page and classify each report PDF link."""
        response = make_request(ARCHIVES_URL)
        response.raise_for_status()
        pattern = r"(/medialibrary/media/[Ss]urvey/[Ee]mpire/[^\"']*?\.pdf[^\"']*)"
        reports: dict[str, str] = {}
        for href in re.findall(pattern, response.text):
            clean = href.replace("&amp;", "&")
            filename = clean.split("?")[0].rsplit("/", 1)[-1]
            period = _classify(filename)
            if period and period not in reports:
                reports[period] = f"{BASE_URL}{clean}"
        return [
            {"period": period, "url": url}
            for period, url in sorted(reports.items(), reverse=True)
        ]

    return cached(
        "ny_empire_reports",
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_empire_state_report(period: str | None = None) -> dict[str, Any]:
    """Return an Empire State Survey report as a base64-encoded PDF payload."""
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    reports = list_empire_state_reports()
    if not reports:
        raise OpenBBError("No Empire State Survey reports are available.")

    selected = reports[0]
    if period:
        selected = next((r for r in reports if r["period"] == period), None)  # type: ignore[assignment]
        if not selected:
            raise OpenBBError(f"No Empire State Survey report for period '{period}'.")

    def _producer() -> str:
        """Download and base64-encode the selected report PDF."""
        response = make_request(selected["url"])
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("ny_empire_report", selected["period"]),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"NY_ESMS_{selected['period']}.pdf",
        },
    }
