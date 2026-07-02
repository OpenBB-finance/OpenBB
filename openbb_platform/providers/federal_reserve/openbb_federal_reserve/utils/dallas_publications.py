"""Dallas Fed publication-archive (PDF) indexing and presentation."""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.dallasfed.org"

_SERIES = {
    "working_papers": {
        "listing": f"{BASE_URL}/research/papers",
        "pattern": (
            r"(/-/media/documents/research/papers/\d{4}/wp\d{4}[a-z0-9]*\.pdf)"
        ),
        "label": "Working Paper",
        "cadence": "monthly",
    },
    "southwest_economy": {
        "listing": f"{BASE_URL}/research/swe/archive",
        "pattern": (r"(/[~-]/media/documents/research/swe/\d{4}/swe\d{4}[a-z]?\.pdf)"),
        "label": "Southwest Economy",
        "cadence": "quarterly",
    },
}

_QUESTIONNAIRES = {
    "manufacturing": (
        f"{BASE_URL}/~/media/documents/research/surveys/tmos/documents/form.pdf"
    ),
    "service_sector": (
        f"{BASE_URL}/-/media/Documents/research/surveys/TSSOS/documents/tssos_form.pdf"
    ),
    "banking": (
        f"{BASE_URL}/~/media/documents/research/surveys/bcs/documents/sample.pdf"
    ),
}

_QUESTIONNAIRE_LABELS = {
    "manufacturing": "Manufacturing Survey Questionnaire",
    "service_sector": "Service Sector Survey Questionnaire",
    "banking": "Banking Conditions Survey Questionnaire",
}

_ENERGY_CHARTS_URL = f"{BASE_URL}/-/media/Documents/research/energy/energycharts.pdf"


def _static_records() -> list[dict[str, Any]]:
    """Return the static questionnaire and energy-charts catalog records."""
    today = dateType.today().isoformat()
    records = [
        {
            "series": "survey_questionnaire",
            "id": f"questionnaire_{survey}",
            "date": today,
            "title": label,
            "url": _QUESTIONNAIRES[survey],
        }
        for survey, label in _QUESTIONNAIRE_LABELS.items()
    ]
    records.append(
        {
            "series": "energy_charts",
            "id": "energy_charts",
            "date": today,
            "title": "Energy Charts",
            "url": _ENERGY_CHARTS_URL,
        }
    )
    return records


def _classify(series: str, href: str) -> dict[str, Any] | None:
    """Classify a publication PDF href into a catalog record."""
    filename = href.rsplit("/", 1)[-1]
    stem = filename[:-4]
    if series == "working_papers":
        match = re.match(r"wp(\d{2})(\d{2})[a-z0-9]*$", stem)
        if match is None:
            return None
        year = 2000 + int(match.group(1))
        pub_date = dateType(year, 1, 1)
        title = f"Working Paper {stem[2:]}"
    else:
        match = re.match(r"swe(\d{2})(\d{2})[a-z]?$", stem)
        if match is None:
            return None
        month = int(match.group(2))
        if not 1 <= month <= 12:
            return None
        year = (
            2000 + int(match.group(1))
            if int(match.group(1)) < 50
            else (1900 + int(match.group(1)))
        )
        pub_date = dateType(year, month, 1)
        title = f"Southwest Economy {pub_date.strftime('%B %Y')}"
    return {
        "series": series,
        "id": stem,
        "date": pub_date.isoformat(),
        "title": title,
        "url": f"{BASE_URL}{href}",
    }


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Dallas Fed publication PDFs, newest first."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    targets = [series] if series else list(_SERIES)

    def _producer() -> list[dict[str, Any]]:
        """Scrape and classify every publication PDF, folding in static PDFs."""
        records: dict[str, dict[str, Any]] = {}
        for name in targets:
            spec = _SERIES[name]
            response = make_request(spec["listing"])
            response.raise_for_status()
            for href in re.findall(spec["pattern"], response.text):
                record = _classify(name, href)
                if record is None:
                    continue
                records[record["id"]] = record
        if series is None:
            for record in _static_records():
                records[record["id"]] = record
        return [
            records[key]
            for key in sorted(
                records, key=lambda k: (records[k]["date"], k), reverse=True
            )
        ]

    return cached(
        ("dallas_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(
    series: str = "working_papers",
    date: str | None = None,
) -> dict[str, Any]:
    """Return a selected Dallas Fed publication PDF as a base64 payload.

    Parameters
    ----------
    series : str
        The publication series, ``"working_papers"`` or ``"southwest_economy"``.
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
        raise OpenBBError(f"No Dallas Fed '{series}' publications are available.")

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next(
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(f"No Dallas Fed '{series}' publication for '{date}'.")

    stem = selected["id"]

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        response = make_request(selected["url"])
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("dallas_publication_pdf", stem),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"Dallas_{stem}.pdf",
        },
    }
