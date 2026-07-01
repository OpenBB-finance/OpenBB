"""New York Fed Survey of Market Expectations PDF indexing and presentation.

The Survey of Market Expectations (formerly the separate Survey of Primary
Dealers and Survey of Market Participants) is published only as per-FOMC-meeting
PDFs - a results report and a blank questionnaire. The landing page links the
full archive back to 2011; this module indexes those links and serves a selected
report as a base64-encoded PDF for an OpenBB Workspace PDF widget.
"""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.newyorkfed.org"
SME_URL = f"{BASE_URL}/markets/market-intelligence/survey-of-market-expectations"

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
    **{
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
    },
    "sept": 9,
}
_SUBTYPE_LABELS = {
    "primary_dealers": "Primary Dealers",
    "market_participants": "Market Participants",
    "combined": "Combined",
}


def _month_from_filename(low: str) -> int | None:
    """Resolve a month number from a survey filename, full or abbreviated."""
    for name, num in _FULL_MONTHS.items():
        if name in low:
            return num
    for abbr, num in sorted(_ABBR_MONTHS.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"(^|[^a-z]){abbr}([^a-z]|$)", low):
            return num
    return None


def _classify(year: str, filename: str) -> dict[str, Any] | None:
    """Classify a survey PDF filename into a catalog record."""
    low = filename.lower()
    month = _month_from_filename(low)
    if month is None:
        return None
    survey_date = dateType(int(year), month, 1)
    if "result" in low:
        kind = "results"
    elif "survey" in low:
        kind = "questionnaire"
    else:
        kind = "results"
    if re.search(r"(^|[^a-z])pd([^a-z]|$)", low):
        subtype = "primary_dealers"
    elif re.search(r"(^|[^a-z])mp([^a-z]|$)", low):
        subtype = "market_participants"
    else:
        subtype = "combined"
    title = (
        f"{_MONTH_NAMES[month - 1]} {year} {kind.capitalize()} "
        f"({_SUBTYPE_LABELS[subtype]})"
    )
    return {
        "date": survey_date.isoformat(),
        "kind": kind,
        "subtype": subtype,
        "title": title,
    }


def list_market_expectations() -> list[dict[str, Any]]:
    """Return the catalog of Survey of Market Expectations PDFs, newest first."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Scrape and classify every survey PDF on the landing page."""
        response = make_request(SME_URL)
        response.raise_for_status()
        pattern = r"/medialibrary/media/markets/survey/(\d{4})/([^\"']+?)\.pdf"
        records: dict[tuple, dict[str, Any]] = {}
        for year, filename in re.findall(pattern, response.text):
            record = _classify(year, filename)
            if record is None:
                continue
            record["url"] = (
                f"{BASE_URL}/medialibrary/media/markets/survey/{year}/{filename}.pdf"
            )
            records[(record["date"], record["kind"], record["subtype"])] = record
        return [records[key] for key in sorted(records, reverse=True)]

    return cached(
        "ny_market_expectations",
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_market_expectations_pdf(
    date: str | None = None, kind: str = "results"
) -> dict[str, Any]:
    """Return a selected Survey of Market Expectations PDF as a base64 payload."""
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    catalog = [
        record for record in list_market_expectations() if record["kind"] == kind
    ]
    if not catalog:
        raise OpenBBError(
            f"No Survey of Market Expectations '{kind}' reports are available."
        )

    selected = catalog[0]
    if date:
        target = date[:7]
        selected = next(  # type: ignore[assignment]
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(
                f"No Survey of Market Expectations '{kind}' report for '{date}'."
            )

    def _producer() -> str:
        """Download and base64-encode the selected report PDF."""
        response = make_request(selected["url"])
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        (
            "ny_market_expectations_pdf",
            selected["date"],
            selected["kind"],
            selected["subtype"],
        ),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"NY_SME_{selected['date']}_{selected['kind']}.pdf",
        },
    }
